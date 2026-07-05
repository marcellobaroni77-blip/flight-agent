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
# DESTINAZIONI EUROPEE (CAPODANNO)
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
# PREZZO SIMULATO
# ----------------------------
def price_model(origin, dest):
    airport_factor = {
        "BLQ": 70, "VRN": 75, "VCE": 80, "BGY": 65, "MXP": 85
    }

    base = airport_factor.get(origin, 75)
    base += destinations[dest]["base"]

    return base + random.randint(30, 140)

# ----------------------------
# STORICO
# ----------------------------
history = {}

if os.path.exists(FILE):
    with open(FILE, "r") as f:
        for row in csv.reader(f):
            history[row[0]] = int(row[1])

results = []

# ----------------------------
# ANALISI
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

# salva storico
with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in history.items():
        writer.writerow([k, v])

# ----------------------------
# ORDINA RISULTATI
# ----------------------------
results_sorted = sorted(results, key=lambda x: x["score"], reverse=True)

best = results_sorted[0]

# ----------------------------
# OUTPUT SEMPLICE E SICURO
# ----------------------------
msg = "🎆 CAPODANNO TRAVEL RADAR 2026/2027\n\n"

msg += f"🏆 MIGLIOR SCELTA:\n"
msg += f"{best['dest']} ({best['route']})\n"
msg += f"💰 Prezzo stimato: {best['price']} €\n"
msg += f"⭐ Score: {round(best['score'],2)}\n\n"

msg += "✈️ TOP 5 OPZIONI:\n"

for r in results_sorted[:5]:
    msg += f"- {r['dest']} ({r['route']}): {r['price']} € | score {round(r['score'],1)}\n"

msg += "\n🧭 Consiglio: Capodanno = prezzi alti, controlla spesso 📈"

send(msg)
