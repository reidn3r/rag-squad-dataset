from templates.prompts import read_reranking_prompt
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from models.query_model import QueryRetrievalModel
from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails
import logging
import json
import os

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

config = RailsConfig.from_path("./config")

llm = ChatOpenAI(
  api_key=os.getenv("LLM_API_KEY"),      
  base_url=os.getenv("LLM_BASE_URL"),
  model=os.getenv("LLM_MODEL"),
  temperature=0.8,
  streaming=True
)

rails = LLMRails(config)

async def generate(
  query: str,
  context: list[QueryRetrievalModel]
):
  context = await rerank(query, context)

  response = await rails.generate_async(
    messages=[
      { "role": "system", "content": f"[CONTEXTO]\n{format_rag_context(context)}"},
      { "role": "user", "content": query },
    ],
  )
  
  return response["content"]

async def stream(
    query: str,
    context: list[QueryRetrievalModel]
):
    context = await rerank(query, context)
    messages = [
      {"role": "system", "content": f"[CONTEXTO]\n{format_rag_context(context)}"},
      {"role": "user", "content": query},
    ]

    async for chunk in rails.stream_async(
      messages=messages,
      options={"log": {"activated_rails": True}},
      ):
      yield f"data: {chunk}\n\n"
    yield "data: [DONE]\n\n"
    
async def rerank(query: str, context: list[QueryRetrievalModel]) -> list[QueryRetrievalModel]:
  prompt = read_reranking_prompt()
  parser = StrOutputParser()

  rag_context = format_rag_context(context)

  chain = prompt | llm | parser
  result = await chain.ainvoke({
    "context": rag_context,
    "input": query,
  })

  indexes = json.loads(result)
  return [context[i] for i in indexes]


def format_rag_context(context: list[QueryRetrievalModel]) -> str:
  return "\n\n".join([
    f"[{i}] {c['text']}" for i, c in enumerate(context)
  ])