# Imports
import flet as ft 
import speech_recognition as sr 
import os
import time
from google.api_core.exceptions import ResourceExhausted
from ai import (
    create_murf_client,
    create_gemini_client,
    get_gemini_response,
    stream_text_to_speech,
    GEMINI_API_KEY,
    MURF_API_KEY
)

class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

# Main app
def main(page: ft.Page):
    page.title = "AVA (Artificial Virtual Assistant)"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    gemini_client = create_gemini_client(GEMINI_API_KEY)
    murf_client = create_murf_client(MURF_API_KEY)
    recognizer = sr.Recognizer()
    recording = False

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
        padding=20
    )

    new_message = ft.TextField(
        hint_text="Start typing, don't waste my time — otherwise, speak to me, dumbass!",
        expand=True,
        multiline=False
    )

    # Add message to chat
    def add_message(user_name: str, text: str, message_type: str):
        message = Message(user_name, text, message_type)

        if message_type == "system":
            text_color = ft.Colors.RED_400
            bg_color = ft.Colors.GREY_400
        elif message_type == "ai":
            text_color = ft.Colors.WHITE    
            bg_color = ft.Colors.BLUE_400
        else:
            text_color = ft.Colors.BLACK
            bg_color = ft.Colors.GREY_400

        chat.controls.append(
            ft.Column(
                controls=[
                    ft.Text(message.user_name, size=12, color=ft.Colors.GREY_600),
                    ft.Container(
                        content=ft.Text(message.text, selectable=True, color=text_color),
                        border_radius=10,
                        padding=10,
                        bgcolor=bg_color                
                    ),
                ]
            )
        )
        page.update()

    # Send message logic
    def send_message(e):
        if not new_message.value:
            return    
    
        user_message = new_message.value
        add_message("You", user_message, "user")
        new_message.value = ""
        page.update()

        instructions = "Start typing. Impress me. Or at least try not to embarrass yourself."

        try:
            ai_res = get_gemini_response(gemini_client, user_message, instructions)
        except ResourceExhausted:
            add_message("System", "Rate limit exceeded. Retrying after 40 seconds...", "system")
            time.sleep(40)
            try:
                ai_res = get_gemini_response(gemini_client, user_message, instructions)
            except Exception as err:
                add_message("System", f"Gemini error after retry: {err}", "system")
                return
        except Exception as e:
            add_message("System", f"Gemini API error: {e}", "system")
            return

        add_message("AVA", ai_res, "ai")

        # Convert to speech
        try:
            file_path = os.path.abspath("audio.mp3")
            stream_text_to_speech(murf_client, ai_res, file_path)

            page.overlay.clear()
            page.overlay.append(ft.Audio(src="audio.mp3", autoplay=True))
            page.update()

        except Exception as e:
            print(f"ERROR with playing Audio: {e}")    

    # Chat UI
    chat_container = ft.Container(
        content=chat,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=10,
        expand=True,
        padding=10
    )

    input_row = ft.Row(
        controls=[
            new_message,
            ft.IconButton(
                icon=ft.Icons.MIC,
                bgcolor=ft.Colors.GREEN_400
            ),
            ft.IconButton(
                icon=ft.Icons.SEND_ROUNDED,
                bgcolor=ft.Colors.BLUE_400,
                on_click=send_message
            )
        ]
    )

    page.add(
        ft.Column(
            controls=[
                chat_container,
                input_row
            ],
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
