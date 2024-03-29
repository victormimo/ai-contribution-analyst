from typing import List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status

from llama_index.core.llms import MessageRole
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from dotenv import load_dotenv
import json

load_dotenv()

from app.agent.openai import get_agent

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


# how the fuck do I pass more data
@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
    agent = Depends(get_agent),
):
    print("data", data)

    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    
    lastMessage = data.messages.pop()

    print("last_message", lastMessage)
   
    chat_history = []
     # Iterate through messages and add them to history based on their role
    for m in data.messages:
        if m.role == MessageRole.ASSISTANT:
            chat_history.extend([
                AIMessage(content=m.content)
            ])
        elif m.role == MessageRole.USER:
            chat_history.extend([
                HumanMessage(content=m.content)
            ])

    print("chat history ", chat_history)

    try:
        # response = await agent.astream_chat(lastMessage.content, messages)
        response = agent.astream({ "input": lastMessage, "chat_history": chat_history })
    except Exception as e:
        print("Error here: ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in chat engine",
        )

    async def event_generator():
        async for token in response:  # Assuming response is an async iterable
            output_text = token.get('output', '')  # Extract the 'output' text
            yield output_text  # Stream the 'output' text back to the client

    return StreamingResponse(event_generator(), media_type="text/plain")


