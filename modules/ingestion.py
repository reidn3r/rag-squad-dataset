from modules.database import collection_exists, create_collection
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from datasets import DatasetDict

from modules.document_splitter import split_document
from modules.vector import embed_documents

from dotenv import load_dotenv
import uuid
import os

load_dotenv()

QDRANT_HOST = os.getenv('QDRANT_URI')
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION')
DATASET_NAME = os.getenv('DATASET_NAME')
VECTOR_SIZE = 768

client = QdrantClient(url=QDRANT_HOST)

def run(
  dataset: DatasetDict,
  split: str = "train",
  text_field: str = "context",
  batch_size: int = 256,
  upsert_batch_size: int = 1000,
  max_records: int = -1,
  collection_name: str = None
) -> dict:

  if collection_name is None:
    collection_name = QDRANT_COLLECTION_NAME
  
  if not collection_exists(collection_name):
    create_collection(collection_name,  VECTOR_SIZE)
  
  seen = set()
  contexts_batch = []
  all_points = []
  processed = 0
  total_chunks = 0
  
  dataset_split = dataset[split]
  for row in dataset_split:
    if max_records != -1 and processed >= max_records:
      break
    
    ctx = row[text_field]
    
    if ctx in seen:
      continue
    
    seen.add(ctx)
    contexts_batch.append(ctx)
    processed += 1
    
    if len(contexts_batch) >= batch_size:
      points = _process_batch(contexts_batch)
      all_points.extend(points)
      contexts_batch = []
    
    if len(all_points) >= upsert_batch_size:
      client.upsert(
        collection_name=collection_name,
        points=all_points
      )
      all_points = []

  if contexts_batch:
    all_points.extend(_process_batch(contexts_batch))
  
  if all_points:
    client.upsert(
      collection_name=collection_name,
      points=all_points
    )
  
  return {
    'points_inserted': len(all_points),
    'chunks_created': total_chunks,
    'documents_processed': processed
  }

def _process_batch(contexts):
  total_chunks=0
  chunks, payloads = [], []
  
  for ctx in contexts:
    docs = split_document(ctx)
    for doc in docs:
      chunks.append(doc.page_content)
      payloads.append({
        "text": doc.page_content,
        "source": DATASET_NAME,
      })
      total_chunks += 1
  
  if not chunks:
    return []
  
  embeddings = embed_documents(chunks)
  
  return [
    PointStruct(
      id=str(uuid.uuid4()),
      vector=e,
      payload=p
    )
    for e, p in zip(embeddings, payloads)
  ]