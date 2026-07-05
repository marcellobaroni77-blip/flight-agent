import os
import json
import requests

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# carica configurazione
with open("config.json", "r") as f:
    config = json.load(f)

airports = config["airports"]
destinations = config["destinations"]

# -----------------------------
# VOLI (PER ORA: DATI REALI NON ANCORA COLLEGATI)
# -----------------------------

def get_mock_flights():
    return [
        {"route": "BLQ → ZTH", "price": 92},
        {"route": "VRN → CFU", "price": 105},
        {"route": "BGY → HER", "price": 118},
    ]

flights = get_mock_flights()

best = min(flights, key=lambda x: x["price"])

message = "✈️ Travel Agent Report\n\n"
message += f"🏆 Miglior offerta:\n{best['route']} — {best['price']} €\n\n"
message += "📊 Alternative:\n"

for f in flights:
    message += f"- {f['route']}: {f['price']} €\n"

send_message(message)
