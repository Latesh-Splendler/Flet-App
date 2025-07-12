import google.generativeai as genai
import time

class GeminiAi:
    def __init__(self, api_key, model_name="gemini-1.5-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, prompt, instructions=""):
        full_prompt = f"{instructions}\n\n{prompt}" if instructions else prompt

        for attempt in range(3):
            try:
                response = self.model.generate_content(full_prompt)

                if hasattr(response, "text"):
                    return response.text
                else:
                    return "Sorry, I didn't understand that."

            except Exception as e:
                error_msg = str(e)

                if "429" in error_msg or "rate limit" in error_msg.lower():
                    print(f"Rate limit hit. Retrying in 40 seconds... (attempt {attempt+1}/3)")
                    time.sleep(40)
                else:
                    print(f"Gemini API error: {error_msg}")
                    break  # For other errors, don't retry

        return "Sorry, I tried but couldn't get a response from the AI."
