
from typing import Dict, Any, Union, Tuple, Optional
from fastapi import HTTPException, status
from app.chatbot.core.graph import ChatBotGraph
from app.schemas.chatbot import UserMessage
from app.core.app_helper import get_app
from langgraph.types import Command
from contextlib import asynccontextmanager
import logging
logger = logging.getLogger(__name__)

class ChatbotError(Exception):
    """Base exception for chatbot-related errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

def format_chat_input(message: str, manager: str, managerId: str) -> Dict[str, Any]:
    """Format the user message into the expected graph input structure"""
    return {
        "messages": [("user", message)],
        "manager": manager,
    }

def format_config(thread_id: str, residentAppUserId: str, siteId: str) -> Dict[str, Any]:
    """Format the configuration dictionary for graph processing"""
    return {
        "configurable": {
            "thread_id": thread_id,
            "residentAppUserId": residentAppUserId,
            "siteId": siteId
        }
    }

async def get_graph() -> ChatBotGraph:
    """Retrieve and validate the graph from application state"""
    app = get_app()
    logger.info("Accessing app state graph")
    
    graph = getattr(app.state, "graph", None)
    if not graph:
        raise ChatbotError(
            "Chatbot service not initialized", 
            "GRAPH_NOT_INITIALIZED"
        )
    
    return graph

def extract_response_content(result: Dict[str, Any]) -> str:
    """Extract the response content from the graph result"""
    try:
        return result['messages'][-1].content
    except (KeyError, IndexError) as e:
        raise ChatbotError(
            "Invalid response structure from chatbot",
            "INVALID_RESPONSE"
        )

async def check_next_steps(graph: ChatBotGraph, config: Dict[str, Any]) -> Optional[str]:
    """Check if there are pending next steps in the graph state"""
    try:
        snapshot = await graph.aget_state(config)
        logger.info(f"State snapshot: {snapshot}")
        
        # https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/#using-with-invoke-and-ainvoke
        if hasattr(snapshot, 'tasks') and snapshot.tasks:
            logger.info(f"Next step required: {snapshot.values}")
            logger.info(f"Next step required: {snapshot.tasks}")
            # Access the first task in the tuple
            first_task = snapshot.tasks[0]

            # Access the interrupts from the task
            interrupts = first_task.interrupts

            # Since interrupts is a tuple, access the first Interrupt object
            first_interrupt = interrupts[0]

            # Extract the value of the Interrupt
            interrupt_value = first_interrupt.value

            # Print the result
            print("interrupt_value", interrupt_value)
            return interrupt_value
        return None
        
    except Exception as e:
        logger.error(f"Error checking graph state: {e}")
        raise ChatbotError(
            "Failed to check graph state",
            "STATE_CHECK_FAILED"
        )

def handle_error(e: Exception) -> str:
    """Convert various exceptions into appropriate error messages"""
    error_messages = {
        KeyError: "Invalid response structure.",
        ConnectionError: "Graph connection error.",
        AttributeError: "Unexpected response format from graph.",
        ChatbotError: lambda err: err.message
    }
    
    error_type = type(e)
    if error_type in error_messages:
        message = error_messages[error_type]
        if callable(message):
            return message(e)
        return message
    
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return "An unexpected error occurred."

async def process_chat(user_message: UserMessage) -> str:
    """
    Process a user message through the chatbot's graph and return the assistant's response.

    Args:
        user_message (UserMessage): The user's input message.
    """
    try:
        # Initialize and validate graph
        graph = await get_graph()
        
        # Prepare input data and config
        input_data = format_chat_input(user_message.msg, user_message.manager, user_message.residentAppUserId)
        thread_config = format_config(user_message.threadId, user_message.residentAppUserId, user_message.siteId)
        
        logger.debug(f"Processing message with Thread ID: {user_message.threadId}")
        
        # Process message through graph
        if(user_message.status == "approval"):
            msg = user_message.msgFeedback
            result = await graph.ainvoke(Command(resume={"action": "approval", "data": msg}), config=thread_config)
            logger.debug(f"Raw graph response: {result}")
        elif (user_message.status == "reject"):
            result = await graph.ainvoke(Command(resume={"action": "reject", "data": "None"}), config=thread_config)
            logger.debug(f"Raw graph response: {result}")    
        elif (user_message.status == "feedback"):
            msg = user_message.msgFeedback
            result = await graph.ainvoke(Command(resume={"action": "feedback", "data": msg}), config=thread_config)
            logger.debug(f"Raw graph response: {result}")
        else:
            logger.debug(f"Callingggggggggg ")
            result = await graph.ainvoke(input_data, config=thread_config)
            logger.debug(f"Raw graph response: {result}")

        # result = await graph.ainvoke(input_data, config)
        # logger.debug(f"Raw graph response: {result}")
        
        # Check for next steps
        logger.info(f"Checking for next steps... {result}")
        next_step = await check_next_steps(graph, config=thread_config)
        if next_step:
            return next_step
        
        # Extract and return response
        logger.info(f"Returning chatbot response: {result}")
        return extract_response_content(result)
        
    except Exception as e:
        return handle_error(e)