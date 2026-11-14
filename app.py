import os
import requests
from flask import Flask, request, jsonify

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELL = "openai/gpt-oss-20b"
GROQ_KEY = os.environ.get("GROQ_API_KEY")

SALON_INFOS = """
Du bist der freundliche Chat-Assistent von Salon Bella, einem Friseursalon in Geislingen.
Antworte immer kurz, freundlich und auf Deutsch.
Öffnungszeiten: Dienstag bis Freitag 9 bis 18 Uhr, Samstag 8 bis 14 Uhr, Sonntag und Montag geschlossen.
Preise: Herrenschnitt 25 Euro, Damenschnitt ab 40 Euro, Färben ab 60 Euro, Kinderschnitt 15 Euro.
Termine: Kunden können unter 07331 123456 anrufen oder hier Name, Wunschtag und Uhrzeit nennen.
Adresse: Musterstraße 1, 73312 Geislingen.
Wenn du etwas nicht weißt, sag ehrlich, dass der Salon sich darum kümmert.
"""

app = Flask(__name__)

SEITE = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Salon Bella</title>
<style>
body { margin: 0; font-family: Arial, sans-serif; background: #f7f3ef; color: #333; }
header { background: #8b5e3c; color: white; padding: 40px 20px; text-align: center; }
header h1 { margin: 0; font-size: 40px; }
main { max-width: 700px; margin: 30px auto; padding: 0 20px; }
#knopf { position: fixed; bottom: 20px; right: 20px; background: #8b5e3c; color: white; border: none; border-radius: 30px; padding: 15px 25px; font-size: 18px; cursor: pointer; }
#fenster { display: none; position: fixed; bottom: 80px; right: 20px; width: 330px; max-width: calc(100% - 40px); height: 450px; background: white; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.3); flex-direction: column; overflow: hidden; }
#kopf { background: #8b5e3c; color: white; padding: 12px; font-weight: bold; }
#nachrichten { flex: 1; padding: 10px; overflow-y: auto; }
.bot { background: #eee; padding: 8px 12px; border-radius: 10px; margin: 6px 40px 6px 0; }
.kunde { background: #8b5e3c; color: white; padding: 8px 12px; border-radius: 10px; margin: 6px 0 6px 40px; text-align: right; }
#eingabe { display: flex; border-top: 1px solid #ddd; }
#text { flex: 1; border: none; padding: 12px; font-size: 15px; }
#senden { background: #8b5e3c; color: white; border: none; padding: 0 16px; cursor: pointer; }
</style>
</head>
<body>
<header>
<h1>Salon Bella</h1>
<p>Ihr Friseur in Geislingen</p>
</header>
<main>
<h2>Willkommen</h2>
<p>Schnitt, Farbe und Styling mit Herz. Fragen? Einfach unten rechts auf Chat klicken.</p>
</main>
<button id="knopf" onclick="umschalten()">Chat</button>
<div id="fenster">
<div id="kopf">Salon Bella Assistent</div>
<div id="nachrichten"><div class="bot">Hallo! Wie kann ich Ihnen helfen?</div></div>
<div id="eingabe">
<input id="text" placeholder="Ihre Frage..." onkeydown="if(event.key==='Enter'){senden()}">
<button id="senden" onclick="senden()">Senden</button>
</div>
</div>
<script>
let verlauf = [];
function umschalten() {
  const f = document.getElementById("fenster");
  f.style.display = f.style.display === "flex" ? "none" : "flex";
}
function zeige(text, klasse) {
  const n = document.getElementById("nachrichten");
  const d = document.createElement("div");
  d.className = klasse;
  d.textContent = text;
  n.appendChild(d);
  n.scrollTop = n.scrollHeight;
}
async function senden() {
  const feld = document.getElementById("text");
  const frage = feld.value.trim();
  if (!frage) return;
  feld.value = "";
  zeige(frage, "kunde");
  verlauf.push({role: "user", content: frage});
  zeige("...", "bot");
  const r = await fetch("/chat", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({verlauf: verlauf})});
  const daten = await r.json();
  const n = document.getElementById("nachrichten");
  n.removeChild(n.lastChild);
  zeige(daten.antwort, "bot");
  verlauf.push({role: "assistant", content: daten.antwort});
}
</script>
</body>
</html>
"""

@app.route("/")
def startseite():
    return SEITE

@app.route("/chat", methods=["POST"])
def chat():
    verlauf = request.json.get("verlauf", [])[-20:]
    nachrichten = [{"role": "system", "content": SALON_INFOS}] + verlauf
    try:
        antwort = requests.post(GROQ_URL, headers={
            "Authorization": "Bearer " + str(GROQ_KEY),
            "Content-Type": "application/json"
        }, json={
            "model": GROQ_MODELL,
            "messages": nachrichten
        }, timeout=60)
        text = antwort.json()["choices"][0]["message"]["content"]
    except Exception as fehler:
        text = "Entschuldigung, gerade gibt es ein technisches Problem."
        print("Fehler:", fehler)
    return jsonify({"antwort": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
