from typing import List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.llms import ChatMessage, MessageRole
from app.agent.openai import get_agent
from llama_index.agent.openai import OpenAIAgent

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
    agent: OpenAIAgent = Depends(get_agent),
):
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    try:
        response = await agent.astream_chat(lastMessage.content, messages)
    except Exception as e:
        print("error ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in chat",
        )

    
    # stream response
    async def event_generator():
        async for token in response.async_response_gen():
            print('token ', token)
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                print("connection stopped")
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
