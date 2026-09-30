# ⚔️ 1v1 MCQ Battle – Real-Time Quiz Competition Platform

Python · Django · Django Channels (WebSockets) · Django REST Framework · HTML/CSS/JS

## Run
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations quiz
python manage.py migrate
python manage.py seed_questions
python manage.py createsuperuser                      # optional (admin at /admin/)
python manage.py runserver
```
Open http://127.0.0.1:8000 in two different browsers (or one normal + one incognito),
register two users, create a room in one and join with the code in the other.

## Features
- Register / login (Django auth)
- Room code based 1v1 matchmaking
- Server-authoritative game loop: 10 questions, 15 s timer, speed-bonus scoring
- Live score updates over WebSockets; forfeit if a player leaves
- Match history + leaderboard saved in DB
- REST APIs: `/api/questions/`, `/api/leaderboard/`, `/api/matches/`
- Admin panel to add/edit questions

## Structure
- `quiz/consumers.py` – WebSocket game engine (the core of the project)
- `quiz/models.py` – Question, Match
- `quiz/views.py` – pages + DRF API
- `quiz/templates/quiz/battle.html` – battle UI (vanilla JS WebSocket client)

## Notes
- Uses in-memory channel layer + room state → run ONE server process. For production use `channels-redis`.
- Switch to MySQL in `config/settings.py` (commented block).
