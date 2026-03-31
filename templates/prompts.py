from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

base_dir = Path(__file__).resolve().parent

def read_system_prompt() -> ChatPromptTemplate:
  sys_prompt_path = base_dir / "../templates/system.md"
  sys_prompt = read(sys_prompt_path)
  return ChatPromptTemplate.from_messages([
    ("system", sys_prompt),
    ("assistant", "[CONTEXTO]\n{context}"),
    ("user", "{input}"),
  ])

def read_reranking_prompt() -> ChatPromptTemplate:
  reranking_prompt_path = base_dir / "../templates/reranking.md"
  reranking_prompt = read(reranking_prompt_path)

  return ChatPromptTemplate.from_messages([
    ("system", reranking_prompt),
    ("system", "[CONTEXTO]\n{context}"),
    ("user", "{input}"),
  ])

def read(path: str) -> str:
  with open(path, 'r', encoding='utf-8') as f:
    return f.read()