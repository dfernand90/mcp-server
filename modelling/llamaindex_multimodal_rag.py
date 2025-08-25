import os
import sys
import logging
from dotenv import load_dotenv
from PIL import Image
import transformers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.multi_modal_llms.azure_openai import AzureOpenAIMultiModal
from llama_index.core import Settings, StorageContext
from llama_index.core.indices import MultiModalVectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.schema import ImageNode
from qdrant_client import QdrantClient



def create_documents_data_from_folder(folder_path):
    """
    Scans a folder and returns a list of dictionaries for image files.
    Each dictionary contains a caption (filename without extension)
    and the full path to the image.
    """
    documents_data = []
    supported_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}

    try:
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_extensions:
                    caption = os.path.splitext(file)[0]
                    documents_data.append({
                        "caption": caption,
                        "image": file_path
                    })
    except Exception as e:
        print(f"❌ Error reading folder: {e}")

    return documents_data

# ---------------------- Patch Transformers ----------------------
def patch_transformers():
    _orig_auto = transformers.AutoProcessor.from_pretrained
    def _patched_auto(*args, **kwargs):
        kwargs["use_fast"] = False
        return _orig_auto(*args, **kwargs)
    transformers.AutoProcessor.from_pretrained = _patched_auto

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
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "AZURE_MULTIMODAL_EMBEDDING_NAME": os.getenv("AZURE_MULTIMODAL_EMBEDDING_NAME"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
    }
    for key, val in env.items():
        if not val:
            logger.error(f"❌ Missing environment variable: {key}")
    return env

# ---------------------- Safe Embedding Wrapper ----------------------
class SafeHuggingFaceMultiModalEmbedding(HuggingFaceEmbedding):
    def get_query_embedding(self, query):
        if isinstance(query, str):
            return self.get_text_embedding(query)
        elif isinstance(query, dict) and "image" in query:
            return self.get_image_embedding(query["image"])
        else:
            raise ValueError("Unsupported query format for multimodal embedding.")

# ---------------------- Model Initializer ----------------------
def initialize_models(env, logger):
    try:
        logger.info("🧠 Initializing embedding model...")
        embed_model = SafeHuggingFaceMultiModalEmbedding(
            model_name="llamaindex/vdr-2b-multi-v1",
            device="cpu",
            trust_remote_code=True,
        )
        Settings.embed_model = embed_model

        logger.info("🧠 Initializing multimodal LLM...")
        llm = AzureOpenAIMultiModal(
            model="gpt-4o",
            deployment_name=env["AZURE_OPENAI_DEPLOYMENT_NAME"],
            api_key=env["AZURE_OPENAI_API_KEY"],
            azure_endpoint=env["AZURE_OPENAI_ENDPOINT"],
            api_version=env["AZURE_OPENAI_API_VERSION"],
        )
        return llm, embed_model
    except Exception as e:
        logger.error(f"❌ Failed to initialize models: {e}")
        raise

def load_create_multimodal_index(images_path, db_path, embed_model, logger):
    documents_data = create_documents_data_from_folder(images_path)
    index = load_create_multimodal_index_from_dict(documents_data, db_path, embed_model, logger)
    return index
# ---------------------- Load Documents + Setup Qdrant + Build Index ----------------------
def load_create_multimodal_index_from_dict(documents_data, db_path, embed_model, logger):
    try:
        logger.info("📁 Loading image documents...")
        image_nodes = []
        for doc in documents_data:
            node = ImageNode(
                image_path=doc["image"],
                text=doc["caption"],
                metadata={"caption": doc["caption"], "file_path": doc["image"]}
            )
            image_nodes.append(node)
        logger.info(f"📄 {len(image_nodes)} documents loaded.")

        logger.info("💾 Setting up Qdrant vector store...")
        COLLECTION_TEXT = "llama-multi-text"
        COLLECTION_IMAGE = "llama-multi-image"
        client = QdrantClient(path=db_path)
        text_store = QdrantVectorStore(client=client, collection_name=COLLECTION_TEXT)
        image_store = QdrantVectorStore(client=client, collection_name=COLLECTION_IMAGE)
        storage_context = StorageContext.from_defaults(vector_store=text_store, image_store=image_store)

        logger.info("🛠️ Checking if collections exist in Qdrant...")
        text_exists = client.collection_exists(COLLECTION_TEXT)
        image_exists = client.collection_exists(COLLECTION_IMAGE)

        if text_exists and image_exists:
            logger.info("✅ Collections already exist. Loading index from storage...")
            index = MultiModalVectorStoreIndex(
                [],
                storage_context=storage_context,
                image_embed_model=embed_model
            )
        else:
            logger.info("⚠️ Collections not found. Creating new index and embeddings...")
            index = MultiModalVectorStoreIndex(
                image_nodes,
                storage_context=storage_context,
                image_embed_model=embed_model
            )
            logger.info("✅ Index created and stored successfully.")
        return index
    except Exception as e:
        logger.error(f"❌ Failed to load/create index: {e}")
        raise

# ---------------------- Retrieval ----------------------
def run_retrieval(index, query, logger):
    try:
        logger.info("💬 Running retrieval query...")
        retriever_engine = index.as_retriever(similarity_top_k=1, image_similarity_top_k=1)
        retrieval_results = retriever_engine.retrieve(query)

        retrieved_image = []
        for res_node in retrieval_results:
            if isinstance(res_node.node, ImageNode):
                file_path = res_node.node.metadata.get("file_path", "Unknown")
                logger.info(f"🖼️ Retrieved image: {file_path}")
                retrieved_image.append(file_path)
            else:
                display_source_node(res_node, source_length=200)
        return retrieved_image
    except Exception as e:
        logger.error(f"❌ Retrieval failed: {e}")
        raise

# ---------------------- Plotting ----------------------
def plot_images(retrieved_image, logger):
    try:
        logger.info("🖼️ Plotting retrieved images...")
        image_path = retrieved_image[0] if retrieved_image else None
        if not image_path:
            logger.warning("No images retrieved to plot.")
            raise ValueError("No images retrieved to plot.")
        img = Image.open(image_path)
        img.show()
    except Exception as e:
        logger.error(f"❌ Failed to plot images: {e}")

# ---------------------- Main ----------------------
if __name__ == "__main__":
    patch_transformers()
    logger = setup_logger()
    env = load_environment(logger)
    llm, embed_model = initialize_models(env, logger)

    documents_data = [
        {"caption": "An image about plane emergency safety.", "image": "./images/image-1.png"},
        {"caption": "An image about airplane components.", "image": "./images/image-2.png"},
        {"caption": "An image about COVID safety restrictions.", "image": "./images/image-3.png"},
        {"caption": "A confidential image about UFO sightings.", "image": "./images/image-4.png"},
        {"caption": "An image about unusual footprints on Aralar 2011.", "image": "./images/image-5.png"},
    ]
    db_path = "qdrant_mrag_db"
    image_path = "./images"
    index = load_create_multimodal_index(image_path, db_path, embed_model, logger)
    query = "what image portrait footprints?"
    retrieved_image = run_retrieval(index, query, logger)
    plot_images(retrieved_image, logger)
