import json
import logging
import os

import azure.functions as func
from openai import OpenAI

ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT")
API_KEY = os.environ.get("FOUNDRY_KEY")
DEPLOYMENT = os.environ.get("FOUNDRY_DEPLOYMENT")   

SYSTEM_PROMPT = os.environ.get(
    "FOUNDRY_SYSTEM_PROMPT",
    "Du bist ein hilfsbereiter Assistent. Antworte freundlich und knapp.",
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    if not (ENDPOINT and API_KEY and DEPLOYMENT):
        return _json({"error": "Backend nicht konfiguriert (App-Settings fehlen)."}, 500)

    try:
        body = req.get_json()
    except ValueError:
        return _json({"error": "Ungültiger Request-Body."}, 400)

    user_messages = body.get("messages", [])
    if not isinstance(user_messages, list) or not user_messages:
        return _json({"error": "Feld 'messages' fehlt oder ist leer."}, 400)


    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_messages

    try:
        client = OpenAI(
            base_url=ENDPOINT,
            api_key=API_KEY,
        )
        completion = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
        )
        reply = completion.choices[0].message.content
        return _json({"reply": reply})
    except Exception as e:
        logging.exception("Foundry-Aufruf fehlgeschlagen")
        return _json({"error": "Fehler beim Aufruf des Modells."}, 502)


def _json(payload: dict, status: int = 200) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(payload),
        status_code=status,
        mimetype="application/json",
    )