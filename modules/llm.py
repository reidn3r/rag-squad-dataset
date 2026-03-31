from templates.prompts import read_reranking_prompt, read_system_prompt
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from models.query_model import QueryRetrievalModel
from dotenv import load_dotenv
import json
import os

load_dotenv()

llm = ChatOpenAI(
  api_key=os.getenv("LLM_API_KEY"),      
  base_url=os.getenv("LLM_BASE_URL"),
  model=os.getenv("LLM_MODEL"),
  temperature=0.8
)

def generate(
  query: str,
  context: list[QueryRetrievalModel]
  ):
  context = rerank(query, context)
  
  prompt = read_system_prompt()
  parser = StrOutputParser()
  
  chain = prompt | llm | parser  
  response = chain.invoke({
    "context": f'[CONTEXTO]\n{context}',
    "input": query,
  })  
  return response

def rerank(query: str, context: list[QueryRetrievalModel]) -> list[QueryRetrievalModel]:
  prompt = read_reranking_prompt()
  parser = StrOutputParser()

  rag_context = format_rag_context(context)

  chain = prompt | llm | parser
  result = chain.invoke({
    "context": rag_context,
    "input": query,
  })

  indexes = json.loads(result)
  return [context[i] for i in indexes]


def format_rag_context(context: list[QueryRetrievalModel]) -> str:
  return "\n\n".join([
    f"[{i}] {c['text']}" for i, c in enumerate(context)
  ])
