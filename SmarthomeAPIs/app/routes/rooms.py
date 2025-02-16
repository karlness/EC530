from fastapi import APIRouter
from ..models import Room

router = APIRouter()

fake_rooms_db = []

@router.get("/")
def get_all_rooms():
    return fake_rooms_db

@router.post("/")
def create_room(room: Room):
    fake_rooms_db.append(room)
    return room