import cv2
import os


def load_video(video_path):
    print(f"📥 Loading video: {video_path}")

    if video_path.endswith(".webm"):
        print("⚠️ WebM detected — OpenCV fallback")

    # =========================
    # ❌ File existence check
    # =========================
    if not os.path.exists(video_path):
        print("❌ File not found")
        return [], 30

    # =========================
    # 🔥 Force file backend (avoid camera probing)
    # =========================
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Cannot open video")
        return [], 30

    # =========================
    # 📊 FPS
    # =========================
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        fps = 30
        print("⚠️ FPS fallback to 30")

    frames = []

    # =========================
    # 🎞️ Frame extraction
    # =========================
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # safety check
        if frame is None:
            continue

        frames.append(frame)

    cap.release()

    print(f"✅ Loaded {len(frames)} frames")

    # =========================
    # ❌ Handle empty frames
    # =========================
    if len(frames) == 0:
        print("⚠️ No frames extracted")
        return [], fps

    return frames, fps