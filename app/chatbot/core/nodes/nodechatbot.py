
from app.chatbot.core.state import ChatBotState
from app.core import config
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
import logging
logger = logging.getLogger(__name__)


#  # Create a settings instance
settings = config.Settings()

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