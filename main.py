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

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_message(chat_id, text):
    requests.post(TELEGRAM_API_URL, json={
        "chat_id": chat_id,
        "text": text
    })

def get_user_language(chat_id):
    result = supabase.table("user_languages").select("*").eq("chat_id", chat_id).execute()
    if result.data:
        return result.data[0]["language"]
    return "en"

def set_user_language(chat_id, language):
    existing = supabase.table("user_languages").select("*").eq("chat_id", chat_id).execute()
    if existing.data:
        supabase.table("user_languages").update({"language": language}).eq("chat_id", chat_id).execute()
    else:
        supabase.table("user_languages").insert({"chat_id": chat_id, "language": language}).execute()

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        if user_message.startswith("/start"):
            send_message(chat_id, "Welcome to Lexi! Please type your preferred language code (e.g., `en`, `ru`, `es`, `fr`, `de`).")
        elif len(user_message.strip()) == 2:
            # Если это язык (по коду)
            set_user_language(chat_id, user_message.strip())
            send_message(chat_id, f"Language set to {user_message.strip()}. Send me text to translate.")
        else:
            lang = get_user_language(chat_id)
            translated = GoogleTranslator(source='auto', target=lang).translate(user_message)
            send_message(chat_id, f"Translation: {translated}")
    return {"ok": True}

@app.route("/", methods=["GET"])
def index():
    return "Lexi bot is running!"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)