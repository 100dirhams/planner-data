# Planner – Opdracht 3a

Flask-site die mijn taken en deadlines toont. De data (`db.json`) staat in een publieke
GitHub-repository en wordt via kdg-json-server als RESTful API aangeboden.

## Endpoints van de API
- `/taken` – alle taken
- `/taken/1` – één taak
- `/vakken` – alle vakken

## Pagina's van de site
- `/` – alle taken, gesorteerd op deadline, met de vaknaam
- `/taken/<id>` – detail van één taak
- `/vakken/<id>` – enkel de taken van dat vak
- Taken over hun deadline die niet klaar zijn, worden rood gemarkeerd
- Een onbestaand id geeft een nette 404-pagina

## Starten
```
pip install flask requests
python app.py
```
Open dan http://127.0.0.1:5000

## Data uit Canvas halen
`canvas_import.py` haalt mijn vakken en opdrachten (met deadline) uit de Canvas API en
schrijft ze naar `db.json`. Het token staat in `canvas_token.txt`, dat niet in git zit.
```
python canvas_import.py
git add db.json && git commit -m "Taken bijgewerkt" && git push
```

## Bronvermelding
- Canvas LMS REST API: https://canvas.instructure.com/doc/api/
- Flask-documentatie: https://flask.palletsprojects.com
- Requests-documentatie: https://requests.readthedocs.io
- kdg-json-server en cursusmateriaal Informatica voor IoT 2 (KdG)
- Code geschreven met hulp van Claude (Anthropic)
