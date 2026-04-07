from fastapi import FastAPI
from routers.health_check import health_router
from routers.query import query_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_methods=["*"],
  allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(query_router)