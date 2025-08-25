import os
from modelling.azure_rag import (
    setup_logger as setup_logger_text,
    load_environment as load_environment_text,
    initialize_models as initialize_models_text,
    load_or_create_index as load_or_create_text_index,
    send_query as query_text_index
)
from modelling.llamaindex_multimodal_rag import (
    patch_transformers,
    setup_logger as setup_logger_image,
    load_environment as load_environment_image,
    initialize_models as initialize_models_image,
    load_create_multimodal_index,
    run_retrieval as query_image_index,
    plot_images
)

# ---------------------- Text Index Module ----------------------
def create_or_load_text_index_module(persist_dir, documents_dir):
    logger = setup_logger_text()
    env = load_environment_text(logger)
    initialize_models_text(env, logger)
    query_engine = load_or_create_text_index(persist_dir, documents_dir, logger)
    return query_engine, logger

# ---------------------- Multimodal Index Module ----------------------
def create_or_load_multimodal_index_module(images_path, db_path):
    patch_transformers()
    logger = setup_logger_image()
    env = load_environment_image(logger)
    _, embed_model = initialize_models_image(env, logger)
    index = load_create_multimodal_index(images_path, db_path, embed_model, logger)
    return index, logger

# ---------------------- Text Query Module ----------------------
def query_text_module(query_engine, prompt, logger):
    response = query_text_index(query_engine, prompt, logger)
    return response

# ---------------------- Multimodal Query Module ----------------------
def query_multimodal_module(index, query, logger):
    retrieved_image = query_image_index(index, query, logger)
    plot_images(retrieved_image, logger)
    return retrieved_image


# ---------------------- Main Execution ----------------------
if __name__ == "__main__":
    # User-defined inputs
    db_path = "qdrant_mrag_db"
    # remember to change this to vigga bru
    persist_dir = "./storage/Vigga Bru/kg/ada3rag1"
    documents_dir = "./projects/Vigga Bru/01 Underlag/kg"
    images_path = "./projects/Vigga Bru/01 Underlag/images"
    queries_path = "./base_prompts/queries.txt"
    # TODO mmake test combining this with /kg
    response_directory_path = "./projects/Vigga Bru/01 Underlag/text"
    response_file_path = f"{response_directory_path}/text_query_responses.txt"
    image_query = "What image is a better cover for the book 'Vigga Bru'?"

    # Test Text Index Creation and Query
    args={
        "persist_dir": persist_dir,
        "documents_dir": documents_dir,
        "queries_path": queries_path,
        "response_directory_path": response_directory_path,
        "response_file_path": response_file_path
    }
    
    
    """
    # create the text query file if it doesn't exist
    if not os.path.exists(response_directory_path):
        os.mkdir(response_directory_path)
    if not os.path.exists(response_file_path):
        if not os.path.exists(queries_path):
            with open(queries_path, 'w', encoding='utf-8') as f:
                f.write("hva er kontext om?\n")
        
        with open(queries_path, 'r',encoding='utf-8') as file:
            for line in file:
                text_query = line.strip()
                if text_query:
                    print(f"📝 Text Query: {text_query}")
                    text_response = query_text_module(text_query_engine, text_query, text_logger)
                    print(f"📝 Text Response: {text_response.response.strip()}")
                    # save query and response to file
                    with open(response_file_path, "a",  encoding='utf-8') as response_file:
                        response_file.write(f"Query: {text_query}\nResponse: {text_response.response.strip()}\n\n")

    # write the script
    persist_dir_script = "./storage/script/ada3rag1"
    documents_dir_script = "./text"
    script_path = "./text/script.txt"
    script_prompt = "./script_blueprint.txt"
    text_query_engine_script, text_logger = create_or_load_text_index_module(persist_dir_script, documents_dir_script)
    with open(script_prompt, 'r',encoding='utf-8') as file:
        prompt_script = file.read()
    print (f"📝 Script Prompt: {prompt_script.strip()}")
    #prompt_script = "Create a script based on the queries and responses in the text_query_responses.txt file."
    script_response = query_text_module(text_query_engine_script, prompt_script, text_logger)
    with open(script_path, "w", encoding='utf-8') as script_file:
        script_file.write(f"Script: {script_response.response.strip()}\n\n")
    
    # Test Multimodal Index Creation and Query
    image_index, image_logger = create_or_load_multimodal_index_module(images_path, db_path)
    retrieved_images = query_multimodal_module(image_index, image_query, image_logger)
    print(f"🖼️ Retrieved Images: {retrieved_images}")
    """
