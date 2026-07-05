import os
import json
import requests
import csv
import random

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
# PROFILO DESTINAZIONI (logica viaggio reale)
# ----------------------------
destination_profile = {
    "ZTH": {"sea": 10, "crowd": 6},
    "CFU": {"sea": 9, "crowd": 7},
    "HER": {"sea": 8, "crowd": 8},
    "JTR": {"sea": 10, "crowd": 9}
}

airport_penalty = {
    "BLQ": 5, "VRN": 6, "VCE": 4, "BGY": 3, "MXP": 2
}

def market_price(o, d):
    base = 60 + airport_penalty.get(o, 5) * 5
    base += destination_profile.get(d, {"sea": 7})["sea"] * 4
    return max(55, base + random.randint(-25, 40))

# ----------------------------
# storico prezzi
# ----------------------------
history = {}
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            history[row[0]] = int(row[1])

results = []

for o in airports[:3]:
    for d in destinations[:3]:

        route = f"{o}->{d}"
        price = market_price(o, d)
        old = history.get(route)

        # trend
        if old is None:
            trend = "🆕 nuovo"
        else:
            diff = price - old
            if diff < -15:
                trend = "🟢 in calo"
            elif diff > 15:
                trend = "🔴 in aumento"
            else:
                trend = "🟡 stabile"

        # punteggio destinazione (qui nasce l'intelligenza)
        sea_score = destination_profile.get(d, {"sea": 7})["sea"]
        score = sea_score - (price / 50)

        results.append({
            "route": route,
            "price": price,
            "trend": trend,
            "score": score
        })

        history[route] = price

# salva storico
with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in history.items():
        writer.writerow([k, v])

# migliore destinazione
best = max(results, key=lambda x: x["score"])

msg = "✈️ TRAVEL ASSISTANT REPORT\n\n"

msg += f"🏆 MIGLIOR SCELTA OGGI:\n{best['route']}\n"
msg += f"💰 Prezzo stimato: {best['price']} €\n"
msg += f"⭐ Qualità viaggio: {round(best['score'],1)}\n\n"

msg += "📊 ANALISI ROTTE:\n"

for r in sorted(results, key=lambda x: x["score"], reverse=True):
    msg += f"- {r['route']}: {r['price']} € | {r['trend']} | score {round(r['score'],1)}\n"

msg += "\n🧭 Consiglio: scegli la rotta con score più alto, non solo il prezzo"

send_message(msg)
