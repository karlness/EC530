from fastapi import APIRouter, HTTPException, status
from ..models import User

router = APIRouter()

fake_users_db = {}

@router.get("/", response_model=list[User])
def get_all_users():
    return list(fake_users_db.values())

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    if user.user_id in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User ID {user.user_id} already exists"
        )
    fake_users_db[user.user_id] = user
    return user