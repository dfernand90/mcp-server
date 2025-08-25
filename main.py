import os
from modelling.azure_rag import (
    setup_logger as setup_logger_text,
    load_environment as load_environment_text,
    initialize_models as initialize_models_text,
    load_or_create_index as load_or_create_text_index,
    send_query as query_text_index
)
"""
from modelling.llamaindex_multimodal_rag import (
    patch_transformers,
    setup_logger as setup_logger_image,
    load_environment as load_environment_image,
    initialize_models as initialize_models_image,
    load_create_multimodal_index,
    run_retrieval as query_image_index,
    plot_images
)
"""
from modelling.scripter import script_writer, brochure_writer

from modelling.video_assembler import video_assmbly

from modelling.brochure_creator import create_brochure
# ---------------------- Text Index Module ----------------------
def create_or_load_text_index_module(persist_dir, documents_dir):
    logger = setup_logger_text()
    env = load_environment_text(logger)
    initialize_models_text(env, logger)
    query_engine = load_or_create_text_index(persist_dir, documents_dir, logger)
    return query_engine, logger

# ---------------------- Multimodal Index Module ----------------------
"""
def create_or_load_multimodal_index_module(images_path, db_path):
    patch_transformers()
    logger = setup_logger_image()
    env = load_environment_image(logger)
    _, embed_model = initialize_models_image(env, logger)
    index = load_create_multimodal_index(images_path, db_path, embed_model, logger)
    return index, logger
"""
# ---------------------- Text Query Module ----------------------
def query_text_module(query_engine, prompt, logger):
    response = query_text_index(query_engine, prompt, logger)
    return response

# ---------------------- Multimodal Query Module ----------------------
"""
def query_multimodal_module(index, query, logger):
    retrieved_image = query_image_index(index, query, logger)
    plot_images(retrieved_image, logger)
    return retrieved_image
"""
# ---------------------- summarize a document ----------------------

def sumarize_document_based_on_user_questions(args:None):
    persist_dir = args.get("persist_dir", "")
    documents_dir = args.get("documents_dir", "")
    response_directory_path = args.get("response_directory_path", "")
    response_file_path = args.get("response_file_path", "")
    queries_path = args.get("queries_path", "")
    text_query_engine, logger = create_or_load_text_index_module(persist_dir, documents_dir)
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
                    logger.info(f"📝📝 Text Query: {text_query}")
                    text_response = query_text_module(text_query_engine, text_query, logger)
                    logger.info(f"📝📝 Text Response: {text_response.response.strip()}")
                    # save query and response to file
                    with open(response_file_path, "a",  encoding='utf-8') as response_file:
                        response_file.write(f"Query: {text_query}\nResponse: {text_response.response.strip()}\n\n")
    logger.info(f"🖼️Response file created stored in: {response_file_path}")


# ---------------------- create a video ----------------------
def create_a_video(project_name, underlag, kg):
    response_directory_path = f"./projects/{project_name}/{underlag}/text"
    persist_dir_script = f"./storage/script/{project_name}/{kg}/ada3rag1"
    documents_dir_script = response_directory_path
    script_prompt = "./base_prompts/script_blueprint.txt"
    args_script={
        "persist_dir_script": persist_dir_script,
        "documents_dir_script": documents_dir_script,
        "script_prompt": script_prompt,
    }  
    script_id = script_writer(args= args_script)
    script_id_2 = 2865556207773740
    video_assmbly(script_id, help_script_id =script_id_2)
    return f"The video object: {script_id} was created successfully"
# ---------------------- create a presentation ----------------------
def create_a_brochure(project_name, underlag, kg):
    response_directory_path = f"./projects/{project_name}/{underlag}/text"
    persist_dir_script = f"./storage/script/{project_name}/{kg}/ada3rag1"
    documents_dir_script = response_directory_path
    brochure_prompt = "./base_prompts/brochure_blueprint.txt"
    args_brochure={
        "persist_dir_script": persist_dir_script,
        "documents_dir_script": documents_dir_script,
        "brochure_prompt": brochure_prompt,
    }    
    id_brochure = brochure_writer(args= args_brochure)
    create_brochure(id_brochure)
    return f"The presentation object: {id_brochure} was created successfully"

def tool_video_maker(project_name,underlag,kg):
    # remember to change this to vigga bru
    persist_dir = f"./storage/{project_name}/{kg}/ada3rag1"
    documents_dir = f"./projects/{project_name}/{underlag}/{kg}"
    images_path = f"./projects/{project_name}/{underlag}/images"
    queries_path = "./base_prompts/queries.txt"
    # TODO mmake test combining this with /kg
    response_directory_path = f"./projects/{project_name}/{underlag}/text"
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
    
    sumarize_document_based_on_user_questions(args)    
    
    result = create_a_video(project_name,underlag,kg)
    response= {
        "result": result,
        "id": str(1),
        "error": None             
    }
    return response

def tool_brochure_maker(project_name,underlag,kg):
    # remember to change this to vigga bru
    persist_dir = f"./storage/{project_name}/{kg}/ada3rag1"
    documents_dir = f"./projects/{project_name}/{underlag}/{kg}"
    images_path = f"./projects/{project_name}/{underlag}/images"
    queries_path = "./base_prompts/queries.txt"
    # TODO mmake test combining this with /kg
    response_directory_path = f"./projects/{project_name}/{underlag}/text"
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
    
    sumarize_document_based_on_user_questions(args)
    
    result = create_a_brochure(project_name,underlag,kg)
    response= {
        "result": result,
        "id": str(1),
        "error": None             
    }
    return response
# ---------------------- Main Execution ----------------------
if __name__ == "__main__":
    # User-defined inputs
    db_path = "qdrant_mrag_db"
    project_name = "agent strategy"
    underlag = "01 Underlag"
    kg = "kg" # konkuransegrunlag
    
    #tool_video_maker(project_name,underlag,kg)
    response = tool_brochure_maker(project_name,underlag,kg)
    print(response)
    """  
    # Test Multimodal Index Creation and Query
    image_index, image_logger = create_or_load_multimodal_index_module(images_path, db_path)
    retrieved_images = query_multimodal_module(image_index, image_query, image_logger)
    print(f"🖼️ Retrieved Images: {retrieved_images}")
    """
