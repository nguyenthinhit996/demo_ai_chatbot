from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from langchain_openai import ChatOpenAI
from app.chatbot.core.nodes.email import ToResponseEmailAssistant

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

llm = ChatOpenAI(model="gpt-4o-mini")

assistant_runnable = primary_assistant_prompt | llm.bind_tools([ToResponseEmailAssistant])