import os
import groq
from dotenv import load_dotenv

load_dotenv()

class SEOOptimizer:
    def __init__(self):
        self.client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))
    
    def optimize(self, video_path, script):
        prompt = f"""Based on this video script: '{script}', generate SEO-optimized:
        1. A catchy YouTube title
        2. A compelling description (at least 200 words)
        3. 10 relevant hashtags
        4. 5 suggested tags
        
        Format the response as a JSON object with keys: title, description, hashtags, tags"""
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content