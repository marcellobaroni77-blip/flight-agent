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
    "ZTH": {"sea": 10, "crowd": 6, "type": "sea"},
    "CFU": {"sea": 9, "crowd": 7, "type": "sea"},
    "HER": {"sea": 8, "crowd": 8, "type": "sea"},
    "JTR": {"sea": 10, "crowd": 9, "type": "sea"}
}

airport_score = {
    "BLQ": 6, "VRN": 6.5, "VCE": 7, "BGY": 7.5, "MXP": 8
}

# ----------------------------
# prezzo realistico simulato (mercato)
# ----------------------------
def get_price(o, d):
    base = 55 + (airport_score.get(o, 6) * 5)
    base += destination_profile.get(d, {"sea": 7})["sea"] * 4
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

for o in airports[:3]:
    for d in destinations[:3]:

        route = f"{o}->{d}"
        price = get_price(o, d)
        old = history.get(route)

        # trend
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

        profile = destination_profile.get(d, {"sea": 7, "crowd": 7})

        # SCORE INTELLIGENTE
        score = (
            profile["sea"] * 2
            - profile["crowd"] * 0.5
            - price / 40
            + airport_score.get(o, 6)
        )

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

# migliore scelta
best = max(results, key=lambda x: x["score"])

msg = "🌍 TRAVEL PLANNER AI REPORT\n\n"

msg += f"🏆 MIGLIORE DESTINAZIONE OGGI:\n{best['route']}\n"
msg += f"💰 Prezzo stimato: {best['price']} €\n"
msg += f"⭐ Score viaggio: {round(best['score'],1)}\n\n"

msg += "📊 CLASSIFICA COMPLETA:\n"

for r in sorted(results, key=lambda x: x["score"], reverse=True):
    msg += f"- {r['route']}: {r['price']} € | {r['trend']} | score {round(r['score'],1)}\n"

msg += "\n🧭 Consiglio: scegli sempre la destinazione con score più alto, non solo il prezzo"

send_message(msg)
