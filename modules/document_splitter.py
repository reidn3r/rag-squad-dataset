from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
  chunk_size=300,
  chunk_overlap=50
)

def split_document(context: str) -> list[str]:
  return splitter.create_documents([context])