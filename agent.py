import os
import requests
import csv
import random

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ----------------------------
# AEROPORTI NORD ITALIA
# ----------------------------
airports = ["BLQ", "VRN", "VCE", "BGY", "MXP"]

# ----------------------------
# DESTINAZIONI CAPODANNO EUROPA
# ----------------------------
destinations = {
    "LON": {"name": "Londra", "base": 140},
    "PAR": {"name": "Parigi", "base": 150},
    "AMS": {"name": "Amsterdam", "base": 160},
    "BCN": {"name": "Barcellona", "base": 120},
    "PRG": {"name": "Praga", "base": 110},
    "VIE": {"name": "Vienna", "base": 120},
    "ATH": {"name": "Atene", "base": 100},
}

FILE = "history.csv"

# ----------------------------
# PREZZO SIMULATO REALISTICO CAPODANNO
# ----------------------------
def price_model(origin, dest):
    airport_factor = {
        "BLQ": 70, "VRN": 75, "VCE": 80, "BGY": 65, "MXP": 85
    }

    base = airport_factor.get(origin, 75)
    base += destinations[dest]["base"]

    # Capodanno = alta domanda
    volatility = random.randint(30, 140)

    return base + volatility

# ----------------------------
# CARICA STORICO
# ----------------------------
history = {}
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            history[row[0]] = int(row[1])

results = []

# ----------------------------
# ANALISI ROTTE
# ----------------------------
for o in airports:
    for d in destinations:

        route = f"{o}->{d}"
        price = price_model(o, d)
        old = history.get(route)

        if old is None:
            trend = "🆕 nuovo"
        else:
            diff = price - old
            if diff <= -20:
                trend = "🟢 in calo"
            elif diff >= 20:
                trend = "🔴 in aumento"
            else:
                trend = "🟡 stabile"

        score = destinations[d]["base"] / 20 - price / 150 + random.uniform(0, 1)

        results.append({
            "route": route,
            "dest": destinations[d]["name"],
            "price": price,
            "score": score,
            "trend": trend
        })

        history[route] = price

# ----------------------------
# SALVA STORICO
# ----------------------------
with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in history.items():
        writer.writerow([k, v])

# ----------------------------
# MIGLIORE SCELTA
# ----------------------------
best = max(results, key=lambda x: x["score"])

def advice(score):
    if score > 9:
        return "🟢 PRENOTA SUBITO (prezzi in salita)"
    elif score > 7:
        return "🟡 MONITORA ANCORA"
    else:
        return "🔴 NON URGENTE"

# ----------------------------
# OUTPUT PULITO
# ----------------------------
msg = "🎆 CAPODANNO TRAVEL RADAR PRO 2026/2027\n\n"

msg += f"🏆 MIGLIOR SCELTA:\n"
msg += f"{best['dest']} ({best['route']})\n"
msg += f"💰 Prezzo stimato: {best['price']} €\n"
msg += f"⭐ Score: {round(best['score'],2)}\n"
msg += f"🧭 Consiglio: {advice(best['score'])}\n\n"

msg += "✈️ MIGLIORI OPZIONI PER AEROPORTO:\n"

for o in airports:
    msg += f"\n📍 Da {o}:\n"

    subset = [r for r in results if r["route"].startswith(o + "->")]
    subset = sorted(subset, key=lambda x: x["score"], reverse=True)[:3]

    for r in subset:
        msg += f"- {r['dest']}: {r['price']} € | {r['trend']} | score {round(r['score'],1)}\n"

msg += "\n🏆 TOP 5 COMPLESSIVO:\n"

top5 = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

for r in top5:
    msg += f"- {r['dest']} ({r['route']}): {r['price']} € | score {round(r['score'],1)}\n"

msg += "\n✈️ Nota: Capodanno = prezzi in aumento rapido, monitorare spesso 📈"

send(msg)
