# from pipeline.video_loader import load_video
# from pipeline.chunker import create_chunks
# from utils.rppg import rppg_pipeline
# import numpy as np
# import time

# def run_pipeline(video_path):
#     frames, fps = load_video(video_path)
#     chunks = create_chunks(frames, fps)

#     results = []

#     for i, chunk in enumerate(chunks):
#         start = time.time()

#         bpm, resp = rppg_pipeline(chunk, fps)

#         if bpm < 40 or bpm > 180:
#             bpm = 0

#         end = time.time()

#         results.append({
#             "chunk": i+1,
#             "bpm": bpm,
#             "resp": resp,
#             "time": round(end - start, 3)
#         })

#     # =========================
#     # 📊 BPM aggregation
#     # =========================
#     bpms = [r["bpm"] for r in results if r["bpm"] > 0]
#     final_bpm = int(np.median(bpms)) if bpms else 0

#     # =========================
#     # 🧠 HRV (std dev)
#     # =========================
#     hrv = round(np.std(bpms), 2) if len(bpms) > 1 else 0

#     # =========================
#     # 😓 Stress Indicator
#     # =========================
#     if hrv < 5:
#         stress = "High"
#     elif hrv < 10:
#         stress = "Moderate"
#     else:
#         stress = "Low"

#     # =========================
#     # 🫁 Breathing Stability
#     # =========================
#     resps = [r["resp"] for r in results if r["resp"] > 0]
#     resp_variability = round(np.std(resps), 2) if len(resps) > 1 else 0

#     # =========================
#     # 🎯 Confidence Score
#     # =========================
#     if len(bpms) > 1:
#         std_dev = np.std(bpms)
#         variability = max(bpms) - min(bpms)
#     else:
#         std_dev = 0
#         variability = 0

#     valid_ratio = len(bpms) / len(results) if results else 0

#     confidence = (
#         (valid_ratio * 0.4) +
#         ((1 / (1 + std_dev)) * 0.4) +
#         ((1 / (1 + variability)) * 0.2)
#     )

#     confidence = round(confidence * 100, 2)

#     return results, final_bpm, confidence, hrv, stress, resp_variability





















from pipeline.video_loader import load_video
from pipeline.chunker import create_chunks
from utils.rppg import rppg_pipeline
import numpy as np
import time


# =========================
# 🧠 Improved Outlier Filter
# =========================
def remove_outliers(bpms):
    if len(bpms) < 3:
        return bpms

    median = np.median(bpms)

    return [
        b for b in bpms
        if 50 <= b <= 110 and abs(b - median) < 15
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
    frames, fps = load_video(video_path)

    # ❌ Empty video handling
    if len(frames) == 0:
        return [], 0, 0, 0, "Invalid", 0, 0, 0

    chunks = create_chunks(frames, fps)

    results = []

    for i, chunk in enumerate(chunks):
        start = time.time()

        bpm, resp = rppg_pipeline(chunk, fps)

        end = time.time()

        # ❌ Reject invalid chunks
        if bpm == 0 or resp == 0:
            continue

        if bpm < 45 or bpm > 140:
            continue

        results.append({
            "chunk": i + 1,
            "bpm": bpm,
            "resp": resp,
            "time": round(end - start, 3)
        })

    bpms = [r["bpm"] for r in results]

    if len(bpms) == 0:
        return results, 0, 0, 0, "Invalid", 0, 0, 0

    # =========================
    # 📊 Clean + Smooth
    # =========================
    clean_bpms = remove_outliers(bpms)
    smoothed_bpms = smooth_signal(clean_bpms)

    # =========================
    # 🎯 Final BPM (robust)
    # =========================
    if len(smoothed_bpms) >= 3:
        final_bpm = int(np.percentile(smoothed_bpms, 50))  # median
    else:
        final_bpm = int(np.mean(smoothed_bpms)) if smoothed_bpms else 0

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
    resps = [r["resp"] for r in results]
    resp_var = round(np.std(resps), 2) if len(resps) > 1 else 0

    # =========================
    # 🎯 ADVANCED CONFIDENCE (UPDATED)
    # =========================
    valid_ratio = len(clean_bpms) / len(chunks)

    std_dev = np.std(clean_bpms) if len(clean_bpms) > 1 else 0
    consistency_score = 1 / (1 + std_dev)

    deviation = abs(final_bpm - np.median(clean_bpms)) if clean_bpms else 0
    stability_score = 1 / (1 + deviation)

    # 🔥 NEW: reward physiologically good chunks
    good_chunks = [b for b in clean_bpms if 60 <= b <= 100]
    quality_ratio = len(good_chunks) / len(clean_bpms) if clean_bpms else 0

    confidence = (
        (valid_ratio * 0.35) +
        (consistency_score * 0.25) +
        (stability_score * 0.2) +
        (quality_ratio * 0.2)
    )

    confidence = round(confidence * 100, 2)

    # =========================
    # 🔥 Relaxed gating (UPDATED)
    # =========================
    if confidence < 15:
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