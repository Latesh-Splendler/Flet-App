import os
from api_keys import GEMINI_API_KEY, MURF_API_KEY
from gemini import GeminiAi
from murf import Murf

def create_gemini_client(api_key):
    return GeminiAi(api_key=api_key)

def create_murf_client(api_key):
    return Murf(api_key=api_key)

def get_gemini_response(client, user_input, instructions):
    return client.generate_response(user_input, instructions)

def stream_text_to_speech(client, text, output_path):
    try:
        print(f"Streaming text: {text}")
        audio_stream = client.text_to_speech.stream(
            text=text,
            voice_id="en-Us-iris",
            format="MP3",
            sample_rate=48000.0,
            channel_type="STEREO",
            style="Conversational"
        )

        with open(output_path, "wb") as file:
            for chunk in audio_stream:
                file.write(chunk)

        print(f"Audio file created at: {output_path}")        

    except Exception as e:
        print(f"ERROR in Text to Speech: {e}")
        raise

# Optional: fetch voice info on start
# voices = create_murf_client(MURF_API_KEY).text_to_speech.get_voices()
# for voice in voices:
#     print(f'VOICE ID: {voice.voice_id}, Name:{voice.display_name}, MOODS{voice.available_styles}')
