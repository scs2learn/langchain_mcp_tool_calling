from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
import os
from utils.csv_utils import load_users_from_csv, save_users_to_csv

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/users.csv')


class User(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    dob: str
    address_1: str
    address_2: str
    city: str
    state: str
    zip: str
    phone: str
    email: str


def get_users():
    return load_users_from_csv(CSV_FILE_PATH)


def get_user(user_id: int):
    print(f"Incoming user_id : {user_id}")
    users = load_users_from_csv(CSV_FILE_PATH)
    print(users)
    user = next((user for user in users if int(user['user_id']) == user_id), None)
    print(user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def add_user(new_user: dict):
    users = load_users_from_csv(CSV_FILE_PATH)
    if any(int(user['user_id']) == int(new_user['user_id']) for user in users):
        raise HTTPException(status_code=400, detail="User ID already exists")
    users.append(new_user)
    save_users_to_csv(CSV_FILE_PATH, users)
    return new_user


def delete_user(user_id: int):
    users = load_users_from_csv(CSV_FILE_PATH)
    new_users = [user for user in users if int(user['user_id']) != user_id]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail="User not found")
    save_users_to_csv(CSV_FILE_PATH, new_users)
    return {"detail": "User deleted"}


def update_user(updated_user: dict):
    users = load_users_from_csv(CSV_FILE_PATH)
    for index, user in enumerate(users):
        if int(user['user_id']) == int(updated_user['user_id']):
            users[index] = updated_user
            save_users_to_csv(CSV_FILE_PATH, users)
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")
