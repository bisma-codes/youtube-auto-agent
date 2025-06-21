import pyttsx3
import logging

logging.basicConfig(level=logging.INFO)

print("Attempting to initialize pyttsx3 engine...")
try:
    engine = pyttsx3.init()
    print("✅ pyttsx3 engine initialized successfully.")
    
    voices = engine.getProperty('voices')
    if voices:
        print(f"Available voices: {len(voices)}")
        for voice in voices:
            print(f"  - ID: {voice.id}, Name: {voice.name}, Languages: {voice.languages}")
    else:
        print("⚠️ No voices found for pyttsx3 engine.")

    text = "Hello, this is a test of the text to speech engine."
    print(f"Attempting to speak: '{text}'")
    engine.say(text)
    engine.runAndWait()
    print("✅ Text spoken successfully.")

except Exception as e:
    print(f"❌ An error occurred during pyttsx3 initialization or speech generation: {e}")
    logging.exception("Detailed traceback for pyttsx3 error:")

print("pyttsx3 test script finished.")