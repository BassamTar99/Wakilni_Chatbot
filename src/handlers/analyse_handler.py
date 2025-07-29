
from src.services.db_service import save_message, get_conversation
from src.services.ai_analysis import build_prompt, call_openai

def handle_analysis(chat_id: str, user_text: str) -> str:
    # 1. save incoming
    save_message(chat_id, 'user', user_text)
    # 2. gather history & build prompt
    history = get_conversation(chat_id)
    prompt = build_prompt(history, user_text)
    # 3. call OpenAI
    ai_reply = call_openai(prompt)
    # 4. save & return
    save_message(chat_id, 'bot', ai_reply)
    return ai_reply
