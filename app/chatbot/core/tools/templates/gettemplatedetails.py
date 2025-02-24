from typing import Optional, Type, Union, List, Dict
from datetime import date, datetime
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.app_helper import get_app
from app.api.external_service.template import get_detail_template
from langchain_core.runnables import RunnableConfig

class GetTemplateDetailsToolInput(BaseModel):
    id: Optional[str] = Field(description="id of template", default=None)

class GetTemplateDetailsTool(BaseTool):
    name: str = "GetTemplateDetailsTool"
    description: str = (
        """This tool retrieves the detailed content of a specific template identified by its ID or name.
        It is designed to provide the AI with the exact structure and fields of the template, enabling it to assist users or systems in creating requests or performing tasks based on the template"""
    )
    args_schema: Type[BaseModel] = GetTemplateDetailsToolInput
    return_direct: bool = True

    async def _run(
        self,
        id: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        config: RunnableConfig = None,
    ) -> List[Dict]:
        if not id:
            raise ValueError("id of template cannot be empty, please provide id of template")

        configuration = config.get("configurable", {})
        token = configuration.get("token", None)
        origin = configuration.get("origin", None)
        data = await get_detail_template(id, token, origin)

        print(f"Filtered templates: {data}")
        return data

    async def _arun(
        self,
        id: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        config: RunnableConfig = None,
    ) -> List[Dict]:
        """Use the tool asynchronously."""
        data =  await self._run(id=id, run_manager=run_manager, config=config)
        return data


    