from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from modules.vector import embed_query
from dotenv import load_dotenv
import os

load_dotenv()

QDRANT_HOST = os.getenv('QDRANT_URI')
client = QdrantClient(url=QDRANT_HOST)

def create_collection(
  collection_name: str,
  vector_size: int,
  ) -> bool:
    if not collection_exists(collection_name):
      client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
      )
      return True
    return False
  
def collection_exists(
  collection_name: str
) -> bool:
  return client.collection_exists(collection_name)

def search(
  query: str,
  limit: int = 10,
  score_threshold: float = None
) -> list[dict]:
  query_vector = embed_query(query)
  results = client.query_points(
    collection_name=os.getenv('QDRANT_COLLECTION'),
    query=query_vector,
    limit=limit,
    score_threshold=score_threshold
  )

  formatted_results = []
  for point in results.points:
    formatted_results.append({
      "text": point.payload.get("text", ""),
      "score": point.score,
      "source": point.payload.get("source", ""),
    })
  
  return formatted_results