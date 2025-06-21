import os
import groq
from dotenv import load_dotenv

load_dotenv()

class ScriptGenerator:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY in .env file")
        self.client = groq.Client(api_key=api_key)

    def generate_script(self, video_idea, max_words=200):
        prompt = f"""
Write a natural, engaging, human-sounding YouTube video script for the topic: "{video_idea}".

Guidelines:
- Begin with a strong attention-grabbing hook.
- Briefly explain what the viewer will learn.
- Flow naturally through the main points using a storytelling or conversational tone.
- End with a friendly call-to-action (like encouraging the viewer to subscribe or comment).

⚠️ Do NOT include any labels like "Intro", "Section 1", or timestamps.
Just write the script as if a human YouTuber is saying it aloud in one fluid take.
Keep the script under {max_words} words.
"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192"
            )
            script = response.choices[0].message.content.strip()

            # Trim extra if somehow still too long (fallback)
            words = script.split()
            if len(words) > max_words:
                script = ' '.join(words[:max_words]) + "..."
            return script

        except Exception as e:
            print(f"❌ Error generating script: {e}")
            return "Sorry, something went wrong while generating the script."
