import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

class Uploader:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.credentials = None
    
    def _authenticate(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", self.scopes)
        self.credentials = flow.run_local_server(port=0)
    
    def upload(self, video_path, title, description, tags=[]):
        if not self.credentials:
            self._authenticate()
        
        youtube = build('youtube', 'v3', credentials=self.credentials)
        
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '22'  # Typically "People & Blogs"
            },
            'status': {
                'privacyStatus': 'private',  # Can be changed to 'public'
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        response = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        ).execute()
        
        return {
            'video_id': response['id'],
            'title': response['snippet']['title'],
            'status': response['status']['uploadStatus']
        }