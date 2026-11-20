from datetime import date

import requests
from flask import Flask, render_template, abort

app = Flask(__name__)

# De URL van je API op kdg-json-server (zonder / op het einde).
# Vervang dit door je eigen URL, bv. die je in Postman gebruikt.
API_URL = "https://VUL-HIER-JE-KDG-JSON-SERVER-URL-IN"


def haal_op(pad):
    """Roept de API aan en geeft de JSON terug.
    Bestaat het niet (404), dan tonen we onze eigen 404-pagina.
    Bij een andere fout tonen we een foutpagina (503)."""
    try:
        response = requests.get(API_URL + pad, timeout=10)
    except requests.exceptions.RequestException:
        abort(503)

    if response.status_code == 404:
        abort(404)
    if response.status_code != 200:
        abort(503)
    return response.json()


def vakken_per_id():
    """Maakt een dictionary {vak_id: vak}, zodat we snel de vaknaam vinden."""
    vakken = haal_op("/vakken")
    return {str(vak["id"]): vak for vak in vakken}


def is_te_laat(taak):
    """True als de deadline voorbij is en de taak nog niet klaar is."""
    deadline = date.fromisoformat(taak["deadline"])
    return deadline < date.today() and not taak["klaar"]


@app.route("/")
def overzicht():
    taken = haal_op("/taken")
    vakken = vakken_per_id()

    taken = sorted(taken, key=lambda taak: taak["deadline"])
    for taak in taken:
        taak["vak"] = vakken.get(str(taak["vak_id"]))
        taak["te_laat"] = is_te_laat(taak)

    return render_template("index.html", taken=taken)


@app.route("/taken/<int:taak_id>")
def taak_detail(taak_id):
    taak = haal_op(f"/taken/{taak_id}")
    vakken = vakken_per_id()

    taak["vak"] = vakken.get(str(taak["vak_id"]))
    taak["te_laat"] = is_te_laat(taak)

    return render_template("taak.html", taak=taak)


@app.route("/vakken/<int:vak_id>")
def vak_detail(vak_id):
    vak = haal_op(f"/vakken/{vak_id}")
    alle_taken = haal_op("/taken")

    taken = [taak for taak in alle_taken if str(taak["vak_id"]) == str(vak_id)]
    taken = sorted(taken, key=lambda taak: taak["deadline"])
    for taak in taken:
        taak["te_laat"] = is_te_laat(taak)

    return render_template("vak.html", vak=vak, taken=taken)


@app.errorhandler(404)
def niet_gevonden(error):
    return render_template("404.html"), 404


@app.errorhandler(503)
def api_fout(error):
    return render_template("fout.html"), 503


if __name__ == "__main__":
    app.run(debug=True)
