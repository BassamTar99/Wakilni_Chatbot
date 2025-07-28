# FastAPI app + router mounts
from fastapi import FastAPI

from src.api.telegram import telegram_router

app = FastAPI()
app.include_router(telegram_router)

@app.get("/")
def root():
    return {"message": "Wakilni Chatbot API is running!"}

