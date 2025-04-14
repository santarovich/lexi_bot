from flask import Flask, request
from deep_translator import GoogleTranslator
from supabase import create_client, Client
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("Loaded ENV variables:")
print("TELEGRAM_TOKEN exists:", TELEGRAM_TOKEN is not None)
print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY exists:", SUPABASE_KEY is not None)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_message(chat_id, text):
    print(f"Sending message to {chat_id}: {text}")
    response = requests.post(TELEGRAM_API_URL, json={
        "chat_id": chat_id,
        "text": text
    })
    print("Telegram API response:", response.json())

def get_user_language(chat_id):
    print(f"Fetching language for chat_id {chat_id}")
    result = supabase.table("user_languages").select("*").eq("chat_id", chat_id).execute()
    print("Supabase result:", result.data)
    if result.data:
        return result.data[0]["language"]
    return "en"

def set_user_language(chat_id, language):
    print(f"Setting language for chat_id {chat_id} to {language}")
    existing = supabase.table("user_languages").select("*").eq("chat_id", chat_id).execute()
    if existing.data:
        supabase.table("user_languages").update({"language": language}).eq("chat_id", chat_id).execute()
    else:
        supabase.table("user_languages").insert({"chat_id": chat_id, "language": language}).execute()

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received data:", data)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        print(f"Message from {chat_id}: {user_message}")

        if user_message.startswith("/start"):
            send_message(chat_id, "Welcome to Lexi! Please type your preferred language code (e.g., `en`, `ru`, `es`, `fr`, `de`).")
        elif len(user_message.strip()) == 2:
            set_user_language(chat_id, user_message.strip())
            send_message(chat_id, f"Language set to {user_message.strip()}. Send me text to translate.")
        else:
            lang = get_user_language(chat_id)
            print(f"Translating to language: {lang}")
            translated = GoogleTranslator(source='auto', target=lang).translate(user_message)
            send_message(chat_id, f"Translation: {translated}")
    else:
        print("No message.text in data")
    return {"ok": True}

@app.route("/", methods=["GET"])
def index():
    return "Lexi bot is running!"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)