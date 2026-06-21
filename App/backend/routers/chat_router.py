from fastapi import APIRouter
from pydantic import BaseModel

from services.chat_service import ask_ai

router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"]
)

class ChatRequest(BaseModel):

    message:str

class ChatResponse(BaseModel):

    response:str


@router.post(
    "/",
    response_model=ChatResponse
)

async def chat(data: ChatRequest):

    result = ask_ai(data.message)

    return {
        "response":result
    }