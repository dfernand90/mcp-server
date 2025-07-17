import os
import sys
import logging
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ----------------------- Logging Setup -----------------------
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# ----------------------- Paths & Secrets -----------------------
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(FILE_DIR)))
FOLDER_DIR = os.path.join(BASE_DIR, "folder")
DOCUMENTS_DIR = os.path.join(FILE_DIR, "./tilbud_test/Vigga Bru/01 Underlag")
STORAGE_DIR = "./storage/RAG/pump"

# Load API keys from secrets file
def load_api_keys(filepath):
    keys = {}
    with open(filepath, "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                keys[k.strip()] = v.strip()
    return keys

api_keys = load_api_keys(os.path.join(FOLDER_DIR, "AFRY_openAI_key.txt"))
subscription_key = api_keys.get("AFRY_OPENAI_API_KEY")
subscription_key_bridge = api_keys.get("bridge_OpenAI_key")

# ----------------------- Model Setup -----------------------
api_version = "2024-12-01-preview"
llm = AzureOpenAI(
    model="gpt-4o",
    deployment_name="gpt-4o-3",
    api_key=subscription_key,
    azure_endpoint="https://digital1.openai.azure.com/",
    api_version=api_version,
)
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
"""
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding-ada-002-MSLEARNDC",
    api_key=subscription_key_bridge,
    azure_endpoint="https://mslearndc-resource.cognitiveservices.azure.com/",
    api_version="2023-05-15",
)
"""

# Set global settings for llama-index
Settings.llm = llm
Settings.embed_model = embed_model

# ----------------------- Wrapping Function -----------------------
def run_query(prompt: str) -> str:
    """Loads index (or builds if not present) and queries with user prompt."""
    try:
        # Attempt to load prebuilt index
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
        print("Loaded index from storage.")
    except Exception:
        # If not found, build index from documents
        print("No stored index found. Creating new index from documents...")
        documents = SimpleDirectoryReader(DOCUMENTS_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=STORAGE_DIR)

    # Query the index
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    return response.response.strip()

# ----------------------- Testing Entry Point -----------------------
if __name__ == "__main__":
    prompt = "What is the context about?"
    answer = run_query(prompt)
    print(f"Answer: {answer}")
