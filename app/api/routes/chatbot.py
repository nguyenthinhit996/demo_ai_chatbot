from fastapi import APIRouter, HTTPException
from app.chatbot.logic import process_chat, process_chat_for_testing
# from app.chatbot.logic_reply_mail import process_chat
from app.schemas.chatbot import UserMessage
from fastapi import FastAPI, Request
from IPython.display import Image, display
from app.core.app_helper import get_app
import logging
from app.schemas.chatbot import ContenxtEmail, ContenxtEmailUserReply, TestChat
from langchain_core.messages import HumanMessage, RemoveMessage, AIMessage, ToolMessage
from fastapi.responses import FileResponse


logger = logging.getLogger(__name__)

router = APIRouter()

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

@router.post("/auto-replay")
async def chat(context: ContenxtEmail):
    try:

        # Parse messages to string
        messages_str = parse_email_messages_to_str(context.messages)

        # Create the human message
        human_message =f"Given a list of messages email, suggest professional responses to unresolved issues or recurring topics. \n Subject's email: {context.subject}\n\nMessages:\n{messages_str} \n"

        user = UserMessage(msg=human_message, threadId=context.threadId, manager=context.manager, status=context.status, msgFeedback=context.msgFeedback
                           , residentAppUserId=context.residentAppUserId, siteId=context.siteId, token=context.token, origin=context.origin)
        response = await process_chat(user)
        manager = context.manager
        logger.info(f"Response: {response}")
        return {"manager": manager, "bot_response": response}
    except Exception as e:
        print("Error processing", {e})
        logger.error(f"Error processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user-reply")
async def chat(context: ContenxtEmailUserReply):
    try:
        logging.log(logging.INFO, f"Context: {context}")
        user = UserMessage(msg="Empty", threadId=context.threadId, status=context.status, msgFeedback=context.msgFeedback
                           , residentAppUserId=context.residentAppUserId, siteId=context.siteId, token=context.token, origin=context.origin)
        response = await process_chat(user)
        logger.info(f"user-reply Response: {response}")
        # check 'question ' in response or not
        if isinstance(response, dict) and 'question' in response:
            data = {
                "ai": {
                    "conversationId": context.threadId,
                    "asking": response
                }
            }
            return {"manager": "manager", "bot_response": data}
        else:
            data = {
                "ai": {
                    "conversationId": context.threadId,
                    "hint": {
                        "content": response
                    }
                }
            }
            logger.info(f"Response bot_response: {data}")
            return {"manager": "manager", "bot_response": data}
    except Exception as e:
        print("Error processing", {e})
        logger.error(f"Error processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def testchat():
    try:
        logging.log(logging.INFO, f"Context: test chat is running")
        return {"reply": "server run ok"}
    except Exception as e:
        print("Error processing", {e})
        logger.error(f"Error processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/chat")
async def testchatbotbyrest(testChat: TestChat):
    try:

        user = UserMessage(msg=testChat.msg, threadId=testChat.threadId)
        response = await process_chat_for_testing(user)
        logger.info(f"Response: {response}")
        return {"user": testChat.msg, "bot_response": response}
    except Exception as e:
        print("Error processing", {e})
        logger.error(f"Error processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generateimage")
async def download_image():
    try:
        # Retrieve the application and graph state
        app = get_app()
        graph = getattr(app.state, "graph", None)
        
        if not graph:
            raise HTTPException(status_code=500, detail="Graph state is not available")

        # Generate the image data
        img_data = graph.get_graph().draw_mermaid_png()
        
        # Save the image to a temporary file
        temp_file_path = "/tmp/generated_image.png"
        with open(temp_file_path, "wb") as f:
            f.write(img_data)
        
        # Return the file as a downloadable response
        return FileResponse(
            temp_file_path,
            media_type="image/png",
            filename="generated_image.png"
        )
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")