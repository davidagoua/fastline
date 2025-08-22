from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db, get_redis
from dataset import Database
from redis import Redis

app = FastAPI()
db: Database = get_db()
r: Redis = get_redis()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    r.incr(f"hits_{item_id}")
    item = db.get_table("items").find_one(id=item_id)
    if item:
        return item
    else:
        return {"error": "Item not found"}


@app.post("/items/", status_code=201)
def create_item(item: Item):
    db.get_table("items").insert(item.dict())
    return item


@app.get("/items/")
def read_items():
    items = list(db.get_table("items").all())
    return items

@app.get("/items/{item_id}/hits")
def read_item_hits(item_id: int):
    hits = r.get(f"hits_{item_id}")
    return {"hits": hits}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)