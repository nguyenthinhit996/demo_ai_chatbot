
from app.api.routes import chatbot
from app.core.startup import create_app
from app.core.app_helper import set_app
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = create_app()
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
set_app(app)