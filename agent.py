import os
import json
import requests

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# leggi configurazione
with open("config.json", "r") as f:
    config = json.load(f)

airports = config["airports"]
destinations = config["destinations"]

# SIMULAZIONE RICERCA VOLI (per ora gratis e funzionante)
# 👉 dopo la sostituiamo con dati reali
best_flights = [
    {"route": "BLQ → ZTH", "price": 92},
    {"route": "VRN → CFU", "price": 105},
    {"route": "BGY → HER", "price": 118},
]

# trova il migliore
best = min(best_flights, key=lambda x: x["price"])

message = f"""✈️ Travel Agent Report

🏆 Miglior offerta:
{best['route']} — {best['price']} €

📊 Alternative:
"""

for f in best_flights:
    message += f"- {f['route']}: {f['price']} €\n"

send_message(message)
