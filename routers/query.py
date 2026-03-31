from fastapi import APIRouter

from models.query_model import QueryModel
from modules.llm import generate
from modules.database import search

query_router = APIRouter(prefix='/query')

@query_router.post('/')
def query(
  data: QueryModel
):
  context = search(data.query)
  return generate(query=data.query, context=context)
