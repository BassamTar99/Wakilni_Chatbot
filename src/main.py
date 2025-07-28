# FastAPI app + router mounts
from fastapi import FastAPI

app = FastAPI()

# You can add router includes here, e.g.:
# from src.api.telegram import telegram_router
# app.include_router(telegram_router)

@app.get("/")
def root():
    return {"message": "Wakilni Chatbot API is running!"}

