from pydantic import BaseModel, Field, EmailStr
from typing import List

class User(BaseModel):
    user_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    email: EmailStr

class Device(BaseModel):
    device_id: str = Field(..., min_length=1)
    device_type: str = Field(..., min_length=1, max_length=50)
    status: str = Field(
        ...,
        pattern="^(on|off|idle)$",
        description="Must be 'on', 'off', or 'idle'"
    )

class Room(BaseModel):
    room_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    devices: List[Device] = []

class House(BaseModel):
    house_id: str = Field(..., min_length=1)
    address: str = Field(..., min_length=5)
    owner_id: str = Field(..., description="user_id of the house owner")
    rooms: List[Room] = []
