from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
  model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

def embed_documents(documents: str) -> list[list[float]]:
  return embedding_model.embed_documents(documents)

def embed_query(text: str) -> list[float]:
  return embedding_model.embed_query(text)
