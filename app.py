import streamlit as st
import os
import matplotlib.pyplot as plt
from pipeline_runner import run_pipeline

st.title("📹 rPPG Health Monitor")

# =========================
# 🧠 Session State
# =========================
if "video_path" not in st.session_state:
    st.session_state.video_path = None

# =========================
# 🌍 Detect Cloud
# =========================
IS_CLOUD = os.environ.get("STREAMLIT_SERVER_PORT") is not None

# =========================
# 🔘 Mode Selection
# =========================
modes = ["Upload Video"]

if IS_CLOUD:
    modes.append("Webcam (Browser)")
else:
    modes.append("Record Video")

mode = st.radio("Select Input Method:", modes)

# =========================
# 🔗 URL INPUT
# =========================
st.subheader("🔗 Or use video from URL")
url = st.text_input("Paste video URL (.mp4)")

if url:
    st.session_state.video_path = url
    st.success("URL loaded successfully!")

# =========================
# 📤 Upload Mode
# =========================
if mode == "Upload Video":
    uploaded_file = st.file_uploader(
        "Upload a face video (30–60 sec)", type=["mp4"]
    )

    if uploaded_file:
        os.makedirs("output", exist_ok=True)

        # 🔥 unique file name (prevents overwrite issues)
        file_path = os.path.join("output", f"input_{uploaded_file.name}")

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("Video uploaded successfully!")
        st.session_state.video_path = file_path

# =========================
# 🎥 Local Recording (ONLY LOCAL)
# =========================
elif mode == "Record Video":

    if IS_CLOUD:
        st.error("⚠️ Webcam not supported in cloud. Use Upload or Browser Webcam.")
        st.stop()   # 🔥 IMPORTANT

    from pipeline.recorder import record_video

    if st.button("Start Recording"):
        path = record_video()

        if path:
            st.session_state.video_path = path
            
# =========================
# 🌐 Browser Webcam (CLOUD)
# =========================
elif mode == "Webcam (Browser)":
    try:
        from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
        import av
        import cv2

        class VideoProcessor(VideoProcessorBase):
            def __init__(self):
                self.frames = []

            def recv(self, frame):
                img = frame.to_ndarray(format="bgr24")
                self.frames.append(img)
                return av.VideoFrame.from_ndarray(img, format="bgr24")

        ctx = webrtc_streamer(
            key="webcam",
            video_processor_factory=VideoProcessor
        )

        if st.button("Stop & Save Recording"):
            if ctx.video_processor and ctx.video_processor.frames:

                frames = ctx.video_processor.frames

                os.makedirs("output", exist_ok=True)
                path = os.path.join("output", "webcam.mp4")

                h, w, _ = frames[0].shape

                out = cv2.VideoWriter(
                    path,
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    30,
                    (w, h)
                )

                for f in frames:
                    out.write(f)

                out.release()

                st.session_state.video_path = path
                st.success("Webcam video saved!")

    except Exception as e:
        st.error("Webcam not supported in this environment")

# =========================
# ▶️ Run Analysis
# =========================
if st.session_state.video_path:

    st.info(f"Using video: {st.session_state.video_path}")

    if st.button("Run Analysis"):
        with st.spinner("Processing..."):

            results, final_bpm, confidence, hrv, stress, resp_var, avg_time, total_time = run_pipeline(
                st.session_state.video_path
            )

        # =========================
        # ❌ No data case
        # =========================
        if len(results) == 0:
            st.error("❌ No valid data extracted. Try better lighting / stable face.")
        else:
            st.subheader("📊 Chunk Results")

            for r in results:
                st.write(
                    f"Chunk {r['chunk']}: BPM={r['bpm']} | Resp={r['resp']} | Time={r['time']}s"
                )

            # =========================
            # 🧠 Final Metrics
            # =========================
            st.success(f"❤️ Final BPM: {final_bpm}")
            st.info(f"📊 Confidence: {confidence}%")
            st.info(f"📉 HRV: {hrv}")
            st.info(f"🫁 Breathing Stability: {resp_var}")
            st.info(f"😓 Stress Level: {stress}")

            # ⚡ Performance
            st.info(f"⚡ Avg Processing Time: {avg_time}s")
            st.info(f"⚡ Total Processing Time: {total_time}s")

            # =========================
            # 🎯 Confidence Indicator
            # =========================
            if confidence > 80:
                st.success("🟢 High confidence")
            elif confidence > 50:
                st.warning("🟡 Moderate confidence")
            else:
                st.error("🔴 Low confidence")

            # =========================
            # 📈 BPM Graph
            # =========================
            bpms = [r["bpm"] for r in results]

            fig, ax = plt.subplots()
            ax.plot(bpms, marker='o')
            ax.set_title("BPM over Time")
            ax.set_xlabel("Chunk")
            ax.set_ylabel("BPM")

            st.pyplot(fig)