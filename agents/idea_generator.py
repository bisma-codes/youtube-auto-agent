import os
from dotenv import load_dotenv
import groq

load_dotenv()

class IdeaGenerator:
    def __init__(self):
        self.client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

    def _extract_list_items(self, raw_text):
        lines = raw_text.strip().split("\n")
        items = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit() or line.startswith(("*", "-", "•")):
                cleaned = line.split(".", 1)[-1].strip(" -*•\"")
                if cleaned:
                    items.append(cleaned)
        return items

    def generate_trending_titles(self, niche):
        prompt = (
            f"Generate 5 trending YouTube video title ideas about '{niche}'. "
            f"Make them catchy and viral. Number them."
        )

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192"
            )
            raw = response.choices[0].message.content
            return self._extract_list_items(raw)
        except Exception as e:
            print("❌ Error generating trending titles:", e)
            return [f"{niche} Idea {i}" for i in range(1, 6)]

    def generate_variations(self, selected_title):
        prompt = (
            f"Take this YouTube title: '{selected_title}' and generate 5 new unique and creative variations. Number them."
        )

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192"
            )
            raw = response.choices[0].message.content
            return self._extract_list_items(raw)
        except Exception as e:
            print("❌ Error generating variations:", e)
            return [f"{selected_title} - Variation {i}" for i in range(1, 6)]
