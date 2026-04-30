import cv2
import os

def load_video(video_path):
    print(f"📥 Loading video: {video_path}")

    if not os.path.exists(video_path):
        print("❌ File not found")
        return [], 30

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Cannot open video")
        return [], 30

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

    print(f"✅ Loaded {len(frames)} frames")
    return frames, fps