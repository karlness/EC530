from fastapi import APIRouter
from ..models import Device

router = APIRouter()

fake_devices_db = []

@router.get("/")
def get_all_devices():
    return fake_devices_db

@router.get("/{device_id}")
def get_device(device_id: str):
    for d in fake_devices_db:
        if d.device_id == device_id:
            return d
    return {"error": "Device not found"}

@router.post("/")
def create_device(device: Device):
    fake_devices_db.append(device)
    return device
