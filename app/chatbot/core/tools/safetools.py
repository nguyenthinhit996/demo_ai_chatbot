 
from typing import List
from langchain_core.tools import BaseTool
from app.chatbot.core.tools.request.getrequest import GetRequestTool
from app.chatbot.core.tools.emails.generateanwser import GenerateAnwserEmailSimple
from app.chatbot.core.tools.templates.gettemplatedetails import GetTemplateDetailsTool
from app.chatbot.core.tools.templates.gettemplates import GetTemplatesTool

class SafeTools:
    tools: List[BaseTool]
    
    def __init__(self, tools=None):
        if tools is None:
            tools = []
        self.tools = tools

safe_tools = SafeTools([GetRequestTool(), GenerateAnwserEmailSimple(), GetTemplateDetailsTool(), GetTemplatesTool()]).tools