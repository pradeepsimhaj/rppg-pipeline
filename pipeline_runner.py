from pipeline.video_loader import load_video
from pipeline.chunker import create_chunks
from utils.rppg import rppg_pipeline
import numpy as np
import time
import tempfile
import requests


# =========================
# 🌐 Handle URL videos
# =========================
def load_video_safe(video_path):
    if video_path.startswith("http"):
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")

        response = requests.get(video_path, stream=True)
        for chunk in response.iter_content(chunk_size=1024):
            tmp_file.write(chunk)

        tmp_file.close()
        video_path = tmp_file.name

    return load_video(video_path)


# =========================
# 🧠 Improved Outlier Filter
# =========================
def remove_outliers(bpms):
    if len(bpms) < 3:
        return bpms

    median = np.median(bpms)

    return [
        b for b in bpms
        if 50 <= b <= 110 and abs(b - median) < 20   # 🔥 relaxed threshold
    ]


# =========================
# 🔧 Smoothing
# =========================
def smooth_signal(bpms, window=3):
    smoothed = []
    for i in range(len(bpms)):
        start = max(0, i - window + 1)
        smoothed.append(int(np.mean(bpms[start:i+1])))
    return smoothed


# =========================
# 🚀 Main Pipeline
# =========================
def run_pipeline(video_path):

    # 🔥 FIX: support URL + file
    frames, fps = load_video_safe(video_path)

    if len(frames) == 0:
        return [], 0, 0, 0, "Invalid", 0, 0, 0

    chunks = create_chunks(frames, fps)

    results = []

    for i, chunk in enumerate(chunks):
        start = time.time()

        bpm, resp = rppg_pipeline(chunk, fps)

        end = time.time()

        # 🔥 FIX: keep partial data instead of dropping everything
        if bpm < 40 or bpm > 160:
            bpm = 0

        if resp < 5 or resp > 40:
            resp = 0

        results.append({
            "chunk": i + 1,
            "bpm": bpm,
            "resp": resp,
            "time": round(end - start, 3)
        })

    # =========================
    # 📊 BPM Processing
    # =========================
    bpms = [r["bpm"] for r in results if r["bpm"] > 0]

    if len(bpms) == 0:
        return results, 0, 0, 0, "Invalid", 0, 0, 0

    clean_bpms = remove_outliers(bpms)
    smoothed_bpms = smooth_signal(clean_bpms)

    # =========================
    # 🎯 Final BPM
    # =========================
    if len(smoothed_bpms) >= 3:
        final_bpm = int(np.median(smoothed_bpms))
    else:
        final_bpm = int(np.mean(smoothed_bpms))

    # =========================
    # 🧠 HRV
    # =========================
    hrv = round(np.std(clean_bpms), 2) if len(clean_bpms) > 1 else 0

    # =========================
    # 😓 Stress
    # =========================
    if hrv < 5:
        stress = "High"
    elif hrv < 10:
        stress = "Moderate"
    else:
        stress = "Low"

    # =========================
    # 🫁 Resp Stability
    # =========================
    resps = [r["resp"] for r in results if r["resp"] > 0]
    resp_var = round(np.std(resps), 2) if len(resps) > 1 else 0

    # =========================
    # 🎯 Confidence (stable)
    # =========================
    total_chunks = max(len(chunks), 1)

    valid_ratio = len(clean_bpms) / total_chunks

    std_dev = np.std(clean_bpms) if len(clean_bpms) > 1 else 0
    consistency_score = 1 / (1 + std_dev)

    deviation = abs(final_bpm - np.median(clean_bpms))
    stability_score = 1 / (1 + deviation)

    good_chunks = [b for b in clean_bpms if 60 <= b <= 100]
    quality_ratio = len(good_chunks) / len(clean_bpms)

    confidence = (
        (valid_ratio * 0.35) +
        (consistency_score * 0.25) +
        (stability_score * 0.2) +
        (quality_ratio * 0.2)
    )

    confidence = round(confidence * 100, 2)

    # 🔥 FIX: softer gating
    if confidence < 10:
        final_bpm = 0

    # =========================
    # ⚡ Performance Metrics
    # =========================
    times = [r["time"] for r in results]

    avg_time = round(np.mean(times), 3) if times else 0
    total_time = round(np.sum(times), 3) if times else 0

    return (
        results,
        final_bpm,
        confidence,
        hrv,
        stress,
        resp_var,
        avg_time,
        total_time
    )