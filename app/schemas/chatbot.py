from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class StatusEnum(str, Enum):
    APPROVAL = "approval"
    REJECT = "reject"
    FEEDBACK = "feedback"


class UserMessage(BaseModel):
    """
    Schema message for user can asking.
    """
    threadId: str = Field(..., min_length=1, example="2323", title="Thread ID", description="Unique identifier for the conversation thread.")
    msg: str = Field(..., min_length=1, example="Hello AI!", title="User Message", description="The content of the user's message.")
    status: Optional[StatusEnum] = Field(default=None, example="approval", title="Message Status", description="Current status of the message.")
    manager: Optional[str] = Field(default=None, example="manager", title="Manager", description="Manager name.")
    msgFeedback: Optional[str] = Field(default=None, example="Hello AI!", title="User Message", description="The content of the user's feedback tool.")
    residentAppUserId: Optional[str] = Field(default=None, example="residentAppUserId", title="residentAppUserId", description="residentAppUserId.")
    siteId: Optional[str] = Field(default=None, example="siteId", title="Site ID", description="Site ID of the resident.")

class EmailMessage(BaseModel):
    """
    Schema message for email content.
    """
    sender: str = Field( min_length=1, example="user@gmail.com", title="From", description="Email from.", default="")
    receiver: str = Field( min_length=1, example="manager.n@resident-management-company.io", title="To", description="Email to.", default="")
    content: str = Field( min_length=1, example="Hello AI!", title="Body", description="Email body.", default="No Content")

class ContenxtEmail(BaseModel):
    """
    Schema message for user can asking.
    """
    threadId: str = Field(..., min_length=1, example="2323", title="Thread ID", description="Unique identifier for the conversation thread.")
    manager: Optional[str] = Field(default=None, example="manager", title="Manager", description="Manager name.")
    messages: Optional[list[EmailMessage]] = Field(default=[], title="List Message between resident and manager", description="List message")
    subject: Optional[str] = Field( min_length=1, example="Hello AI!", title="Subject", description="Email subject.", default="")
    status: Optional[StatusEnum] = Field(default=None, example="approval", title="Message Status", description="Current status of the message.")
    msgFeedback: Optional[str] = Field(default=None, example="Hello AI!", title="User Message", description="The content of the user's feedback tool.")
    residentAppUserId: Optional[str] = Field(default=None, example="residentAppUserId", title="residentAppUserId ID", description="residentAppUserId ID.")
    siteId: Optional[str] = Field(default=None, example="siteId", title="Site ID", description="Site ID of the resident.")


class ContenxtEmailUserReply(BaseModel):
    """
    Schema message for user can asking.
    """
    threadId: str = Field(..., min_length=1, example="2323", title="Thread ID", description="Unique identifier for the conversation thread.")
    status: Optional[StatusEnum] = Field(default=None, example="approval", title="Message Status", description="Current status of the message.")
    msgFeedback: Optional[str] = Field(default=None, example="Hello AI!", title="User Message", description="The content of the user's feedback tool.")
    residentAppUserId: Optional[str] = Field(default=None, example="residentAppUserId", title="residentAppUserId ID", description="residentAppUserId ID.")
    siteId: Optional[str] = Field(default=None, example="siteId", title="Site ID", description="Site ID of the resident.")