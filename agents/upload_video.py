from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import os
from datetime import datetime, timedelta

def upload_video(
    video_path: str,
    title: str,
    description: str = "",
    tags: list = None,
    category_id: str = "22",
    privacy_status: str = "private",
    thumbnail_path: str = None,
    schedule_time: datetime = None
):
    """
    Uploads a video to YouTube with enhanced metadata options
    
    Args:
        video_path: Path to video file (MP4/MOV)
        title: Video title
        description: Video description
        tags: List of video tags
        category_id: YouTube category ID (default: "22" for People & Blogs)
        privacy_status: "public", "private", or "unlisted"
        thumbnail_path: Optional path to thumbnail image
        schedule_time: datetime object for scheduled uploads
    Returns:
        Video ID if successful, None otherwise
    """
    try:
        # Validate file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Load credentials
        creds = Credentials.from_authorized_user_file('token.json')
        youtube = build('youtube', 'v3', credentials=creds)

        # Prepare request body
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id,
                "tags": tags or []
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        # Add schedule time if provided
        if schedule_time:
            body["status"]["publishAt"] = schedule_time.isoformat() + "Z"

        # Upload video
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        video_id = response['id']

        # Upload thumbnail if provided
        if thumbnail_path and os.path.exists(thumbnail_path):
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()

        print(f"✅ Upload successful! Video ID: {video_id}")
        print(f"https://youtu.be/{video_id}")
        return video_id

    except HttpError as e:
        print(f"❌ YouTube API error: {e}")
        if e.resp.status == 403:
            print("⚠️ Tip: Delete token.json and re-authenticate")
        return None
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return None

if __name__ == '__main__':
    # Example usage
    upload_video(
        video_path="final_video.mp4",
        title="AI-Generated Tech Review",
        description=open("script.txt").read()[:5000],  # Truncate to YouTube's limit
        tags=["AI", "automation", "python"],
        privacy_status="private",
        thumbnail_path="thumbnail.jpg",
        schedule_time=datetime.now() + timedelta(days=1)  # Schedule for tomorrow
    )