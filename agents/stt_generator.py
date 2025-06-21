import os
import requests
import time
import json
import logging
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class STTGenerator:
    def __init__(self):
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            logging.error("ASSEMBLYAI_API_KEY not found in .env file. Speech-to-Text will not work.")
        self.base_url = "https://api.assemblyai.com/v2"

        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }

    def _read_file(self, audio_file_path, chunk_size=5242880):
        """Reads a file in chunks for uploading."""
        with open(audio_file_path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data

    def transcribe_audio(self, audio_file_path):
        """
        Transcribes an audio file using AssemblyAI and returns word-level timings.
        Returns a list of dictionaries, each with 'text', 'start', 'end' for words.
        """
        if not self.api_key:
            return None

        if not os.path.exists(audio_file_path):
            logging.error(f"Audio file not found for transcription: {audio_file_path}")
            return None

        logging.info(f"STTGenerator: Starting transcription for {audio_file_path}")

        # 1. Upload the audio file
        upload_url = f"{self.base_url}/upload"
        try:
            upload_response = requests.post(
                upload_url,
                headers={'authorization': self.api_key}, # Authorization header for upload is slightly different
                data=self._read_file(audio_file_path)
            )
            upload_response.raise_for_status()
            upload_data = upload_response.json()
            audio_url = upload_data["upload_url"]
            logging.info(f"STTGenerator: Audio uploaded. URL: {audio_url}")
        except requests.exceptions.RequestException as e:
            logging.error(f"STTGenerator: Error uploading audio to AssemblyAI: {e}")
            return None
        except Exception as e:
            logging.error(f"STTGenerator: An unexpected error occurred during audio upload: {e}")
            return None

        # 2. Submit for transcription
        json_data = {
            "audio_url": audio_url,
            "word_timestamps": True, # Request word-level timings
            "language_code": "en_us" # Specify language for better accuracy
        }
        transcript_url = f"{self.base_url}/transcript"
        try:
            post_response = requests.post(
                transcript_url,
                json=json_data,
                headers=self.headers
            )
            post_response.raise_for_status()
            post_data = post_response.json()
            transcript_id = post_data["id"]
            logging.info(f"STTGenerator: Transcription request submitted. ID: {transcript_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"STTGenerator: Error submitting transcription request to AssemblyAI: {e}")
            return None

        # 3. Poll for transcription results
        polling_endpoint = f"{self.base_url}/transcript/{transcript_id}"
        while True:
            try:
                polling_response = requests.get(polling_endpoint, headers=self.headers)
                polling_response.raise_for_status()
                polling_data = polling_response.json()
                
                status = polling_data["status"]
                logging.info(f"STTGenerator: Transcription status: {status}")

                if status == "completed":
                    if "words" in polling_data:
                        logging.info("STTGenerator: Transcription completed successfully with word timings.")
                        return polling_data["words"]
                    else:
                        logging.error("STTGenerator: Transcription completed but 'words' field not found.")
                        return None
                elif status == "error":
                    logging.error(f"STTGenerator: Transcription failed: {polling_data.get('error')}")
                    return None
                else:
                    time.sleep(3) # Wait before polling again
            except requests.exceptions.RequestException as e:
                logging.error(f"STTGenerator: Error polling transcription results from AssemblyAI: {e}")
                return None
            except Exception as e:
                logging.error(f"STTGenerator: An unexpected error occurred during polling: {e}")
                return None