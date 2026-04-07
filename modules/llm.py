from templates.prompts import read_reranking_prompt, read_system_prompt, read_rails_prompt
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from models.query_model import QueryRetrievalModel
from dotenv import load_dotenv
import json
from langchain_core.messages import SystemMessage, HumanMessage
import os

load_dotenv()

llm = ChatOpenAI(
  api_key=os.getenv("LLM_API_KEY"),      
  base_url=os.getenv("LLM_BASE_URL"),
  model=os.getenv("LLM_MODEL"),
  temperature=0.9,
  streaming=True
)

guard = ChatOpenAI(
  api_key=os.getenv("LLM_API_KEY"),
  base_url=os.getenv("LLM_BASE_URL"),
  model="openai/gpt-oss-safeguard-20b",
  temperature=0.0,
)

async def generate(
  query: str,
  context: list[QueryRetrievalModel]
):
  if not await check_safety(query):
    return "Não posso responder a essa pergunta."
  
  prompt = read_system_prompt()
  parser = StrOutputParser()

  context = await rerank(query, context, -1)

  chain = prompt | llm | parser
  response = await chain.ainvoke({
    "context": format_rag_context(context),
    "input": query,
  })

  return response

async def stream(
  query: str,
  context: list[QueryRetrievalModel]
):
  prompt = read_system_prompt()
  context = await rerank(query, context, 2)

  chain = prompt | llm 
  async for chunk in chain.astream({
    "input": query,
    "context": format_rag_context(context)
  }):
    yield f"data: {chunk.content}\n\n"
  yield "data: [DONE]\n\n"
    
async def rerank(query: str, context: list[QueryRetrievalModel], top_k: int = -1) -> list[QueryRetrievalModel]:
  prompt = read_reranking_prompt()
  parser = StrOutputParser()

  rag_context = format_rag_context(context)

  chain = prompt | llm | parser
  result = await chain.ainvoke({
    "context": rag_context,
    "input": query,
  })

  indexes = json.loads(result)
  selected = len(indexes) if top_k == -1 else top_k
  return [context[i] for i in indexes][:selected]

async def check_safety(text: str) -> bool:
  prompt = read_rails_prompt()
  chain = prompt | guard
  
  response = await chain.ainvoke([
    ("input", text)
  ])

  return response.content.strip().upper().startswith("SAFE")

def format_rag_context(context: list[QueryRetrievalModel]) -> str:
  return "\n\n".join([
    f"[{i}] {c['text']}" for i, c in enumerate(context)
  ])