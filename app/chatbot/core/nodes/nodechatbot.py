
from app.chatbot.core.state import ChatBotState
from langchain_openai import ChatOpenAI
from app.chatbot.core.nodes.nodetools import node_run_tool
from app.core import config

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from datetime import date, datetime
from app.chatbot.core.tools.safetools import safe_tools
from app.chatbot.core.tools.sensitivetools import sensitvetool_tools, sensitive_tool_names
from langchain_core.messages import SystemMessage
from pydantic import BaseModel

import logging
logger = logging.getLogger(__name__)


#  # Create a settings instance
settings = config.Settings()


assistant_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful customer support assistant for resident-management-company."
                    "resident-management-company is a single-platform customer service solution that revolutionises the way management companies connect with their communities."
                    "\nCurrent time: {time}.",
                ),
                ("placeholder", "{messages}"),
            ]
        ).partial(time=datetime.now)

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = assistant_prompt | llm.bind_tools(safe_tools + sensitvetool_tools)

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: ChatBotState, config: RunnableConfig):
        while True:
            # get summary 
            summary = state.get("summary", "")
            messages = state["messages"]
            if summary:
                system_message = f"Summary of conversation earlier: {summary}"
                messages = [SystemMessage(content=system_message)] + state["messages"]
                state = {**state, "messages": messages}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
    
class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""

    cancel: bool = True
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need to search the user's emails or calendar for more information.",
            },
        }    