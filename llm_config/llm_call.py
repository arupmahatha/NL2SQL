import requests
import os
from dotenv import load_dotenv;

LLM_API_URL = "https://api.deepseek.com/v1/chat/completions"

conversation_history = []
max_turns = 5

def generate_text(prompt: str, api_key: str = None):
    """Generate text using the default LLM (DeepSeek) with conversation history and user API key or .env fallback."""
    global conversation_history
    conversation_history.append({"role": "user", "content": prompt})
    messages = []
    start_idx = max(0, len(conversation_history) - (max_turns * 2))
    for i in range(start_idx, len(conversation_history)):
        entry = conversation_history[i]
        messages.append({
            "role": entry["role"],
            "content": entry["content"]
        })
    # Use provided api_key or fallback to .env
    if api_key is None:
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
    return _call_llm_api(messages, api_key)

def _call_llm_api(messages, api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 1024
    }
    try:
        response = requests.post(LLM_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            generated_text = response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            _update_conversation_history(generated_text)
            return generated_text
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            print(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error calling LLM API: {str(e)}"
        print(error_msg)
        return error_msg

def _update_conversation_history(generated_text: str):
    global conversation_history
    conversation_history.append({"role": "assistant", "content": generated_text})
    if len(conversation_history) > max_turns * 2:
        conversation_history = conversation_history[-(max_turns * 2):]

def reset_conversation():
    global conversation_history
    conversation_history = []
    return True