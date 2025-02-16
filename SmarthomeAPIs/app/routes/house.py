from fastapi import APIRouter
from ..models import House

router = APIRouter()

fake_houses_db = []

@router.get("/")
def get_all_houses():
    return fake_houses_db

@router.get("/{house_id}")
def get_house(house_id: str):
    for h in fake_houses_db:
        if h.house_id == house_id:
            return h
    return {"error": "House not found"}

@router.post("/")
def create_house(house: House):
    fake_houses_db.append(house)
    return house