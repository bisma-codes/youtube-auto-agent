import os
import sys
import logging
import requests # Needed for making HTTP requests to Pexels API
from dotenv import load_dotenv # Needed to load API key from .env
# Added VideoFileClip, ColorClip. Included VideoClip for TextClip.
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, ColorClip, VideoClip
from moviepy.video.fx import all as vfx # For video effects like looping, resizing, and cropping

load_dotenv() # Load environment variables from .env file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VideoGenerator:
    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not self.pexels_api_key:
            logging.warning("PEXELS_API_KEY not found in .env file. Video fetching from Pexels will not work.")
            # For now, we'll allow it to proceed but video fetching will fail.
            # In a production app, you might want to raise an error or use a default static background.

        # Directory to temporarily store downloaded Pexels videos
        self.temp_video_dir = "assets/temp_videos"
        os.makedirs(self.temp_video_dir, exist_ok=True) # Ensure this directory exists

        # Common video dimensions for vertical videos (e.g., YouTube Shorts, TikTok)
        self.video_width = 1080
        self.video_height = 1920

        # Subtitle styling
        self.font = 'Arial-Bold' # Ensure this font is available on your system, or change it
        self.text_color = 'white'
        self.stroke_color = 'black'
        self.stroke_width = 1.5
        self.fontsize = 60 # Increased for better visibility

    def _fetch_pexels_video(self, query):
        """Fetches and downloads a portrait orientation video from Pexels."""
        if not self.pexels_api_key:
            logging.error("Pexels API key is not set. Cannot fetch videos.")
            return None

        headers = {
            "Authorization": self.pexels_api_key
        }
        # Pexels video search endpoint
        # Requesting 'portrait' orientation for TikTok/YouTube Shorts format
        # per_page=1 as we only need one video for now
        # min_width/min_height ensure we get reasonably high-res vertical videos
        url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=1&min_width={self.video_width/2}&min_height={self.video_height/2}" # Adjusted min_width/height

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if not data.get("videos"):
                logging.warning(f"No Pexels videos found for query: '{query}'")
                return None

            video_info = data["videos"][0]

            # Find the highest quality 'mp4' file available, prioritizing portrait resolutions
            video_url = None
            # Prioritize common vertical resolutions closest to target
            target_resolutions = [
                (self.video_width, self.video_height), # Full HD vertical
                (self.video_width // 2, self.video_height // 2), # Half HD vertical
                (720, 1280), # Common phone vertical
                (540, 960) # Lower res phone vertical
            ]

            for res_w, res_h in target_resolutions:
                for file in video_info["video_files"]:
                    # Check for mp4, and dimensions, or at least portrait aspect ratio
                    if (file["file_type"] == "video/mp4" and
                        file.get("width") == res_w and
                        file.get("height") == res_h):
                        video_url = file["link"]
                        break
                if video_url:
                    break

            if not video_url: # Fallback to any mp4 if specific resolutions not found
                for file in video_info["video_files"]:
                    if file["file_type"] == "video/mp4" and "link" in file:
                        video_url = file["link"]
                        break

            if not video_url:
                logging.warning(f"No suitable MP4 video file found for Pexels video ID {video_info['id']}.")
                return None

            # Download the video
            video_filename = f"pexels_{video_info['id']}.mp4"
            local_video_path = os.path.join(self.temp_video_dir, video_filename)

            logging.info(f"Downloading Pexels video from {video_url} to {local_video_path}")
            video_response = requests.get(video_url, stream=True)
            video_response.raise_for_status()

            with open(local_video_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logging.info(f"Successfully downloaded Pexels video to {local_video_path}")
            return local_video_path

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching/downloading Pexels video for query '{query}': {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred during Pexels video fetching: {e}")
            return None

    def generate_video(self, script, audio_path, word_timings=None): # NEW: Added word_timings parameter
        logging.info(f"VideoGenerator: Received audio_path: '{audio_path}'")
        logging.info(f"VideoGenerator: Current working directory: '{os.getcwd()}'")

        abs_audio_path = os.path.abspath(audio_path)
        logging.info(f"VideoGenerator: Absolute audio path being tried: '{abs_audio_path}'")

        if not os.path.exists(abs_audio_path):
            logging.error(f"VideoGenerator: File NOT FOUND at '{abs_audio_path}'")
            raise FileNotFoundError(f"Audio file '{audio_path}' not found at absolute path '{abs_audio_path}'")

        output_dir = "Static/videos/output"
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"VideoGenerator: Output directory ensured: '{output_dir}'")

        try:
            audio = AudioFileClip(abs_audio_path)
            duration = audio.duration
            logging.info(f"VideoGenerator: Audio file loaded successfully. Duration: {duration}s")
        except Exception as e:
            logging.error(f"VideoGenerator: Error loading audio file '{abs_audio_path}': {e}")
            raise

        # --- Fetch Pexels background video based on script content ---
        video_query = " ".join(script.split()[:3]) if script else "nature" # Default to 'nature' if script is empty
        logging.info(f"VideoGenerator: Fetching background video for query: '{video_query}'")
        background_video_path = self._fetch_pexels_video(video_query)

        background_clip = None
        if background_video_path and os.path.exists(background_video_path):
            try:
                background_clip = VideoFileClip(background_video_path)

                # Resize and crop the background clip to fit target dimensions while maintaining aspect ratio
                if background_clip.w / background_clip.h > self.video_width / self.video_height:
                    background_clip = background_clip.fx(vfx.resize, height=self.video_height)
                    x_center = background_clip.w / 2
                    background_clip = background_clip.fx(vfx.crop, x_center=x_center, width=self.video_width)
                else:
                    background_clip = background_clip.fx(vfx.resize, width=self.video_width)
                    y_center = background_clip.h / 2
                    background_clip = background_clip.fx(vfx.crop, y_center=y_center, height=self.video_height)

                # Loop or trim background video to match audio duration
                if background_clip.duration < duration:
                    background_clip = background_clip.fx(vfx.loop, duration=duration)
                elif background_clip.duration > duration:
                    background_clip = background_clip.subclip(0, duration)

                logging.info(f"VideoGenerator: Background video processed. Dimensions: {background_clip.size}, Duration: {background_clip.duration}s")

            except Exception as e:
                logging.error(f"VideoGenerator: Error processing downloaded Pexels video: {e}. Falling back to black background.")
                background_clip = None # Fallback if processing fails
        else:
            logging.warning("VideoGenerator: No Pexels background video available or download failed. Using a black background.")

        # Create a blank black background clip if no Pexels video is used
        if background_clip is None:
            background_clip = ColorClip(size=(self.video_width, self.video_height), color=(0,0,0)).set_duration(duration)
            logging.info("VideoGenerator: Using black background clip as fallback.")


        # --- NEW: Generate subtitle clips based on word_timings or full script ---
        text_clips_for_composition = []

        if word_timings and isinstance(word_timings, list) and len(word_timings) > 0:
            logging.info("VideoGenerator: Generating dynamic subtitle clips based on word timings.")
            for word_info in word_timings:
                word = word_info['word']
                # Convert milliseconds to seconds
                start_time = word_info['start'] / 1000.0
                end_time = word_info['end'] / 1000.0

                # Create a text clip for each word/phrase
                txt_clip = TextClip(
                    word,
                    font=self.font,
                    fontsize=self.fontsize,
                    color=self.text_color,
                    stroke_color=self.stroke_color,
                    stroke_width=self.stroke_width,
                    # Text size is constrained by overall video width, but auto-wrapped by method='caption'
                    size=(self.video_width * 0.9, None), # Max 90% of video width, height auto
                    method='caption' # Ensures text wraps if too long
                )

                # Set duration and position for the individual word clip
                txt_clip = txt_clip.set_start(start_time).set_duration(end_time - start_time)
                # Position the text at the bottom, slightly above the bottom edge
                txt_clip = txt_clip.set_position(('center', self.video_height * 0.85)) # Adjust vertical position as needed

                text_clips_for_composition.append(txt_clip)
        else:
            logging.warning("VideoGenerator: No word timings provided or invalid. Falling back to single text clip for entire script.")
            # Fallback to the original single text clip if word_timings are not available
            single_text_clip = TextClip(
                script,
                font=self.font,
                fontsize=self.fontsize, # Use the class's default fontsize
                color=self.text_color,
                stroke_color=self.stroke_color,
                stroke_width=self.stroke_width,
                size=(self.video_width * 0.9, None), # 90% width, auto height
                method='caption'
            ).set_duration(duration).set_position(('center', self.video_height * 0.85)) # Position at bottom
            text_clips_for_composition.append(single_text_clip)

        logging.info("VideoGenerator: Text clips prepared for composition.")


        # --- Combine background video and all text clips ---
        # Ensure background_clip is the first element so text clips are on top
        final_video_composition_elements = [background_clip] + text_clips_for_composition
        video = CompositeVideoClip(final_video_composition_elements, size=(self.video_width, self.video_height))
        video = video.set_audio(audio)
        logging.info("VideoGenerator: Audio, text, and background combined.")

        # --- Write the final video ---
        output_path = os.path.join(output_dir, "generated_video.mp4")
        logging.info(f"VideoGenerator: Writing video to '{output_path}'")
        video.write_videofile(
            output_path,
            fps=24,
            codec="libx264", # High compatibility video codec
            audio_codec="aac", # High compatibility audio codec
            threads=os.cpu_count(), # Use all available CPU cores for faster encoding
            preset="medium", # Encoding speed vs. compression efficiency (ultrafast, superfast, fast, medium, slow, slower, veryslow)
            bitrate="5000k", # Target video bitrate (adjust for quality/file size)
            ffmpeg_params=['-movflags', 'faststart'] # Optimizes for web playback
        )
        logging.info(f"VideoGenerator: Video saved: {output_path}")

        # Clean up temporary video file after generation
        if background_video_path and os.path.exists(background_video_path):
            try:
                os.remove(background_video_path)
            except Exception as e:
                logging.warning(f"Could not remove temporary background video {background_video_path}: {e}")

        return output_path