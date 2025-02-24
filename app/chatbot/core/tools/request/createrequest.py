from typing import Optional, Type, Union, List, Dict
from datetime import date, datetime
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.app_helper import get_app
from app.chatbot.core.state import ChatBotState
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from app.api.external_service.request import create_request
import json
import logging

class ItemValue(BaseModel):
    itemId: Optional[str] = Field(description="id of item from available template",  default=None)
    value: Optional[str] = Field(description="value of item from user input, if value is type of date should parse to correctly format ISO 8601 example: 2024-12-19T17:00:00.000Z ", default=None)

class CreateRequestToolInput(BaseModel):
    formVersionId: str = Field(description="formVersionId of template request")
    itemsValue: Optional[List[ItemValue]] = Field(
        description="List of ItemValue, data user want to create request",
        default=None
    )

class CreateRequestTool(BaseTool):
    name: str = "CreateRequestTool"
    description: str = """this tool is used to create a request based on the template id and the values of the items in the template."""
    args_schema: Type[BaseModel] = CreateRequestToolInput
    return_direct: bool = True

    async def runWithAsynch(
        self,
        formVersionId: str,
        itemsValue: List[ItemValue], 
        run_manager: Optional[CallbackManagerForToolRun] = None,
        config: RunnableConfig = None,
    ) -> List[Dict]:
            
            configuration = config.get("configurable", {})
            residentAppUserId = configuration.get("residentAppUserId", None)
            siteId = configuration.get("siteId", None)
            token = configuration.get("token", None)
            origin = configuration.get("origin", None)
            print(f"CreateRequestTool siteId: {siteId}")

            logging.info(f"Create Request with id: {itemsValue}")
            if not itemsValue:
                raise ValueError("itemsValue cannot be empty")
            print(f"Create Request with id: {formVersionId}")
            submissionId = await create_request(formVersionId=formVersionId, itemsValue=itemsValue, residentAppUserId=residentAppUserId, siteId=siteId, token=token, origin=origin)
            return f"Create Request with id: {submissionId} Successfully"

    def _run(
        self,
        formVersionId: str, 
        itemsValue: List[ItemValue], 
        run_manager: Optional[CallbackManagerForToolRun] = None,
        config: RunnableConfig = None,
    ) -> List[Dict]:
        
        return None

    async def _arun(
        self,
        formVersionId: str, 
        itemsValue: List[ItemValue], 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        config: RunnableConfig = None,
    ) -> List[Dict]:
        print("Using the tool asynchronously")
        data = await self.runWithAsynch(formVersionId, itemsValue, run_manager=run_manager.get_sync(), config=config)
        return data