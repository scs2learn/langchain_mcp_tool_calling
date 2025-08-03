from fastapi import FastAPI, Request
from api.users import get_users, get_user, add_user, delete_user, update_user

app = FastAPI()


@app.get("/users")
def users():
    return get_users()


@app.get("/users/{user_id}")
def user(user_id: int):
    return get_user(user_id)


@app.post("/users")
async def add_new_user(request: Request):
    data = await request.json()
    return add_user(data)


@app.delete("/users/{user_id}")
def remove_user(user_id: int):
    return delete_user(user_id)


@app.put("/users")
async def modify_user(request: Request):
    data = await request.json()
    return update_user(data)
