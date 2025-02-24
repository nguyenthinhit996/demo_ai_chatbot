from typing import Optional, Type, List, Dict
from datetime import date, datetime
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

class EmailMessage(BaseModel):
    """
    Schema message for email content.
    """
    sender: str = Field( min_length=1, example="user@gmail.com", title="From", description="Email from.", default="")
    receiver: str = Field( min_length=1, example="manager.n@resident-management-company.io", title="To", description="Email to.", default="")
    content: str = Field( min_length=1, example="Hello AI!", title="content", description="Email body.", default="No Content")

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

class GenerateAnwserEmailSimplelInput(BaseModel):
    manager: str = Field(default=None, example="manager", title="Manager", description="Manager name.")
    messages: list[EmailMessage] = Field(default=[], title="List Message between resident and manager", description="List message")
    subject: str = Field( min_length=1, example="Hello AI!", title="Subject", description="Email subject.", default="")

class GenerateAnwserEmailSimple(BaseTool):
    name: str = "GenerateAnwserEmailTool"
    description: str = "Useful for generating answer when resident send email to manager, these email not related to any request"
    args_schema: Type[BaseModel] = GenerateAnwserEmailSimplelInput
    return_direct: bool = True

    def _run(
        self, 
        manager: str, 
        messages: list[EmailMessage], 
        subject: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict]:
            """Use the tool."""
            assistant_prompt = SystemMessage(
            content=(
                "You are a helpful customer support assistant for resident-management-company. You are playing the role of a manager {manager} who is responding to a resident's email. "
                "Given a list of messages, identify patterns, summarize key points, and suggest professional responses to unresolved issues or recurring topics. "
                "Format the response is a text, the content is concise not including Dear and signature \n"
                "Current time: {time}."
            ).format(manager=manager, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            # Parse messages to string
            messages_str = parse_email_messages_to_str(messages)

            # Create the human message
            human_message = HumanMessage(
                content=f"Subject's email: {subject}\n\nMessages:\n{messages_str}"
            )

            # Combine messages into a list
            conversation = [assistant_prompt, human_message]

            # Initialize the chat model
            llm = ChatOpenAI(model="gpt-4o-mini")

            # Invoke the LLM
            response = llm.generate(messages=[conversation])

            # Return the AI response content
            return response.generations[0][0].text

    async def _arun(
        self,
        manager: str, 
        messages: list[EmailMessage], 
        subject: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> List[Dict]:
        """Use the tool asynchronously."""
        print("Using the tool asynchronously")
        # If the calculation is cheap, you can just delegate to the sync implementation
        # as shown below.
        # If the sync calculation is expensive, you should delete the entire _arun method.
        # LangChain will automatically provide a better implementation that will
        # kick off the task in a thread to make sure it doesn't block other async code.
        return self._run(manager, messages, subject, run_manager=run_manager.get_sync()) 
    


    