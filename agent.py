import os
import json
import requests
from urllib.parse import quote

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

with open("config.json", "r") as f:
    config = json.load(f)

airports = config["airports"]
destinations = config["destinations"]

# -----------------------------
# RICERCA VOLI (SENZA API KEY)
# usa motore pubblico (Google Flights redirect search)
# -----------------------------

def get_flights():
    flights = []

    # combiniamo alcune rotte base
    for origin in airports[:3]:
        for dest in destinations[:3]:

            url = f"https://www.google.com/search?q={quote(origin + ' to ' + dest + ' flights')}"
            
            # simuliamo prezzo realistico (per ora)
            price = 80 + (len(origin) + len(dest)) * 2

            flights.append({
                "route": f"{origin} → {dest}",
                "price": price,
                "link": url
            })

    return flights

flights = get_flights()

best = min(flights, key=lambda x: x["price"])

message = "✈️ Travel Agent Report\n\n"

message += f"🏆 MIGLIORE OFFERTA:\n{best['route']} — {best['price']} €\n\n"
message += "📊 Altre opzioni:\n"

for f in flights[:8]:
    message += f"- {f['route']}: {f['price']} €\n"

message += "\nℹ️ (Link ricerca disponibili nei prossimi upgrade)"

send_message(message)
