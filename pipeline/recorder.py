import cv2
import os
import tempfile
import requests


def download_video(url):
    """Download video from URL to temp file"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            print("❌ Failed to download video")
            return None

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        for chunk in response.iter_content(chunk_size=1024):
            temp_file.write(chunk)

        temp_file.close()
        return temp_file.name

    except Exception as e:
        print("❌ Error downloading video:", e)
        return None


def load_video(video_path):
    """
    Supports:
    - Local file path
    - URL input
    """

    # =========================
    # 🌐 Handle URL input
    # =========================
    if video_path.startswith("http"):
        print("🌐 Downloading video from URL...")
        video_path = download_video(video_path)

        if video_path is None:
            return [], 0

    # =========================
    # 📁 Validate file
    # =========================
    if not os.path.exists(video_path):
        print("❌ Video file not found:", video_path)
        return [], 0

    # =========================
    # 🎥 Load video
    # =========================
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Failed to open video")
        return [], 0

    fps = int(cap.get(cv2.CAP_PROP_FPS))

    if fps == 0:
        fps = 30
        print("⚠️ FPS fallback to 30")

    frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()

    print(f"✅ Loaded {len(frames)} frames at {fps} FPS")

    return frames, fps