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

# ----------------------------
# BASE REALISTICA (Nord Italia)
# ----------------------------
airports = ["BLQ", "VRN", "VCE", "BGY", "MXP"]

destinations = {
    "ZTH": {"name": "Zante", "sea": 10},
    "CFU": {"name": "Corfù", "sea": 9},
    "HER": {"name": "Creta", "sea": 8},
    "JTR": {"name": "Santorini", "sea": 10},
}

FILE = "history.csv"

# ----------------------------
# modello prezzi realistico
# ----------------------------
def price_model(origin, dest):
    base_airport = {
        "BLQ": 60, "VRN": 65, "VCE": 70, "BGY": 55, "MXP": 75
    }
    base = base_airport.get(origin, 65)
    base += destinations[dest]["sea"] * 4

    return max(50, base + random.randint(-30, 45))

# ----------------------------
# storico
# ----------------------------
history = {}
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            history[row[0]] = int(row[1])

results = []

for o in airports:
    for d in destinations:

        route = f"{o}->{d}"
        price = price_model(o, d)
        old = history.get(route)

        if old is None:
            trend = "🆕 nuovo"
        else:
            diff = price - old
            if diff <= -15:
                trend = "🟢 in calo"
            elif diff >= 15:
                trend = "🔴 in aumento"
            else:
                trend = "🟡 stabile"

        sea = destinations[d]["sea"]

        # SCORE FINALE (viaggio reale)
        score = sea * 2 - price / 55

        results.append({
            "route": route,
            "price": price,
            "trend": trend,
            "score": score,
            "name": destinations[d]["name"]
        })

        history[route] = price

# salva storico
with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in history.items():
        writer.writerow([k, v])

best = max(results, key=lambda x: x["score"])

# ----------------------------
# LOGICA “VIAGGIO REALE”
# ----------------------------
def travel_advice(best):
    if best["score"] > 8:
        return "🟢 OTTIMO MOMENTO PER PRENOTARE"
    elif best["score"] > 6:
        return "🟡 BUON MOMENTO, MONITORA ANCORA"
    else:
        return "🔴 ASPETTA QUALCHE GIORNO"

advice = travel_advice(best)

# ----------------------------
# OUTPUT
# ----------------------------
msg = "🌍 TRAVEL PLANNER DEFINITIVO - MODENA\n\n"

msg += f"🏆 MIGLIOR DESTINAZIONE:\n{best['name']}\n"
msg += f"💰 Prezzo stimato: {best['price']} €\n"
msg += f"⭐ Score viaggio: {round(best['score'],1)}\n"
msg += f"🧭 Consiglio: {advice}\n\n"

msg += "📊 CLASSIFICA VIAGGI ESTATE:\n"

for r in sorted(results, key=lambda x: x["score"], reverse=True):
    msg += f"- {r['name']}: {r['price']} € | {r['trend']} | score {round(r['score'],1)}\n"

msg += "\n✈️ IDEA PRATICA: weekend o settimana mare dalla zona Modena"

send_message(msg)
