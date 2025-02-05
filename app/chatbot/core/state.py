from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from typing import Annotated, Literal, Optional


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]

class ChatBotState(TypedDict):
    messages: Annotated[list, add_messages]
    summary: str
    manager: str
    dialog_state: Annotated[
        list[
            Literal[
                "assistant",
                "email",
            ]
        ],
        update_dialog_stack,
    ]
    user_info: str