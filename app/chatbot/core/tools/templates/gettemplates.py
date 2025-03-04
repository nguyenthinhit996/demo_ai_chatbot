from typing import Optional, Type, Union, List, Dict
from datetime import date, datetime
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.app_helper import get_app
from app.api.external_service.template import get_all_templates
from langchain_core.runnables import RunnableConfig

# class GetTemplatesToolInput(BaseModel):

class GetTemplatesTool(BaseTool):
    name: str = "GetTemplatesTool"
    description: str = """This tool retrieves a list of all available templates.
    It is designed to help residents find and select templates suited to their needs when creating specific types of requests"""
    # args_schema: None
    return_direct: bool = True

    async def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        config: RunnableConfig = None,
    ) -> List[Dict]:
            # app = get_app()
            # mock_templates = app.state.mock_templates
            # # Filter mock data based on inputs
            # print(f"Found {mock_templates}")

            configuration = config.get("configurable", {})
            token = configuration.get("token", None)
            origin = configuration.get("origin", None)
            templates = await get_all_templates(token, origin)

            print(f"get_all_templates: {templates}")

            return templates

    async def _arun(
        self,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        config: RunnableConfig = None,
    ) -> List[Dict]:
        """Use the tool asynchronously."""
        print("Using the tool asynchronously")
        data = await self._run(run_manager=run_manager.get_sync(), config=config) 
        return data
    


    