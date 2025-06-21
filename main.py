import os
import sys
import logging
import requests # This might not be explicitly used in the provided snippet, but keep if used elsewhere.
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory

# Setup
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))
load_dotenv()

# Logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask app
app = Flask(
    __name__,
    static_folder=str(BASE_DIR / "Static"),
    template_folder=str(BASE_DIR / "template")
)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-123')

# Agents
from agents.idea_generator import IdeaGenerator
from agents.script_generator import ScriptGenerator
from agents.audio_generator import AudioGenerator
from agents.video_generator import VideoGenerator
from agents.uploader import Uploader
from agents.seo_optimizer import SEOOptimizer
from agents.stt_generator import STTGenerator

idea_gen = IdeaGenerator()
script_gen = ScriptGenerator()
audio_gen = AudioGenerator()
video_gen = VideoGenerator()
uploader = Uploader()
seo_optimizer = SEOOptimizer()
stt_gen = STTGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_titles', methods=['POST'])
def generate_titles():
    try:
        topic = request.get_json().get("topic", "")
        titles = idea_gen.generate_trending_titles(topic)
        return jsonify({"titles": titles})
    except Exception as e:
        logging.exception("Error generating titles")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_variations', methods=['POST'])
def generate_variations():
    try:
        title = request.get_json().get("selected_title", "")
        variations = idea_gen.generate_variations(title)
        return jsonify({"variations": variations})
    except Exception as e:
        logging.exception("Error generating variations")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_script', methods=['POST'])
def generate_script():
    try:
        idea = request.get_json().get("idea", "")
        script = script_gen.generate_script(idea)
        return jsonify({"script": script})
    except Exception as e:
        logging.exception("Error generating script")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    logging.info("DEBUG: /generate_audio route hit.")
    try:
        data = request.get_json()
        text = data.get("text", "")
        voice_id = data.get("voice_id", "")

        logging.info(f"DEBUG: Received text for audio generation: '{text[:50]}...'")
        logging.info(f"DEBUG: Received voice_id: '{voice_id}'")

        if not text:
            logging.error("❌ Backend: Text for audio generation is empty.")
            return jsonify({"error": "No text provided for audio generation"}), 400

        audio_path = audio_gen.generate_with_pyttsx3(text)

        if audio_path:
            logging.info(f"DEBUG: Audio generation successful. Path: {audio_path}")
            return jsonify({"audio_path": audio_path})
        else:
            logging.error("❌ Backend: Audio generation returned None.")
            return jsonify({"error": "Failed to generate audio"}), 500

    except Exception as e:
        logging.exception("❌ Error in /generate_audio route:")
        return jsonify({"error": "Failed to generate audio: " + str(e)}), 500

@app.route('/optimize_seo', methods=['POST'])
def optimize_seo():
    try:
        script = request.get_json().get("script", "")
        # The optimize method now needs the actual video path for better SEO,
        # but for now, we're keeping it a placeholder as per your current setup.
        # If SEO requires the *generated* video, you'd need to pass it from generate_video
        # or store it in a session. For now, it's just the script.
        result = seo_optimizer.optimize("placeholder_video_path.mp4", script)
        return jsonify(result)
    except Exception as e:
        logging.exception("Error optimizing SEO")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        script = data.get("script", "")
        relative_audio_path = data.get("audio_path", "")
        
        abs_audio_path = os.path.join(BASE_DIR, relative_audio_path)
        
        logging.info(f"DEBUG: generate_video received audio_path: {relative_audio_path}")
        logging.info(f"DEBUG: generate_video using absolute audio_path: {abs_audio_path}")

        word_timings = stt_gen.transcribe_audio(abs_audio_path)

        if word_timings is None:
            logging.warning("No word timings received from STT. Video will be generated without dynamic subtitles.")

        video_path = video_gen.generate_video(script, abs_audio_path, word_timings)
        
        if video_path:
            logging.info(f"DEBUG: Video generation successful. Path: {video_path}")
            return jsonify({"video_path": video_path})
        else:
            logging.error("❌ Backend: Video generation returned None.")
            return jsonify({"error": "Failed to generate video"}), 500
    except Exception as e:
        logging.exception("Error generating video")
        return jsonify({"error": str(e)}), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        data = request.get_json() # NEW: Get data from frontend
        video_path_relative = data.get("video_path", "") # e.g., "assets/output/generated_video.mp4"
        title = data.get("title", "AI Generated Video")
        description = data.get("description", "A video generated by AI.")
        tags = data.get("tags", ["AI", "Generated", "YouTube"])

        if not video_path_relative:
            logging.error("❌ Backend: No video_path received for upload.")
            return jsonify({"status": "failed", "message": "No video path provided."}), 400

        # Reconstruct absolute path for the uploader
        abs_video_path = os.path.join(BASE_DIR, video_path_relative)
        logging.info(f"DEBUG: Attempting to upload video from: {abs_video_path}")

        uploaded_video_id = uploader.upload(abs_video_path, title, description, tags)
        
        if uploaded_video_id:
            logging.info(f"DEBUG: Video uploaded successfully. ID: {uploaded_video_id}")
            return jsonify({"status": "uploaded", "video_id": uploaded_video_id})
        else:
            logging.error("❌ Backend: Video upload failed (uploader returned None).")
            return jsonify({"status": "failed", "message": "Video upload failed."}), 500
    except Exception as e:
        logging.exception("Error uploading video")
        return jsonify({"error": str(e)}), 500

@app.route('/Static/videos/<filename>')
def serve_video(filename):
    logging.info(f"DEBUG: Serving video file: {filename}")
    full_path_to_video_dir = os.path.join(BASE_DIR, 'assets', 'output')
    if not os.path.exists(os.path.join(full_path_to_video_dir, filename)):
        logging.error(f"ERROR: Video file not found at {os.path.join(full_path_to_video_dir, filename)}")
        return "File not found", 404
    return send_from_directory(full_path_to_video_dir, filename)

@app.route('/download_audio/<path:filename>')
def download_audio(filename):
    logging.info(f"DEBUG: Attempting to serve audio file: {filename}")
    try:
        full_path = os.path.join(BASE_DIR, filename)
        logging.info(f"DEBUG: Full path being served for download: {full_path}")
        if not os.path.exists(full_path):
            logging.error(f"ERROR: File not found for download: {full_path}")
            return "File not found", 404
        return send_from_directory(BASE_DIR, filename, as_attachment=False)
    except Exception as e:
        logging.exception(f"ERROR: Error serving audio file: {filename}, Error: {e}")
        return "Internal server error", 500

if __name__ == '__main__':
    app.run(debug=True)