import os
import requests
import time
import json
from dotenv import load_dotenv
def send_sora_request(output_filename="output.mp4",args=None):
    """
    Function to send a request to the Sora video generation API and save the output video.
    """
    load_dotenv()
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_US_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_US_ENDPOINT_SORA")
    API_VERSION = "preview"
    params = f'?api-version={API_VERSION}'

    if args is None:
        args = {}
    prompt = args.get("prompt", "A serene and professional background scene unfolds, showcasing a modern workspace with a large digital screen displaying a project timeline and key objectives. The setting includes a sleek conference table surrounded by organized documents, blueprints, and a glowing 3D model of a bridge rotating slowly on a side monitor. Through the large windows, a picturesque view of a calm river with a bridge under construction is visible, symbolizing progress and collaboration. The atmosphere is calm yet focused, with soft ambient lighting and subtle animations of data and diagrams appearing on the screen, emphasizing precision and expertise.")
    duration = args.get("duration", 5)
    height = args.get("height", 1080)
    width = args.get("width", 1920)
    test_mode = False
    # 1. Submit the video generation job
    headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_API_KEY
    }
    body = {
    "model": "sora",  
    "prompt": prompt,
    "width": width,
    "height": height,
    "n_seconds": duration
    }
    

    resp = requests.post(f"{AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs?api-version={API_VERSION}", json=body, headers=headers)
    job = resp.json()
    job_id = job["id"]
    print("Job created, ID:", job_id)
    status = job["status"]


    # 2. Poll until status becomes “succeeded”

    while status not in ("succeeded", "failed"):
        time.sleep(2)
        resp = requests.get(f"{AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs/{job_id}?api-version={API_VERSION}", headers=headers)
        status = resp.json()["status"]
        job_response = requests.get(f"{AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs/{job_id}?api-version={API_VERSION}", headers=headers).json()
        status = job_response.get("status")
        print("Status:", status)

    if status == "succeeded":
            generations = job_response.get("generations", [])
            if generations:
                print(f"✅ Video generation succeeded.")
                generation_id = generations[0].get("id")
                video_url = f'{AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/{generation_id}/content/video{params}'
                video_response = requests.get(video_url, headers=headers)
                if video_response.ok:                    
                    with open(output_filename, "wb") as file:
                        file.write(video_response.content)
                    print(f'Generated video saved as "{output_filename}"')
            else:
                print("⚠️ Status is succeeded, but no generations were returned.")
    elif status == "failed":
        print("❌ Video generation failed.")
        print(json.dumps(job_response, sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    send_sora_request(output_filename="output.mp4", args={
        "prompt": "A serene office environment with soft natural lighting streaming through large windows. The scene features a tidy desk with neatly arranged documents, a laptop displaying a spreadsheet, and a stack of folders labeled \"CVs,\" \"Pricing Form,\" and \"Project Summary.\" In the background, a whiteboard displays a checklist with items like \"Submit CVs,\" \"Complete Pricing Form,\" and \"Review Tender Documents.\" The atmosphere is calm and professional, emphasizing organization and attention to detail.",
        "duration": 5,
        "height": 1080,
        "width": 1920,
        "test_mode": False
    })