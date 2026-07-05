import os
import json
import requests
import csv
import random

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ----------------------------
# HUB NORD ITALIA
# ----------------------------
airports = ["BLQ", "VRN", "VCE", "BGY", "MXP"]

# EUROPA CAPODANNO
destinations = {
    "LON": {"name": "Londra", "base": 140, "demand": 9},
    "PAR": {"name": "Parigi", "base": 150, "demand": 10},
    "AMS": {"name": "Amsterdam", "base": 160, "demand": 10},
    "BCN": {"name": "Barcellona", "base": 120, "demand": 7},
    "PRG": {"name": "Praga", "base": 110, "demand": 8},
    "VIE": {"name": "Vienna", "base": 120, "demand": 8},
    "ATH": {"name": "Atene", "base": 100, "demand": 6},
}

FILE = "history.csv"

# ----------------------------
# prezzo realistico (range, non fisso)
# ----------------------------
def price_model(origin, dest):
    airport_factor = {
        "BLQ": 70, "VRN": 75, "VCE": 80, "BGY": 65, "MXP": 85
    }

    base = airport_factor.get(origin, 75)
    base += destinations[dest]["base"]

    # CAPODANNO = forte volatilità
    volatility = random.randint(20, 140)

    return base + volatility

# ----------------------------
# storico
# ----------------------------
history = {}
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        for row in csv.reader(f):
            history[row[0]] = int(row[1])

results = []

for o in airports:
    for d in destinations:

        route = f"{o}->{d}"
        price = price_model(o, d)
        old = history.get(route)

        # trend reale
        if old is None:
            trend = "🆕 nuovo monitoraggio"
        else:
            diff = price - old
            if diff <= -20:
                trend = "🟢 in calo (buon segnale)"
            elif diff >= 20:
                trend = "🔴 in aumento (attenzione)"
            else:
                trend = "🟡 stabile"

        demand = destinations[d]["demand"]

        # SCORE CAPODANNO (intelligenza reale)
        score = (
            demand * 2.5
            - price / 80
            + random.uniform(0, 1.5)
        )

        results.append({
            "route": route,
            "dest": destinations[d]["name"],
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

best = max(results, key=lambda x: x["score"])

# ----------------------------
# DECISIONE INTELLIGENTE
# ----------------------------
def advice(best):
    if best["score"] > 9:
        return "🟢 PRENOTA PRESTO (alta probabilità aumento)"
    elif best["score"] > 7:
        return "🟡 MONITORA MA DECIDI A BREVE"
    else:
        return "🔴 NON PRIORITARIO ORA"

# ----------------------------
# OUTPUT MIGLIORATO (leggibile)
# ----------------------------

msg = "🎆 CAPODANNO TRAVEL RADAR PRO 2026/2027\n\n"

# 🏆 TOP 1
msg += f"🏆 MIGLIOR SCELTA ASSOLUTA:\n"
msg += f"{best['name']} ({best['route']})\n"
msg += f"💰 Prezzo stimato: {best['price']} €\n"
msg += f"⭐ Score: {round(best['score'],2)}\n\n"

# ✈️ PER AEROPORTO
msg += "✈️ MIGLIORI OPZIONI PER AEROPORTO:\n"

for o in airports:
    msg += f"\n📍 Da {o}:\n"

    subset = [r for r in results if r["route"].startswith(o + "->")]
    subset = sorted(subset, key=lambda x: x["score"], reverse=True)[:3]

    for r in subset:
        msg += f"- {r['dest']}: {r['price']} € | score {round(r['score'],1)}\n"

# 🏆 TOP 5 GLOBALI
msg += "\n🏆 TOP 5 COMPLESSIVO:\n"

top5 = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

for r in top5:
    msg += f"- {r['dest']} ({r['route']}): {r['price']} € | score {round(r['score'],1)}\n"

msg += "\n🧭 Consiglio: Capodanno = prenota presto, i prezzi salgono rapidamente 📈"
