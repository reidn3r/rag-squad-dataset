from fastapi import FastAPI
from routers.health_check import health_router
from routers.query import query_router

app = FastAPI()

app.include_router(health_router)
app.include_router(query_router)