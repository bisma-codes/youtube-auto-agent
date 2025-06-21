import pyttsx3
import os
from datetime import datetime

class AudioGenerator:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.output_dir = "assets/audio_local"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_with_pyttsx3(self, text):
        if not text:
            print("❌ Missing text for pyttsx3 generation.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voiceover_local_{timestamp}.mp3"
        filepath = os.path.join(self.output_dir, filename)

        print(f"DEBUG: Attempting to save audio to: {filepath}") # ADD THIS LINE
        print(f"DEBUG: Absolute path for saving: {os.path.abspath(filepath)}") # ADD THIS LINE
        print(f"DEBUG: Does output_dir exist before saving? {os.path.exists(self.output_dir)}") # ADD THIS LINE

        try:
            self.engine.save_to_file(text, filepath)
            self.engine.runAndWait()

            print(f"DEBUG: After runAndWait(). Does file exist? {os.path.exists(filepath)}") # ADD THIS LINE
            print(f"DEBUG: File size after runAndWait(): {os.path.getsize(filepath) if os.path.exists(filepath) else 'N/A'}") # ADD THIS LINE

            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"✅ Local audio saved: {filepath}")
                return filepath
            else:
                print(f"❌ pyttsx3 failed to save audio to: {filepath}")
                return None
        except Exception as e:
            print("❌ Exception occurred while generating local audio:", str(e))
            return None