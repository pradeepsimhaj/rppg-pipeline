import streamlit as st
import os
import time
import cv2
import matplotlib.pyplot as plt
from pipeline_runner import run_pipeline

# =========================
# 🎯 APP TITLE
# =========================
st.title("📹 rPPG Health Monitor")

st.info("💡 Upload or record a 60-second face video for analysis")

# =========================
# 🧠 SESSION STATE
# =========================
if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "recording" not in st.session_state:
    st.session_state.recording = False
    st.session_state.start_time = None

# =========================
# ⏱ VALIDATION
# =========================
def validate_video_length(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()

    if fps <= 0:
        return False

    duration = frames / fps
    return 58 <= duration <= 70


# =========================
# 🔘 MODE SELECTION
# =========================
mode = st.radio(
    "Select Input Method:",
    ["Upload Video", "Video URL", "Record & Upload"]
)

# =========================
# 📤 UPLOAD VIDEO
# =========================
if mode == "Upload Video":
    uploaded_file = st.file_uploader(
        "Upload a 60–65 second face video",
        type=["mp4", "webm"]
    )

    if uploaded_file:
        os.makedirs("output", exist_ok=True)
        path = os.path.join("output", uploaded_file.name)

        with open(path, "wb") as f:
            f.write(uploaded_file.read())

        if not validate_video_length(path):
            st.error("❌ Video must be between 60–65 seconds")
            st.stop()

        st.session_state.video_path = path
        st.success("✅ Video uploaded successfully!")

# =========================
# 🔗 VIDEO URL
# =========================
elif mode == "Video URL":
    url = st.text_input("Paste video URL (.mp4)")

    if url:
        st.session_state.video_path = url
        st.success("✅ URL loaded successfully!")

# =========================
# 🎥 RECORD & UPLOAD (STREAMLIT SAFE)
# =========================
elif mode == "Record & Upload":

    st.info("🎥 Record a 60-second video using your camera")

    st.markdown("""
    ### 📌 Instructions:
    - Keep your face clearly visible
    - Avoid movement
    - Use good lighting
    - Remove glasses if possible
    """)

    # START RECORDING
    if not st.session_state.recording:
        if st.button("▶️ Start Recording"):
            st.session_state.recording = True
            st.session_state.start_time = time.time()

    # RECORDING STATE
    else:
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = max(0, 60 - elapsed)

        st.warning(f"⏱ Recording... {remaining}s remaining")
        st.progress(min(elapsed / 60, 1.0))

        if remaining == 0:
            st.session_state.recording = False
            st.success("✅ Recording complete. Upload video below.")

    # UPLOAD AFTER RECORDING
    uploaded_file = st.file_uploader(
        "Upload your recorded video",
        type=["mp4", "webm"]
    )

    if uploaded_file:
        os.makedirs("output", exist_ok=True)
        path = os.path.join("output", uploaded_file.name)

        with open(path, "wb") as f:
            f.write(uploaded_file.read())

        if not validate_video_length(path):
            st.error("❌ Video must be between 60–65 seconds")
            st.stop()

        st.session_state.video_path = path
        st.success("✅ Video ready for analysis")


# =========================
# ▶️ RUN ANALYSIS
# =========================
if st.session_state.video_path:

    st.info(f"📂 Using: {st.session_state.video_path}")

    if st.button("Run Analysis"):
        with st.spinner("Processing..."):

            result = run_pipeline(st.session_state.video_path)

            # ✅ SAFETY FIX (no crash)
            if not result or len(result) != 8:
                st.error("❌ Processing failed. Invalid video.")
                st.stop()

            results, final_bpm, confidence, hrv, stress, resp_var, avg_time, total_time = result

        if len(results) == 0:
            st.error("❌ No valid data extracted. Try better lighting / stable face.")
        else:
            st.subheader("📊 Results Summary")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("❤️ BPM", final_bpm)
                st.metric("📉 HRV", hrv)
                st.metric("📊 Confidence", f"{confidence}%")

            with col2:
                st.metric("🫁 Resp Stability", resp_var)
                st.metric("😓 Stress", stress)
                st.metric("⚡ Avg Time", f"{avg_time}s")

            st.markdown("---")

            st.subheader("📈 BPM Over Time")

            bpms = [r["bpm"] if r["bpm"] > 0 else None for r in results]
            st.line_chart(bpms)

            # 🧠 Smart feedback
            if confidence < 20:
                st.warning("⚠️ Low confidence — improve lighting and reduce movement.")

            if final_bpm == 0:
                st.error("❌ Unable to estimate heart rate — ensure face is visible.")