import os
import requests
import base64
from PIL import Image
from io import BytesIO
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

def decode_and_save_image(b64_data, output_filename):
    image = Image.open(BytesIO(base64.b64decode(b64_data)))
    image.show()
    image.save(output_filename)
    print(f"✅ Image saved to: '{output_filename}'")

def save_response(response_data, filename_prefix):
    data = response_data['data']
    b64_img = data[0]['b64_json']
    filename = f"{filename_prefix}.png"
    decode_and_save_image(b64_img, filename)

def get_env_config():
    load_dotenv()
    deployment = os.getenv("AZURE_FLUX_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_FLUX_DEPLOYMENT_VERSION", "2025-04-01-preview")

    print("🔧 Loaded configuration:")
    print(f"  Deployment: {deployment}")
    print(f"  API Version: {api_version}")

    return deployment, api_version

def create_image_flux(output_filename = "generated_image", args=None):
    deployment, api_version = get_env_config()
    base_path = f'openai/deployments/{deployment}/images'
    params = f'?api-version={api_version}'
    credential = DefaultAzureCredential()
    token_response = credential.get_token("https://cognitiveservices.azure.com/.default")    
    generation_url = f"https://multimodalragresource.cognitiveservices.azure.com/{base_path}/generations{params}"
    #generation_url = f"{endpoint}/openai/deployments/{deployment}/images/generations?api-version={api_version}"
    prompt = args.get("prompt", "A serene and professional background scene unfolds, showcasing a modern workspace with a large digital screen displaying a project timeline and key objectives. The setting includes a sleek conference table surrounded by organized documents, blueprints, and a glowing 3D model of a bridge rotating slowly on a side monitor. Through the large windows, a picturesque view of a calm river with a bridge under construction is visible, symbolizing progress and collaboration. The atmosphere is calm yet focused, with soft ambient lighting and subtle animations of data and diagrams appearing on the screen, emphasizing precision and expertise.")
    size = args.get("size", "1024x1024")
    n = args.get("n", 1)
    generation_body = {
        "prompt": prompt,
        "n": n,
        "size": size,
        "output_format": "png"
    }
    generation_response = requests.post(
    generation_url,
    headers={
      'Authorization': 'Bearer ' + token_response.token,
      'Content-Type': 'application/json',
    },
    json=generation_body
    ).json()
    save_response(generation_response, output_filename)
    

def edit_image_flux(input_image="generated_image.png", output_filename="edited_image", args=None):
    deployment, api_version = get_env_config()
    base_path = f'openai/deployments/{deployment}/images'
    params = f'?api-version={api_version}'
    credential = DefaultAzureCredential()
    token_response = credential.get_token("https://cognitiveservices.azure.com/.default")    
    prompt = args.get("prompt", "add lables, directors and dimensions to the image that specify what is the kulvert, what is the water stram, what is the highway and so on...")
    n = args.get("n", 1)
    size = args.get("size", "1024x1024")
    edit_url = f"https://multimodalragresource.cognitiveservices.azure.com/{base_path}/edits{params}"   
    edit_body = {
        "prompt": prompt,
        "n": n,
        "size": size
    }
    files = {
        "image": (input_image, open(input_image, "rb"), "image/png"),
    }

    response = requests.post(
        edit_url,
        headers={'Authorization': f'Bearer {token_response.token}'},
        data=edit_body,
        files=files
    ).json()

    save_response(response, output_filename)

if __name__ == "__main__":
    print("🖼️ Image Generation")    
    create_image_flux(output_filename="generated_image", args={
        "prompt": "A serene office environment with soft natural lighting streaming through large windows. The scene features a tidy desk with neatly arranged documents, a laptop displaying a spreadsheet, and a stack of folders labeled \"CVs,\" \"Pricing Form,\" and \"Project Summary.\" In the background, a whiteboard displays a checklist with items like \"Submit CVs,\" \"Complete Pricing Form,\" and \"Review Tender Documents.\" The atmosphere is calm and professional, emphasizing organization and attention to detail.",
        "size": "1024x1024",
        "n": 1,
        "format": "png",
    })
    print("\n🎨 Image Editing")
    
    edit_image_flux(input_image="generated_image.png", output_filename= "edited_image", args={
        "prompt": "add lables to the image that specify what is the desk, what is the laptop, what is the stack of folders, and so on...",
        "n": 1,
        "size": "1024x1024",
        "format": "png",
    })

