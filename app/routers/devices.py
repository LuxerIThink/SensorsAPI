from typing import Annotated
from fastapi import APIRouter, Depends
from app.internal.authentication import authorize
from tortoise.transactions import in_transaction
from app.models import Device
from app.pydantics.device import (
    DeviceOutPydantic,
    DeviceInPydantic,
    DevicesOutPydantic,
    DeviceInPydanticAllOptional,
)

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.get("/", response_model=DevicesOutPydantic)
async def get_device(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str = "",
    name: str = "",
    is_shared: bool | None = None,
):
    parameters = {
        "uuid": uuid,
        "name__contains": name,
        "is_shared": is_shared,
    }
    filtered_parameters = {key: value for key, value in parameters.items() if value}
    return await Device.filter(user_id=user_id, **filtered_parameters)


@router.post("/", response_model=DeviceOutPydantic)
async def create_device(
    user_id: Annotated[dict, Depends(authorize)], device: DeviceInPydantic
):
    return await Device.create(**device.model_dump(), user_id=user_id)


@router.put("/{uuid}", response_model=DeviceOutPydantic)
async def edit_device(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str,
    device_in: DeviceInPydantic,
):
    device_dict = device_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        device = await Device.get(uuid=uuid, user_id=user_id)
        await device.update_from_dict(device_dict).save(
            update_fields=device_dict.keys()
        )
        return device


@router.patch("/{uuid}", response_model=DeviceOutPydantic)
async def edit_partially_device(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str,
    device_in: DeviceInPydanticAllOptional,
):
    device_dict = device_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        device = await Device.get(uuid=uuid, user_id=user_id)
        await device.update_from_dict(device_dict).save(
            update_fields=device_dict.keys()
        )
        return device


@router.delete("/{uuid}", response_model=DeviceOutPydantic)
async def remove_device(user_id: Annotated[dict, Depends(authorize)], uuid: str):
    async with in_transaction():
        device = await Device.get(uuid=uuid, user_id=user_id)
        await device.delete()
        return device
