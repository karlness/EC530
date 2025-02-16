from fastapi import FastAPI
from .routes import user, house, rooms, devices

app = FastAPI()
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(house.router, prefix="/houses", tags=["Houses"])
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
app.include_router(devices.router, prefix="/devices", tags=["Devices"])


@app.get("/")
def read_root():
    return {"message": " The Smart Home API is up and running!"}