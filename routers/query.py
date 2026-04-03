from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import APIRouter
from models.query_model import QueryModel
from modules.llm import generate, stream
from modules.database import search
import json

query_router = APIRouter(prefix='/query')

@query_router.post('/')
async def query(data: QueryModel):
  context = search(data.query)
  response = await generate(query=data.query, context=context)
  return JSONResponse({ "response": response })

@query_router.post('/stream')
async def stream_response(data: QueryModel):
  context = search(data.query)  
  return StreamingResponse(
    stream(query=data.query, context=context), 200, media_type='text/event-stream')
