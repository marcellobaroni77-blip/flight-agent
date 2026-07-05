import os
import json
import requests
from datetime import datetime
import random
import csv

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

with open("config.json", "r") as f:
    config = json.load(f)

airports = config["airports"]
destinations = config["destinations"]

FILE = "prices.csv"

# ----------------------------
# prezzo simulato realistico
# ----------------------------
def generate_price(origin, dest):
    base = 60 + (len(origin) * 7) + (len(dest) * 6)
    return max(45, base + random.randint(-15, 35))

# ----------------------------
# carica storico
# ----------------------------
history = {}
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            history[row[0]] = int(row[1])

flights = []

for o in airports[:3]:
    for d in destinations[:3]:

        route = f"{o}->{d}"
        price = generate_price(o, d)

        old_price = history.get(route)

        trend = ""
        if old_price:
            if price < old_price:
                trend = "📉 sceso"
            elif price > old_price:
                trend = "📈 salito"
            else:
                trend = "➡️ stabile"

        flights.append({
            "route": route,
            "price": price,
            "trend": trend
        })

        history[route] = price

# salva storico
with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in history.items():
        writer.writerow([k, v])

best = min(flights, key=lambda x: x["price"])

msg = "✈️ Travel Agent Report\n\n"
msg += f"🏆 MIGLIORE OFFERTA:\n{best['route']} — {best['price']} €\n\n"

msg += "📊 Dettaglio:\n"
for f in sorted(flights, key=lambda x: x["price"]):
    msg += f"- {f['route']}: {f['price']} € {f['trend']}\n"

send_message(msg)
