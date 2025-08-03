from typing import List, Dict
import csv
import os


def load_users_from_csv(file_path: str) -> List[Dict[str, str]]:
    users: List[Dict[str, str]] = []
    if not os.path.exists(file_path):
        return users
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            return users
        for row in reader:
            if isinstance(row, dict):
                users.append(row)
    return users


def save_users_to_csv(file_path: str, users: List[Dict[str, str]]):
    fieldnames = users[0].keys() if users else [
        "user_id", "first_name", "last_name", "dob", "address_1", "address_2",
        "city", "state", "zip", "phone", "email"
    ]
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)
