import os
import requests
from mutagen.mp3 import MP3
from dotenv import load_dotenv
def send_gpt4tts_request(output_filename="output_audio.wav", args=None):
    """
    Function to send a request to the GPT-4 TTS API and save the output audio.
    """
    load_dotenv()
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_US_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_US_ENDPOINT_TTS")
    prompt = args.get("prompt", "jeg er glad i deg hoper jeg at du har det bra")
    voice = args.get("voice", "alloy")
    headers = {
        "Content-Type": "application/json",
        "Accept": "audio/wav",
        "Authorization": f"Bearer {AZURE_OPENAI_API_KEY}"
    }

    data = {
        "model": "gpt-4o-mini-tts-multimodalrag",
        "input": prompt,
        "voice": voice,
        "audio_format": "wav",
    }

    response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        print("response status code:", response.status_code)
        print(response.headers.get("Content-Type"))

        # If JSON, parse and decode audio
        if "application/json" in response.headers.get("Content-Type", ""):
            result = response.json()
            import base64
            audio_data = base64.b64decode(result["data"][0]["audio"])
        else:
            audio_data = response.content
        with open(output_filename, "wb") as f:
            f.write(audio_data)
        audio = MP3(output_filename)
        duration_seconds = audio.info.length
        print(f"Duration: {duration_seconds:.2f} seconds")
        return duration_seconds

    else:
        print("Error:", response.status_code, response.text)
        return None
    
if __name__ == "__main__":
    duration = send_gpt4tts_request(output_filename="output_audio.mp3", args={
        "prompt": "jeg er glad i deg hoper jeg at du har det bra",
        "voice": "alloy"
    })
