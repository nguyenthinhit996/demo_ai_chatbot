from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph, START, END
from langchain_core.runnables import RunnableLambda
from app.chatbot.core.state import ChatBotState
from app.chatbot.core.nodes.nodechatbot import Assistant
from langgraph.prebuilt import ToolNode
from app.chatbot.core.nodes.nodehummanreview import human_review_node
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import (
    AnyMessage,
)
import logging
from typing import (
    Any,
    Literal,
    Union,
)
from pydantic import BaseModel
from app.core import config
from app.chatbot.core.nodes.email import create_entry_node, email_runnable, email_sensitive_tools, email_safe_tools, ToResponseEmailAssistant
from app.chatbot.core.nodes.nodechatbot import CompleteOrEscalate
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import tools_condition
from app.chatbot.core.nodes.primary_assistant import assistant_runnable

settings = config.Settings()
logger = logging.getLogger(__name__)

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def tools_condition_custom(
    state: Union[list[AnyMessage], dict[str, Any], BaseModel],
    messages_key: str = "messages",
) -> Literal["human_review", END]:
    if isinstance(state, list): 
        ai_message = state[-1]
    elif isinstance(state, dict) and (messages := state.get(messages_key, [])):
        ai_message = messages[-1]
    elif messages := getattr(state, messages_key, []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "human_review"
    return END

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    logger.error(f"tool_calls {tool_calls}, error: {error}")

def route_email_assistant(
    state: ChatBotState,
):
    route = tools_condition_custom(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
    return "human_review"

# This node will be shared for exiting all specialized assistants
def pop_dialog_state(state: ChatBotState) -> dict:
    """Pop the dialog stack and return to the main assistant.

    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []
    if state["messages"][-1].tool_calls:
        # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }

def route_primary_assistant(
    state: ChatBotState,
):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == ToResponseEmailAssistant.__name__:
            return "enter_email_assistant"
        return END
    raise ValueError("Invalid route")

def user_info(state: ChatBotState):
    return {"user_info": "user_info_mock"}

def route_to_workflow(
    state: ChatBotState,
) -> Literal[
    "primary_assistant",
    "run_email",
]:
    """If we are in a delegated state, route directly to the appropriate assistant."""
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state[-1]

class ChatBotGraph:
    graph: CompiledStateGraph

    def __init__(self, checkpointer):
       self.graph = self.graph_builder(checkpointer)

    def graph_builder(self, checkpointer: AsyncPostgresSaver):
        graph = StateGraph(ChatBotState)

        # graph.add_node("fetch_user_info", user_info)
        # graph.add_edge(START, "fetch_user_info")

        # graph.add_conditional_edges("fetch_user_info", route_to_workflow)

        # Primary assistant
        graph.add_node("primary_assistant", Assistant(assistant_runnable))
        graph.add_edge(START, "primary_assistant")

        # Email assistant
        graph.add_node(
            "enter_email_assistant",
            create_entry_node("response email Assistant", "run_email"),
        )
        graph.add_node("run_email", Assistant(email_runnable))
        graph.add_node("human_review", human_review_node)
        graph.add_edge("enter_email_assistant", "run_email")
        graph.add_node(
            "email_sensitive_tools",
            create_tool_node_with_fallback(email_sensitive_tools),
        )
        graph.add_node(
            "email_safe_tools",
            create_tool_node_with_fallback(email_safe_tools),
        )
        graph.add_edge("email_sensitive_tools", "run_email")
        graph.add_edge("email_safe_tools", "run_email")
        graph.add_conditional_edges(
            "run_email",
            route_email_assistant,
            ["human_review", "leave_skill", END],
        )

        graph.add_node("leave_skill", pop_dialog_state)
        graph.add_edge("leave_skill", "primary_assistant")
        graph.add_conditional_edges(
            "primary_assistant",
            route_primary_assistant,
            [
                "enter_email_assistant",
                END,
            ],
        )

        graph_complier = graph.compile(checkpointer=checkpointer)
        return graph_complier