import signal

from random import randint

import geopy.distance
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uuid

signal.signal(signal.SIGUSR1, lambda: None)
app = FastAPI()

origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins)


class User:
    def __init__(self, desc: str):
        self.id = uuid.uuid4()
        self.desc = desc
        self.lat = None
        self.lon = None
        self.code = randint(0, 100000)


class Game:
    def __init__(self, u1, u2):
        self.id = uuid.uuid4()
        self.user1 = u1
        self.user2 = u2


users_queue = {}
paired_queue = {}
users = {}


@app.post("/start", status_code=200)
def start_game(description: str):
    user = User(description)
    users_queue[str(user.id)] = user
    return {'user_id': str(user.id), 'user_code': str(user.code)}


@app.post("/ask_game", status_code=200)
def ask_game(user_id: str):
    if user_id in paired_queue.keys():
        user1 = paired_queue.pop(str(user_id))
        users[str(user1.id)] = user1
        return {'found': True, 'user_id': str(user1.id), 'desc': str(user1.desc), 'user_code': str(user1.code)}

    if len(users_queue) >= 2:
        user1 = users_queue.pop(user_id)
        user2 = users_queue.pop(list(users_queue.keys())[0])
        users[str(user2.id)] = user2
        paired_queue[str(user2.id)] = user1
        return {'found': True, 'user_id': str(user2.id), 'desc': str(user2.desc)}

    return {'found': False}


@app.post("/update_info", status_code=200)
def update_info(user_id: str, lat: str, lon: str):
    user = users[user_id]
    user.lat = lat
    user.lon = lon
    return {'status': 'OK'}


@app.post("/get_info", status_code=200)
def get_info(user_id: str):
    user = users[user_id]
    return {'lat': user.lat, 'lon': user.lon}


@app.post("/get_distance", status_code=200)
def get_distance(user1_id: str, user2_id: str):
    user1 = users[user1_id]
    user2 = users[user2_id]
    coords_1 = (float(user1.lat), float(user1.lon))
    coords_2 = (float(user2.lat), float(user2.lon))
    return {'dist': geopy.distance.geodesic(coords_1, coords_2).m}
