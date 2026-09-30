"""
Real-time 1v1 battle engine (Django Channels).

Flow: 2 players join the same room code -> server runs the whole game loop
(questions, timer, scoring) so clients can't cheat -> result saved to DB.
Room state lives in memory (ROOMS) -> run a single server process, or move it to Redis.
"""
import asyncio
import random
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer

from .models import Match, Question

ROOMS = {}
QUESTIONS_PER_MATCH = 10
TIME_PER_QUESTION = 15  # seconds
BASE_POINTS, MAX_SPEED_BONUS = 10, 5


@database_sync_to_async
def load_questions():
    qs = list(Question.objects.all())
    random.shuffle(qs)
    return [{"id": q.id, "text": q.text, "correct": q.correct,
             "options": {"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d}}
            for q in qs[:QUESTIONS_PER_MATCH]]


@database_sync_to_async
def save_match(code, p1, p2, winner_id):
    Match.objects.create(room_code=code, player1_id=p1["id"], player2_id=p2["id"],
                         score1=p1["score"], score2=p2["score"], winner_id=winner_id)


def players_payload(room):
    return [{"id": uid, "name": p["name"], "score": p["score"], "answer": p["answer"]}
            for uid, p in room["players"].items()]


async def broadcast(code, payload):
    await get_channel_layer().group_send(f"room_{code}", {"type": "broadcast", "payload": payload})


async def finish(code, forfeit_by=None):
    room = ROOMS.get(code)
    if not room or room["finished"]:
        return
    room["finished"] = True
    ps = list(room["players"].items())
    winner = None
    if forfeit_by:
        winner = next(uid for uid, _ in ps if uid != forfeit_by)
    elif ps[0][1]["score"] != ps[1][1]["score"]:
        winner = max(ps, key=lambda x: x[1]["score"])[0]
    p1, p2 = ({"id": uid, **p} for uid, p in ps)
    await save_match(code, p1, p2, winner)
    await broadcast(code, {"type": "finished", "players": players_payload(room),
                           "winner": winner, "forfeit": bool(forfeit_by)})
    ROOMS.pop(code, None)


async def run_game(code):
    room = ROOMS[code]
    questions = await load_questions()
    if not questions:
        await broadcast(code, {"type": "error", "message": "No questions in DB. Run: python manage.py seed_questions"})
        ROOMS.pop(code, None)
        return
    await broadcast(code, {"type": "start"})
    await asyncio.sleep(3)

    for i, q in enumerate(questions):
        for p in room["players"].values():
            p["answer"], p["elapsed"] = None, TIME_PER_QUESTION
        room["current"] = i
        room["event"].clear()
        room["q_started"] = time.monotonic()
        await broadcast(code, {"type": "question", "index": i + 1, "total": len(questions),
                               "text": q["text"], "options": q["options"], "time": TIME_PER_QUESTION})
        try:
            await asyncio.wait_for(room["event"].wait(), TIME_PER_QUESTION)  # both answered -> move on
        except asyncio.TimeoutError:
            pass

        for p in room["players"].values():
            if p["answer"] == q["correct"]:
                bonus = int(MAX_SPEED_BONUS * max(0, 1 - p["elapsed"] / TIME_PER_QUESTION))
                p["score"] += BASE_POINTS + bonus
        await broadcast(code, {"type": "reveal", "correct": q["correct"], "players": players_payload(room)})
        await asyncio.sleep(3)

    await finish(code)


class BattleConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return await self.close()
        self.code = self.scope["url_route"]["kwargs"]["code"].upper()
        self.group = f"room_{self.code}"
        room = ROOMS.setdefault(self.code, {"players": {}, "started": False, "finished": False,
                                            "current": -1, "event": asyncio.Event(), "task": None})
        await self.accept()
        if self.user.id not in room["players"] and (len(room["players"]) >= 2 or room["started"]):
            await self.send_json({"type": "error", "message": "Room is full or already started."})
            return await self.close()

        self.joined = True
        await self.channel_layer.group_add(self.group, self.channel_name)
        room["players"].setdefault(self.user.id, {"name": self.user.username, "score": 0,
                                                  "answer": None, "elapsed": TIME_PER_QUESTION})
        await self.send_json({"type": "you", "id": self.user.id})
        await broadcast(self.code, {"type": "lobby", "players": players_payload(room)})

        if len(room["players"]) == 2 and not room["started"]:
            room["started"] = True
            room["task"] = asyncio.create_task(run_game(self.code))

    async def receive_json(self, content):
        room = ROOMS.get(self.code)
        if not room or content.get("type") != "answer" or room["current"] < 0:
            return
        me = room["players"].get(self.user.id)
        choice = str(content.get("choice", "")).upper()
        if me and me["answer"] is None and choice in "ABCD" and choice:
            me["answer"] = choice
            me["elapsed"] = time.monotonic() - room["q_started"]
            if all(p["answer"] for p in room["players"].values()):
                room["event"].set()

    async def disconnect(self, code):
        if not getattr(self, "joined", False):
            return
        await self.channel_layer.group_discard(self.group, self.channel_name)
        room = ROOMS.get(self.code)
        if not room or room["finished"]:
            return
        if room["started"]:               # leaving mid-game = forfeit
            if room["task"]:
                room["task"].cancel()
            await finish(self.code, forfeit_by=self.user.id)
        else:                             # left the lobby
            room["players"].pop(self.user.id, None)
            if not room["players"]:
                ROOMS.pop(self.code, None)
            else:
                await broadcast(self.code, {"type": "lobby", "players": players_payload(room)})

    async def broadcast(self, event):
        await self.send_json(event["payload"])
