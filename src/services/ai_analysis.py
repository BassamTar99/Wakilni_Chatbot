
import os
import openai

# Load OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_engineering_prompt(user_message, history=None):
    """
    Build a prompt for the fine-tuned OpenAI model, including system instructions and conversation history.
    """
    system_prompt = (
        "You are Wakilni’s support assistant. "
        "Format your output as JSON. If the user needs a Jira ticket, output a JSON object with a 'create_issue' key. "
        "Otherwise, reply with a plain answer."
    )
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["text"]})
    messages.append({"role": "user", "content": user_message})
    return messages

def call_openai(messages, model=None):
    """
    Call the OpenAI ChatCompletion API with the given messages and return the reply.
    """
    if model is None:
        model = os.getenv("OPENAI_FINE_TUNED_MODEL", "gpt-3.5-turbo")
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.2
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[AI error] {str(e)}"

