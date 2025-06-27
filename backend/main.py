from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent.agent import chat_with_agent

app = FastAPI()

class ChatInput(BaseModel):
    user_message: str

@app.post("/api/chat")  # <-- changed from /chat to /api/chat
async def chat(input: ChatInput):
    reply = await chat_with_agent(input.user_message)
    return {"response": reply}