"""Haalt mijn vakken en opdrachten uit Canvas en schrijft ze naar db.json.

Gebruik:
    1. Zet je Canvas-token in een bestand canvas_token.txt (naast dit script).
       Dat bestand staat in .gitignore en komt dus NOOIT op GitHub.
    2. Vul hieronder CANVAS_URL in.
    3. python canvas_import.py
    4. Controleer db.json en push: git add db.json && git commit -m "..." && git push
"""

import json
from datetime import datetime
from pathlib import Path

import requests

# Het adres van Canvas van KdG (zonder / op het einde), bv. https://canvas.voorbeeld.be
CANVAS_URL = "https://canvas.kdg.be"

MAP = Path(__file__).parent
TOKEN_BESTAND = MAP / "canvas_token.txt"
DB_BESTAND = MAP / "db.json"


def lees_token():
    if not TOKEN_BESTAND.exists():
        raise SystemExit("Maak eerst canvas_token.txt aan met je Canvas-token erin.")
    return TOKEN_BESTAND.read_text(encoding="utf-8").strip()


def haal_alles_op(pad, token, params=None):
    """Vraagt een lijst op bij de Canvas API en volgt alle pagina's."""
    headers = {"Authorization": f"Bearer {token}"}
    url = CANVAS_URL + "/api/v1" + pad
    resultaat = []
    while url:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code == 401:
            raise SystemExit("Canvas weigert het token (401). Klopt canvas_token.txt nog?")
        response.raise_for_status()
        resultaat.extend(response.json())
        # Canvas geeft de volgende pagina mee in de Link-header
        url = response.links.get("next", {}).get("url")
        params = None  # zitten al in de 'next'-URL
    return resultaat


def naar_datum(canvas_tijd):
    """'2026-11-27T22:59:00Z' -> '2026-11-27' (in onze lokale tijd)."""
    tijd = datetime.fromisoformat(canvas_tijd.replace("Z", "+00:00"))
    return tijd.astimezone().date().isoformat()


def is_ingediend(opdracht):
    inzending = opdracht.get("submission") or {}
    return inzending.get("submitted_at") is not None or inzending.get("workflow_state") == "graded"


def main():
    token = lees_token()

    cursussen = haal_alles_op(
        "/courses", token,
        {"enrollment_state": "active", "include[]": "teachers", "per_page": 100},
    )

    vakken = []
    taken = []
    for cursus in cursussen:
        if "name" not in cursus:  # cursus waar je geen toegang meer toe hebt
            continue

        opdrachten = haal_alles_op(
            f"/courses/{cursus['id']}/assignments", token,
            {"include[]": "submission", "per_page": 100},
        )
        # Zonder deadline hoort een opdracht niet in de planner
        opdrachten = [o for o in opdrachten if o.get("due_at")]
        if not opdrachten:  # vakken zonder taken (bv. info-cursussen) laten we weg
            continue

        vak_id = len(vakken) + 1
        namen = [d["display_name"] for d in cursus.get("teachers", [])]
        docenten = ", ".join(namen[:3]) + (" e.a." if len(namen) > 3 else "")
        vakken.append({"id": vak_id, "naam": cursus["name"], "docent": docenten or "onbekend"})

        for opdracht in opdrachten:
            taken.append({
                "titel": opdracht["name"],
                "vak_id": vak_id,
                "deadline": naar_datum(opdracht["due_at"]),
                "klaar": is_ingediend(opdracht),
            })

    # Taken op deadline sorteren en netjes nummeren vanaf 1
    taken.sort(key=lambda taak: taak["deadline"])
    taken = [{"id": i, **taak} for i, taak in enumerate(taken, start=1)]

    DB_BESTAND.write_text(
        json.dumps({"vakken": vakken, "taken": taken}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Klaar: {len(vakken)} vakken en {len(taken)} taken geschreven naar {DB_BESTAND.name}")


if __name__ == "__main__":
    main()
