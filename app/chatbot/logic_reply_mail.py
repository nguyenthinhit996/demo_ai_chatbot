
from typing import Dict, Any, Union, Tuple, Optional
from fastapi import HTTPException, status
from app.chatbot.core.graph import ChatBotGraph
from app.schemas.chatbot import UserMessage
from app.core.app_helper import get_app
from langgraph.types import Command
from contextlib import asynccontextmanager
import logging
from app.schemas.chatbot import ContenxtEmail
import json

from typing import Optional, Type, Union, List, Dict
from datetime import date, datetime
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage


logger = logging.getLogger(__name__)

class ChatbotError(Exception):
    """Base exception for chatbot-related errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

def format_chat_input(context: ContenxtEmail) -> Dict[str, Any]:
    """Format the user message into the expected graph input structure"""
    message = f" I am {context.manager} , providing you a list message {context.messages} , please give me a sensible response to resident"
    return {
        "messages": [("user", message)]
    }

def format_config(thread_id: Union[str, int]) -> Dict[str, Any]:
    """Format the configuration dictionary for graph processing"""
    return {
        "configurable": {
            "thread_id": str(thread_id)
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

def parse_email_messages_to_str(messages: list) -> str:
    """
    Parses a list of custom EmailMessage objects into a formatted string.

    Args:
        messages (list): List of EmailMessage objects with `sender`, `receiver`, and `content` attributes.

    Returns:
        str: Formatted string representation of the messages.
    """
    formatted_messages = []
    for message in messages:
        # Access attributes directly
        sender = getattr(message, "sender", "Unknown Sender")
        receiver = getattr(message, "receiver", "Unknown Receiver")
        content = getattr(message, "content", "No Content")

        # Format the message
        formatted_messages.append(
            f"From: {sender}\nTo: {receiver}\nContent: {content}\n"
        )

    return "\n".join(formatted_messages)


async def process_chat(context: ContenxtEmail) -> str:

    try:
        # assistant_prompt = ChatPromptTemplate.from_messages(
        #     [
        #         (
        #             "system",
        #             "You are a helpful customer support assistant for resident-management-company. You are playing the role of a manager {manager} who is responding to a resident's email."
        #             "Given a list of messages, identify patterns, summarize key points, and suggest professional responses to unresolved issues or recurring topics."
        #             "Format response as a text email."
        #             "\nCurrent time: {time}.",
        #         ),
        #         ("placeholder", "{messages}"),
        #     ]).partial(time=datetime.now).partial(manager=context.manager)

        # llm = ChatOpenAI(model="gpt-4o-mini")
        # messages_str =  parse_email_messages_to_str(context.messages)
        # humanmsg = HumanMessage(content=f" Subject's email: {context.subject} \n\n Messages: {messages_str}")
        # messages = [
        #     assistant_prompt,
        #     humanmsg,
        # ]
    
        # response = llm.invoke({"messages": messages})
        # return response

        # Define the system message prompt template
        assistant_prompt = SystemMessage(
            content=(
                "You are a helpful customer support assistant for resident-management-company. You are playing the role of a manager {manager} who is responding to a resident's email. "
                "Given a list of messages, identify patterns, summarize key points, and suggest professional responses to unresolved issues or recurring topics. "
                "Format the response is a text, the content is concise not including Dear and signature \n"
                "Current time: {time}."
            ).format(manager=context.manager, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        # Parse messages to string
        messages_str = parse_email_messages_to_str(context.messages)

        # Create the human message
        human_message = HumanMessage(
            content=f"Subject's email: {context.subject}\n\nMessages:\n{messages_str}"
        )

        # Combine messages into a list
        conversation = [assistant_prompt, human_message]

        # Initialize the chat model
        llm = ChatOpenAI(model="gpt-4o-mini")

        # Invoke the LLM
        response = await llm.agenerate(messages=[conversation])

        # Return the AI response content
        return response.generations[0][0].text
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        return handle_error(e)