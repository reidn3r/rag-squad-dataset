from modules import ingestion
from datasets import load_dataset
from dotenv import load_dotenv
import os

load_dotenv()
def run_ingestion():
  ds = load_dataset(os.getenv('HF_DATASET'))

  QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION')
  ingestion.run(ds, collection_name=QDRANT_COLLECTION_NAME, max_records=1_000)

if __name__ == "__main__":
  run_ingestion()