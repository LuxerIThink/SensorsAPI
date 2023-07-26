from typing import Annotated
from argon2.exceptions import VerifyMismatchError
from jose import jwt

from api.models import User
from api.startup.security import password_hasher, oauth2_scheme, salt
from fastapi import HTTPException, Depends


async def get_token(username, password):
    user = await authenticate_user(username, password)
    token_data = {"email": user.email}
    token = jwt.encode(token_data, salt, algorithm="HS256")
    json = {"access_token": token, "token_type": "bearer"}
    return json


async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        raise HTTPException(status_code=401, detail="User not exist")
    try:
        password_hasher.verify(user.password, password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid password")
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    decoded_json = jwt.decode(token, salt, algorithms=["HS256"])
    user = await User.get(email=decoded_json["email"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user