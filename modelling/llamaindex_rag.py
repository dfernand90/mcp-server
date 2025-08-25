import os
import sys
import logging
from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
#from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
)

# ---------------------- Logger Setup ----------------------
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)
    logger.info("🔧 Logger initialized.")
    return logger

# ---------------------- Environment Loader ----------------------
def load_environment(logger):
    load_dotenv()
    env = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
        "AZURE_OPENAI_EMBEDDING_NAME": os.getenv("AZURE_OPENAI_EMBEDDING_NAME"),
    }

    for key, val in env.items():
        if not val:
            logger.error(f"❌ Missing environment variable: {key}")
    return env

# ---------------------- Model Initializer ----------------------
def initialize_models(env, logger):
    try:
        logger.info("🧠 Initializing LLM and embedding models...")
        llm = AzureOpenAI(
            model="gpt-4o",
            deployment_name=env["AZURE_OPENAI_DEPLOYMENT_NAME"],
            api_key=env["AZURE_OPENAI_API_KEY"],
            azure_endpoint=env["AZURE_OPENAI_ENDPOINT"],
            api_version=env["AZURE_OPENAI_API_VERSION"],
        )
        embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        Settings.llm = llm
        Settings.embed_model = embed_model
        return llm, embed_model
    except Exception as e:
        logger.error(f"❌ Failed to initialize models: {e}")
        raise

# ---------------------- Index Manager ----------------------
def load_or_create_index(persist_dir, documents_dir, logger):
    try:
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        logger.info("📦 Loaded index from storage.")
    except Exception:
        logger.warning("⚠️ Storage not found. Creating new index...")
        documents = SimpleDirectoryReader(documents_dir).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
        logger.info("✅ New index created and persisted.")
    return index.as_query_engine()

# ---------------------- Query Engine ----------------------
def send_query(query_engine, prompt, logger):
    response = query_engine.query(prompt)
    logger.info(f"📝 Response: {response.response.strip()}")
    return response

# ---------------------- Main Execution ----------------------
if __name__ == "__main__":
    logger = setup_logger()
    env = load_environment(logger)
    initialize_models(env, logger)

    documents_dir = os.path.join(os.path.dirname(__file__), ".././Vigga Bru/01 Underlag/kg")
    persist_dir = "./storage/hfallmini2"

    query_engine = load_or_create_index(persist_dir, documents_dir, logger)
    prompt = "hva er omfang av prosjektet?"
    response = send_query(query_engine, prompt, logger)
    print(f"Response: {response.response.strip()}")
    with open("test_rag.txt", "a", encoding='utf-8') as file:
        file.write(f"Query: {prompt}\nResponse: {response.response.strip()}\n\n")
