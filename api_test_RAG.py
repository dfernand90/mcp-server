from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import logging
import sys
import os
from llama_index.core import Settings
#from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, load_index_from_storage
import json
# Step 1 : set up logger
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)  # logging.DEBUG for more verbose output
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Step 2: set up Azure OpenAI client or headers
endpoint = "https://digital1.openai.azure.com/"
endpoint_ada = "https://mslearndc-resource.cognitiveservices.azure.com/openai/deployments/text-embedding-ada-002-MSLEARNDC/embeddings?api-version=2023-05-15"
model_name = "gpt-4o"
deployment = "gpt-4o-3"
EMBEDDING_DEPLOYMENT = "text-embedding-ada-002-MSLEARNDC"
AZURE_ENDPOINT = "https://mslearndc-resource.cognitiveservices.azure.com/"
#deployment_name_ada_2 = "text-embedding-ada-002" + "some custom name"
#resource_name = "my_resource_name"  # replace with your resource name
#endpoint_ada = "https://{resource_name}.cognitiveservices.azure.com/openai/deployments/{deployment_name_ada_2}/embeddings?api-version=2023-05-15" 

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(FILE_DIR)))
FOLDER_DIR = os.path.join(BASE_DIR, "folder")
documents_dir = os.path.join(FILE_DIR, "./tilbud_test/Vigga Bru/01 Underlag")

with open(os.path.join(FOLDER_DIR, "AFRY_openAI_key.txt"), "r") as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith("AFRY_OPENAI_API_KEY"):
            subscription_key = line.split("=")[1].strip()

with open(os.path.join(FOLDER_DIR, "AFRY_openAI_key.txt"), "r") as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith("bridge_OpenAI_key"):
            subscription_key_bridge = line.split("=")[1].strip()

api_version = "2024-12-01-preview"

# step 3: set up the LLM and embedding model
#TODO: find out how can we access the dashboard to see the models and configurations
llm = AzureOpenAI(
    model="gpt-4o",
    deployment_name="gpt-4o-3",
    api_key=subscription_key,
    azure_endpoint=endpoint,
    api_version=api_version,
)
"""
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
"""
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name=EMBEDDING_DEPLOYMENT,
    api_key=subscription_key_bridge,
    azure_endpoint=AZURE_ENDPOINT,
    api_version="2023-05-15",
)
# step 4: set up the LLM settings

Settings.llm = llm
Settings.embed_model = embed_model
try:
       
        storage_context = StorageContext.from_defaults(
        persist_dir="./storage/adarag",
    )
        index_templates = load_index_from_storage(
            storage_context=storage_context)
        query_engine_templates = index_templates.as_query_engine()
        index_loaded = True
        print("Loaded documents from storage.")
except:
    index_loaded = False
if not index_loaded:  
    # You need to deploy your own embedding model as well as your own chat completion model
    """
    # find out why we cant us this model for embedding
    embed_model = AzureOpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=subscription_key,
        azure_endpoint=endpoint,
        api_version=api_version,
    )
    """


    # step 5: set up the index
    documents = SimpleDirectoryReader(documents_dir).load_data()
    index = VectorStoreIndex.from_documents(
        documents
    )
    index.storage_context.persist(persist_dir="./storage/adarag")
    query_engine_templates = index.as_query_engine()

# step 6: query the index
prompt = "what is the context about?"
response = query_engine_templates.query(
    prompt
)

print(f"answer: {response.response.strip()}")

# step 7: download the CV for CV partner
"""
CV_PATH = os.path.join(BASE_DIR, "./Users/GSG945/Downloads/cvs")
cvs = []
target_name = "Rune Sander Pedersen"
for file in os.listdir(CV_PATH):
    if file.endswith(".json"):
        with open(os.path.join(CV_PATH, file), "r", encoding="utf-8") as f:
            cv = json.load(f)
            if cv.get("name") == target_name:
                print(f"Found CV for {target_name}")
                cvs.append(cv)
                break
            else:
                print(f"CV for {target_name} not found in {file}")

"""
