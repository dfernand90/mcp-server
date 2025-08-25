from modelling.utils import(
    create_or_load_text_index_module, 
    query_text_module,
)
from template_code.sora_curl import send_sora_request
from template_code.gpt4tts_curl import send_gpt4tts_request
from modelling.flux_image_generation import create_image_flux, edit_image_flux
from azure.identity import DefaultAzureCredential
import random
import os
def script_writer(args:None
    ):
    persist_dir_script = args.get("persist_dir_script", "./storage/script/ada3rag1")
    documents_dir_script = args.get("documents_dir_script", "./text")
    script_prompt = args.get("script_prompt", "./script_blueprint.txt")
    # create a dictionary to hold the object script. id, name, base prompt, context_path, scenes, scene number
    #id random sequence of 16 digits
    id = ''.join(random.choices('0123456789', k=16))
    # make directory for the script    
    if not os.path.exists(f"./scripts/{id}"):
        os.makedirs(f"./scripts/{id}")
        os.makedirs(f"./scripts/{id}/audio")
        os.makedirs(f"./scripts/{id}/images")
        os.makedirs(f"./scripts/{id}/video") 
    #name name of the project from first second line of the text_query_responses.txt after the word Response: 
    with open(f"{documents_dir_script}/text_query_responses.txt", "r", encoding='utf-8') as file:
        lines = file.readlines()
        name = lines[1].split("Response: ")[1].strip() if len(lines) > 1 else "Untitled Script"
    #context_path is the path to documents_dir_script
    context_path = documents_dir_script
    print (f"context from: {context_path}")
    #main promtpot is the content of the first line of the script_blueprint.txt
    with open(script_prompt, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        base_prompt = str(lines[0].split("base prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file."    
        # scene number is in the second line of the script_blueprint.txt after the word scenes in script:
        scene_number = int(lines[1].split("scenes in script: ")[1].strip()) if len(lines) > 1 else 5
        title_prompt = str(lines[2].split("scene prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        narration_prompt = str(lines[3].split("narration prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        video_prompt = str(lines[4].split("video prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        image_prompt = str(lines[5].split("image prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
    #scenes is empty for now
    scenes = {}
    # each scene is a dictionary with scene number, scene title, description, ... 
    # narration 'a dictionary contaning (narration: to be filled, audio path: to be filled), 
    # video 'a dictionary contaning (sora prompt: to be filled, video path: to be filled), 
    # image 'a dictionary contaning (image: to be filled, image path: to be filled)
    for scene_num in range(1, scene_number + 1):
        scenes[scene_num] = {
            "scene title": "",
            "description": "",
            "narration": {"narration": "", "audio path": ""},
            "video": {"sora prompt": "", "video path": ""},
            "image": {"image description": "", "image path": ""},
            "duration": 0  
        }
    
    script_object = {   
        "id": id,
        "name": name,
        "base_prompt": base_prompt,
        "context_path": context_path,
        "scene_number": scene_number,
        "scenes": scenes
    }
    text_query_engine_script, text_logger = create_or_load_text_index_module(persist_dir_script, documents_dir_script)
    # the promt script is the base prompt from the script_object property base_prompt
    prompt_script = script_object["base_prompt"]
    print (f"📝 Script Prompt: {prompt_script.strip()}")
    script_response = query_text_module(text_query_engine_script, prompt_script, text_logger)
    script_content = script_response.response.strip()
    print(f"📝 Script Content: {script_content}")
    script_object.update({"script_content": script_content})
    # write scenes to the script_object
    for scene_num in range(1, scene_number + 1):
        scene_description_prompt = f"take out the description for wirting the scene {scene_num} based on the script content: {script_content}"
        scene_description = query_text_module(text_query_engine_script, scene_description_prompt, text_logger).response.strip()
        scene_title_prompt = f"write {title_prompt} of the scene {scene_num} from the {scene_description}"
        scene_title = query_text_module(text_query_engine_script, scene_title_prompt, text_logger).response.strip()
        scene_narration_prompt = f"write {narration_prompt} of the scene {scene_num} from the {scene_description}"
        if scene_num == 1 or scene_num == 0:
            scene_narration_prompt = f"write {narration_prompt} of the scene {scene_num} from the {scene_description} remember to say the name of the project: {name}"
            
        scene_narration = query_text_module(text_query_engine_script, scene_narration_prompt, text_logger).response.strip()
        scene_video_prompt = f"write {video_prompt} of the scene {scene_num} from the {scene_description}"
        scene_video = query_text_module(text_query_engine_script, scene_video_prompt, text_logger).response.strip()
        scene_image_prompt = f"write {image_prompt} of the scene {scene_num} from the {scene_description}"
        scene_image = query_text_module(text_query_engine_script, scene_image_prompt, text_logger).response.strip()

        script_object["scenes"][scene_num]["scene title"] = scene_title
        script_object["scenes"][scene_num]["description"] = scene_description
        script_object["scenes"][scene_num]["narration"]["narration"] = scene_narration
        script_object["scenes"][scene_num]["video"]["sora prompt"] = scene_video
        script_object["scenes"][scene_num]["image"]["image description"] = scene_image
        # make the audio for the narration
        
        try:            
            duration = send_gpt4tts_request(
                output_filename=f"./scripts/{id}/audio/scene_{scene_num}_narration.wav",
                args={
                    "prompt": scene_narration,
                    "voice": "alloy"
                }
            )
            script_object["scenes"][scene_num]["narration"]["audio path"] = f"./scripts/{id}/audio/scene_{scene_num}_narration.wav"
        except Exception as e:
            print(f"Error creating audio for scene {scene_num}: {e}")
            duration = 10  # default duration if TTS fails
        #write the duration to the scene
        script_object["scenes"][scene_num]["duration"] = duration
        # make the video for the scene
        duration = min(duration, 5)  # Ensure a maximum duration of 5 seconds    
     
        try:                   
            """
            send_sora_request(
                output_filename=f"./scripts/{id}/video/scene_{scene_num}_video.mp4",
                args={
                    "prompt": scene_video,
                    "duration": duration,
                    "height": 1080,
                    "width": 1920,
                    "test_mode": False
                }
            )
            """
            script_object["scenes"][scene_num]["video"]["video path"] = f"./scripts/{id}/video/scene_{scene_num}_video.mp4"
        except Exception as e:
            print(f"Error creating video for scene {scene_num}: {e}")
        # make the image for the scene
        """
        try:            
            create_image_flux(
                output_filename=f"./scripts/{id}/images/scene_{scene_num}_image.png",
                args={
                    "prompt": scene_image,
                    "size": "1024x1024",
                    "n": 1,
                    "format": "png"
                }
            )
            script_object["scenes"][scene_num]["image"]["image path"] = f"./scripts/{id}/images/scene_{scene_num}_image.png"
        except Exception as e:
            print(f"Error creating image for scene {scene_num}: {e}")
        """
    # write the script object to a file
    script_file_path = f"./scripts/{script_object['id']}/script_object.json"
    with open(script_file_path, "w", encoding='utf-8') as script_file:
        import json
        json.dump(script_object, script_file, ensure_ascii=False, indent=4)
    return id

def brochure_writer(args:None    
    ):
    persist_dir_script = args.get("persist_dir_script", "./storage/script/ada3rag1")
    documents_dir_script = args.get("documents_dir_script", "./text")
    brochure_prompt = args.get("brochure_prompt", "./brochure_blueprint.txt")

    # create a dictionary to hold the object script. id, name, base prompt, context_path, scenes, scene number
    #id random sequence of 16 digits
    id = ''.join(random.choices('0123456789', k=16))
    # make directory for the script    
    if not os.path.exists(f"./brochures/{id}"):
        os.makedirs(f"./brochures/{id}")
        os.makedirs(f"./brochures/{id}/images")
    #name name of the project from first second line of the text_query_responses.txt after the word Response: 
    with open(f"{documents_dir_script}/text_query_responses.txt", "r", encoding='utf-8') as file:
        lines = file.readlines()
        name = lines[1].split("Response: ")[1].strip() if len(lines) > 1 else "Untitled Script"
    #context_path is the path to documents_dir_script
    context_path = documents_dir_script
    #main promtpot is the content of the first line of the script_blueprint.txt
    # HUGE ERROR TODO, slide number is a hardcoded
    with open(brochure_prompt, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        base_prompt = str(lines[0].split("base prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file."    
        # scene number is in the second line of the script_blueprint.txt after the word scenes in script:
        slide_number = int(lines[1].split("slides in brochure: ")[1].strip()) if len(lines) > 1 else 5
        title_prompt = str(lines[2].split("slide prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        image_prompt = str(lines[3].split("image prompt: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        slide1_prompt = str(lines[4].split("slide 1: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        slide2_prompt = str(lines[5].split("slide 2: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        slide3_prompt = str(lines[6].split("slide 3: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        slide4_prompt = str(lines[7].split("slide 4: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        slide5_prompt = str(lines[8].split("slide 5: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
        slide6_prompt = str(lines[9].split("slide 6: ")[1].strip()) if len(lines) > 1 else "make  a script based on the queries and responses in the text_query_responses.txt file." 
    #scenes is empty for now
    slide_prompts=[slide1_prompt, slide2_prompt,slide3_prompt,slide4_prompt,slide5_prompt,slide6_prompt]
    slides = {}
    # each scene is a dictionary with scene number, scene title, description, ... 
    # narration 'a dictionary contaning (narration: to be filled, audio path: to be filled), 
    # video 'a dictionary contaning (sora prompt: to be filled, video path: to be filled), 
    # image 'a dictionary contaning (image: to be filled, image path: to be filled)
    for slide_num in range(1, slide_number + 1):
        slides[slide_num] = {
            "title": "",
            "description": "",
            "image": ""
        }
    
    brochure_object = {   
        "id": id,
        "name": name,
        "base_prompt": base_prompt,
        "context_path": context_path,
        "slides_number": slide_number,
        "slides": slides
    }
    text_query_engine_script, text_logger = create_or_load_text_index_module(persist_dir_script, documents_dir_script)
    # the promt script is the base prompt from the script_object property base_prompt
    """
    prompt_script = brochure_object["base_prompt"]
    print (f"📝 Script Prompt: {prompt_script.strip()}")
    script_response = query_text_module(text_query_engine_script, prompt_script, text_logger)
    script_content = script_response.response.strip()
    print(f"📝 Script Content: {script_content}")
    brochure_object.update({"script_content": script_content})
    """
    # write scenes to the script_object
    for slide_num in range(1, slide_number + 1):
        slide_prompt_temp = slide_prompts[slide_num-1]
        slide_description_prompt = f"{base_prompt} {slide_prompt_temp}"
        if slide_num == 1:
            slide_description_prompt = f"{base_prompt} {slide_prompt_temp} remeber to mention the name of the project: {name}"
        slide_description = query_text_module(text_query_engine_script, slide_description_prompt, text_logger).response.strip()
        slide_title_prompt = f"write {title_prompt} of the slide {slide_num} considering this content: {slide_description}"
        if slide_num == 1:
            slide_title_prompt = f"write {title_prompt} of the slide {slide_num} considering the name of the proejct: {name}"
        slide_title = query_text_module(text_query_engine_script, slide_title_prompt, text_logger).response.strip()
        scene_image_prompt = f"write {image_prompt} of the slide {slide_num} from the {slide_description}"
        slide_image = query_text_module(text_query_engine_script, scene_image_prompt, text_logger).response.strip()

        brochure_object["slides"][slide_num]["title"] = slide_title
        brochure_object["slides"][slide_num]["description"] = slide_description
        #brochure_object["slides"][slide_num]["image"] = scene_image
               
        # make the image for the scene 
        try:            
            create_image_flux(
                output_filename=f"./brochures/{id}/images/slide_{slide_num}_image",
                args={
                    "prompt": slide_image,
                    "size": "1024x1024",
                    "n": 1,
                    "format": "png"
                }
            )
            brochure_object["slides"][slide_num]["image"] = f"./brochures/{id}/images/slide_{slide_num}_image.png"
        except Exception as e:
            print(f"Error creating image for scene {slide_num}: {e}")

    # write the script object to a file
    brochure_file_path = f"./brochures/{brochure_object['id']}/brochure_object.json"
    with open(brochure_file_path, "w", encoding='utf-8') as script_file:
        import json
        json.dump(brochure_object, script_file, ensure_ascii=False, indent=4)
    return id
if __name__ == "__main__":
    persist_dir_script = "./libros/storage/script/ada3rag2"
    documents_dir_script = "./libros/text"
    #script_prompt = "./script_blueprint.txt"
    script_prompt = "./lecture_script_blueprint.txt"
    #brochure_prompt = "./brochure_blueprint.txt"
    brochure_prompt = "./lecture_blueprint.txt"
    id = script_writer(persist_dir_script, documents_dir_script, script_prompt)
    #id = brochure_writer(persist_dir_script, documents_dir_script, brochure_prompt)
    