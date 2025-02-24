from typing import Literal
from app.chatbot.core.state import ChatBotState
from langgraph.types import Command, interrupt
from langchain_core.runnables.config import RunnableConfig
import logging
from app.chatbot.core.nodes.email import email_sensitive_tools


logger = logging.getLogger(__name__)

def human_review_node(state: ChatBotState, config: RunnableConfig) -> Command[Literal["run_email", "email_safe_tools", "email_sensitive_tools"]]:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[-1]
    human_review = None
    logger.info(f"Tool call human_review_node: {tool_call}")
    logger.info(f"Tool call email_sensitive_tools: {email_sensitive_tools}")
    if(
    any(
        tool.name == tool_call["name"]
        for tool in email_sensitive_tools
    )):
        logger.info(f"interrupt Tool call human_review_node: {tool_call}")
        configuration = config.get("configurable", {})
        residentAppUserId = configuration.get("residentAppUserId", None)
        siteId = configuration.get("siteId", None)
        threadId = configuration.get("thread_id", None)
        human_review = interrupt(
            {
                "question": "Please Review the sensitive API call",
                "tool_call": tool_call,
                "status": "review",
                "residentAppUserId": residentAppUserId,
                "siteId": siteId,
                "thread_id": threadId,
            }
        )

    if human_review is None:
        return Command(goto="email_safe_tools")

    review_action = human_review["action"]
    review_data = human_review.get("data")

    # if approved, call the tool
    if review_action == "approval":
        return Command(goto="email_sensitive_tools")
    elif review_action == "reject":
        updated_message = [
            {
                "role": "tool",
                # This is our natural language feedback
                "content":f"API call denied by user. Reasoning: 'No need any more'.",
                "name": tool_call["name"],
                "tool_call_id": tool_call["id"],
            },
            {
                "role": "human",
                "content": f"I dont need to ask previous questions anymore, should comfirm me you do not call {tool_call["name"]}",
            },
        ]
        return Command(goto="run_email", update={"messages": updated_message})
    # update the AI message AND call tools
    elif review_action == "update":
        updated_message = {
            "role": "ai",
            "content": last_message.content,
            "tool_calls": [
                {
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    # This the update provided by the human
                    "args": review_data,
                }
            ],
            # This is important - this needs to be the same as the message you replacing!
            # Otherwise, it will show up as a separate message
            "id": last_message.id,
        }
        return Command(goto="run_sensitive_tools", update={"messages": [updated_message]})

    # provide feedback to LLM
    elif review_action == "feedback":
        # NOTE: we're adding feedback message as a ToolMessage
        # to preserve the correct order in the message history
        # (AI messages with tool calls need to be followed by tool call messages)
        tool_message = {
            "role": "tool",
            # This is our natural language feedback
            "content": "user feedback is: " +  review_data,
            "name": tool_call["name"],
            "tool_call_id": tool_call["id"],
        }
        return Command(goto="run_email", update={"messages": [tool_message]})
    
    return Command(goto="run_email")