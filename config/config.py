from nemoguardrails import LLMRails
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from nemoguardrails.actions import action
from templates.prompts import read_system_prompt
import os

async def init(app: LLMRails):
  llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL"),
    temperature=0.8
  )

  prompt = read_system_prompt()
  parser = StrOutputParser()
  chain = prompt | llm | parser

  @action(name="rag_generate")
  async def rag_generate(context: dict):
    query = context.get("user_message")
    rag_context = context.get("relevant_chunks", "")
    return chain.invoke({
      "context": f"[CONTEXTO]\n{rag_context}",
      "input": query,
    })

  app.register_action(rag_generate)