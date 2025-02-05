
from langchain_core.prompts import ChatPromptTemplate
from datetime import date, datetime
from app.chatbot.core.nodes.nodechatbot import CompleteOrEscalate
from app.chatbot.core.tools.request.getrequest import GetRequestTool
from app.chatbot.core.tools.emails.generateanwser import GenerateAnwserEmailSimple
from app.chatbot.core.tools.templates.gettemplatedetails import GetTemplateDetailsTool
from app.chatbot.core.tools.templates.gettemplates import GetTemplatesTool
from app.chatbot.core.tools.request.createrequest import CreateRequestTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import ToolMessage
from typing import Callable
from app.chatbot.core.state import ChatBotState


email_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a specialized assistant for handling email response."
            "You are playing the role of a manager {manager} who is responding to a resident's email"
            " The primary assistant delegates work to you whenever the user needs help responding emails. "
            " Reply email with simple content or confirming create, update or delete request with avaiable templates. "
            " At First check whether resident need to manipulate with request should find these related template by calling GetRequestTool and GetTemplateDetailsTool. if the conversation not match any template just reply content, the output only contain content, should be simple not include dear and signature."
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            " Remember that a replying email isn't completed until after the relevant tool has successfully been used."
            "\nCurrent time: {time}."
            "\n\nIf the user needs help, and none of your tools are appropriate for it, then"
            ' "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user\'s time. Do not make up invalid tools or functions.',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

llm = ChatOpenAI(model="gpt-4o-mini")

email_safe_tools = [GetTemplatesTool(), GetTemplateDetailsTool()]
email_sensitive_tools = [CreateRequestTool()]
email_tools = email_safe_tools + email_sensitive_tools
email_runnable = email_prompt | llm.bind_tools(
    email_tools + [CompleteOrEscalate]
)

class EmailMessage(BaseModel): 
    """
    Schema message for email content.
    """
    sender: str = Field( min_length=1, example="user@gmail.com", title="From", description="Email from.", default="")
    receiver: str = Field( min_length=1, example="manager.n@resident-management-company.io", title="To", description="Email to.", default="")
    content: str = Field( min_length=1, example="Hello AI!", title="Body", description="Email body.", default="No Content")

class ToResponseEmailAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle reponse email."""

    messages: list[EmailMessage] = Field(default=[], title="List original Message between resident and manager", description="List message")
    subject: str = Field( min_length=1, example="Hello AI!", title="Subject", description="Email subject.", default="")

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Request for fixing my house",
                "messages": [
                    {
                        "sender": "thinh.n@resident-management-company.io",
                        "receiver": "nguyenthinhit996@gmail.com",
                        "content": "Hello resident how about you house"
                    },
                    {
                        "sender": "nguyenthinhit996@gmail.com",
                        "receiver": "thinh.n@resident-management-company.io",
                        "content": "OMG my house is running ruin very bad"
                    },
                    {
                        "sender": "nguyenthinhit996@gmail.com",
                        "receiver": "thinh.n@resident-management-company.io",
                        "content": "My door cant open smoothly"
                    }
                ],
            }
        }

def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: ChatBotState) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " and the create, update, other other action is not complete until after you have successfully invoked the appropriate tool."
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node        