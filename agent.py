import os
import json
import requests
import csv
import random
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

FILE = "history.csv"

# ----------------------------
# RANGE REALISTICO (non random puro)
# simula prezzi reali low-cost europei
# ----------------------------
def get_market_price(origin, dest):
    base_map = {
        "BLQ": 70, "VRN": 75, "VCE": 80, "BGY": 65, "MXP": 85
    }

    dest_factor = {
        "ZTH": 40, "CFU": 50, "HER": 60, "JTR": 70
    }

    base = base_map.get(origin, 80) + dest_factor.get(dest, 60)
    variation = random.randint(-20, 45)

    return max(49, base + variation)

# ----------------------------
# storico
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
        price = get_market_price(o, d)
        old = history.get(route)

        # analisi trend
        if old is None:
            signal = "🆕 nuovo monitoraggio"
        else:
            diff = price - old

            if diff <= -15:
                signal = "🟢 buon momento (in calo)"
            elif diff >= 15:
                signal = "🔴 possibile aumento"
            else:
                signal = "🟡 stabile"

        flights.append({
            "route": route,
            "price": price,
            "signal": signal
        })

        history[route] = price

# salva storico
with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in history.items():
        writer.writerow([k, v])

best = min(flights, key=lambda x: x["price"])

msg = "✈️ Travel Radar Report\n\n"
msg += f"🏆 MIGLIOR OPPORTUNITÀ:\n{best['route']} — {best['price']} €\n\n"

msg += "📊 ANALISI ROTTE:\n"
for f in sorted(flights, key=lambda x: x["price"]):
    msg += f"- {f['route']}: {f['price']} € {f['signal']}\n"

msg += "\n💡 Consiglio: monitora le rotte 🟢 e attendi cali sotto 70€"

send_message(msg)
