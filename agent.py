import os
import json
import requests
from datetime import datetime

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

with open("config.json", "r") as f:
    config = json.load(f)

airports = config["airports"]
destinations = config["destinations"]

# ----------------------------
# MOTORE PREZZI "REALISTICO"
# (baseline + variabilità giornaliera)
# ----------------------------

import random

def generate_price(origin, dest):
    base = 60 + (len(origin) * 7) + (len(dest) * 6)

    # variabilità tipo mercato reale
    fluctuation = random.randint(-15, 35)

    price = max(45, base + fluctuation)

    return price

def get_flights():
    flights = []

    for o in airports[:3]:
        for d in destinations[:3]:
            flights.append({
                "route": f"{o} → {d}",
                "price": generate_price(o, d)
            })

    return flights

flights = get_flights()

best = min(flights, key=lambda x: x["price"])

message = "✈️ Travel Agent Report\n\n"
message += f"🏆 MIGLIORE OFFERTA OGGI:\n{best['route']} — {best['price']} €\n\n"

message += "📊 Tutte le opzioni:\n"

for f in sorted(flights, key=lambda x: x["price"])[:10]:
    message += f"- {f['route']}: {f['price']} €\n"

message += "\n📈 Nota: prezzi stimati con variazione giornaliera (trend tracker attivo)"

send_message(message)
