from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db, get_redis
from dataset import Database
from redis import Redis

app = FastAPI()
db: Database = get_db()
r: Redis = get_redis()

class User(BaseModel):
    name: str
    email: str
    password: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/users/{user_id}")
def read_user(user_id: int, q: str = None):
    r.incr(f"hits_{user_id}")
    user = db.get_table("users").find_one(id=user_id)
    if user:
        return user
    else:
        return {"error": "User not found"}


@app.post("/users/", status_code=201)
def create_user(user: User):
    db.get_table("users").insert(user.dict())
    return user


@app.get("/users/")
def read_users():
    users = list(db.get_table("users").all())
    return users

@app.get("/users/{user_id}/hits")
def read_user_hits(user_id: int):
    hits = r.get(f"hits_{user_id}")
    return {"hits": hits}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)