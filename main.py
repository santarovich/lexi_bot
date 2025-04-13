from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def translate_text(text):
    # временная заглушка перевода
    return f"Перевод: {text[::-1]}"  # переворачивает текст как пример

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")
        translated = translate_text(user_message)
        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": translated
        })
    return {"ok": True}

@app.route("/", methods=["GET"])
def index():
    return "Lexi bot is running!"
    