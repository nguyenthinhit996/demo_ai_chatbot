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
from langchain_community.tools.tavily_search import TavilySearchResults
from app.chatbot.core.nodes.email import ToResponseEmailAssistant

# primary_assistant_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful customer support assistant for resident-management-company. "
#             "Your primary role is to search for flight information and company policies to answer customer queries. "
#             "If a customer requests to update or cancel a flight, book a car rental, book a hotel, or get trip recommendations, "
#             "delegate the task to the appropriate specialized assistant by invoking the corresponding tool. You are not able to make these types of changes yourself."
#             " Only the specialized assistants are given permission to do this for the user."
#             "The user is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
#             "Provide detailed information to the customer, and always double-check the database before concluding that information is unavailable. "
#             " When searching, be persistent. Expand your query bounds if the first search returns no results. "
#             " If a search comes up empty, expand your search before giving up."
#             "\n\nCurrent user flight information:\n<Flights>\n{user_info}\n</Flights>"
#             "\nCurrent time: {time}.",
#         ),
#         ("placeholder", "{messages}"),
#     ]
# ).partial(time=datetime.now)


# You are a helpful manager support assistant for resident-management-company. If a manager ask any related to email, should use ToResponseEmailAssistant to handle reponse email and pass list original message to this tool. You are not able to make these types of changes yourself.The manager is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. if the context is email. please answer with format below: 
# Subject: 
# Hi...
# Context...
# Best regards.

# primary_assistant_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful manager support assistant for resident-management-company. "
#             "If a manager ask any related to email, should use ToResponseEmailAssistant to handle reponse email and pass list original message to this tool. "
#             "You are not able to make these types of changes yourself."
#             "The manager is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
#             "Provide detailed information to the manager, and always double-check the database before concluding that information is unavailable. "
#             " When searching, be persistent. Expand your query bounds if the first search returns no results. "
#             " If a search comes up empty, expand your search before giving up."
#             "\n\nCurrent manager information: \n{manager}\n "
#             "\nCurrent time: {time}.",
#         ),
#         ("placeholder", "{messages}"),
#     ]
# ).partial(time=datetime.now)

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful manager support assistant for resident-management-company. "
            "If a manager ask any related to email, should use ToResponseEmailAssistant to handle reponse email and pass list original message to this tool. "
            "You are not able to make these types of changes yourself."
            "The manager is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
            "if the context is email. please answer with format below: "
            "Hi resident, "
            "Answer... "
            "Best regards."
            "\n\nCurrent manager information: \n{manager}\n "
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

primary_assistant_tools = [
    TavilySearchResults(max_results=1),
    # search_flights,
    # lookup_policy,
]

llm = ChatOpenAI(model="gpt-4o-mini")

assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools
    + [
        ToResponseEmailAssistant,
        # ToBookCarRental,
        # ToHotelBookingAssistant,
        # ToBookExcursion,
    ]
)