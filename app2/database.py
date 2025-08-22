import os
from dataset import connect
from redis import Redis
from functools import lru_cache


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

@lru_cache
def get_db():
    engine = connect(DATABASE_URL)
    return engine


@lru_cache
def get_redis():
    redis = Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, db=0)
    return redis


