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
    return max(45, base + random.randint(-20, 40))

# ----------------------------
# storico prezzi
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

        # ----------------------------
        # LOGICA DECISIONALE
        # ----------------------------
        if old_price is None:
            decision = "🆕 nuovo monitoraggio"
        else:
            diff = price - old_price

            if diff <= -10:
                decision = "🟢 conviene aspettare"
            elif diff >= 10:
                decision = "🔴 possibile momento di prenotare"
            else:
                decision = "🟡 stabile"

        flights.append({
            "route": route,
            "price": price,
            "decision": decision
        })

        history[route] = price

# salva storico
with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in history.items():
        writer.writerow([k, v])

best = min(flights, key=lambda x: x["price"])

msg = "✈️ Travel Agent AI Report\n\n"
msg += f"🏆 MIGLIORE OFFERTA:\n{best['route']} — {best['price']} €\n\n"

msg += "📊 ANALISI:\n"
for f in sorted(flights, key=lambda x: x["price"]):
    msg += f"- {f['route']}: {f['price']} € {f['decision']}\n"

msg += "\n🤖 Consiglio automatico attivo"

send_message(msg)
