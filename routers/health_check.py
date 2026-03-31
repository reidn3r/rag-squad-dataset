from fastapi import APIRouter

health_router = APIRouter(prefix='/health')

@health_router.get('/')
def ping():
  return "pong"