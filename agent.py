import requests

# === INSERISCI QUI I TUOI DATI ===
TOKEN = "8974112249:AAH6hvCqvRGpy0UCzGf3csqUPDko7pyY2e4"
CHAT_ID = "8618378256"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# TEST AGENTE
message = "🤖 Agente attivo: funziono correttamente!"

send_message(message)
