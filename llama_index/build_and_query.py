"""
Recreates LlamaIndex tutorial to build and query an index.
"""

from llama_index import VectorStoreIndex, SimpleDirectoryReader
import os

os.getenv('OPENAI_API_KEY')
documents = SimpleDirectoryReader('data').load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
print(response)
