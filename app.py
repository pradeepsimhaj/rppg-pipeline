import streamlit as st
from pipeline_runner import run_pipeline
from pipeline.recorder import record_video
import matplotlib.pyplot as plt

st.title("📹 rPPG Health Monitor")

if "video_path" not in st.session_state:
    st.session_state.video_path = None

mode = st.radio("Select Input Method:", ["Upload Video", "Record Video"])

# Upload
if mode == "Upload Video":
    uploaded_file = st.file_uploader("Upload a face video (30–60 sec)", type=["mp4"])

    if uploaded_file:
        with open("input.mp4", "wb") as f:
            f.write(uploaded_file.read())

        st.success("Video uploaded successfully!")
        st.session_state.video_path = "input.mp4"

# Record
elif mode == "Record Video":
    st.warning("This will open your system webcam")

    if st.button("Start Recording"):
        path = record_video()

        if path:
            st.success("Recording completed!")
            st.session_state.video_path = path
        else:
            st.error("Recording failed")

# Run analysis
if st.session_state.video_path:

    st.info(f"Using video: {st.session_state.video_path}")

    if st.button("Run Analysis"):
        with st.spinner("Processing..."):
            results, final_bpm, confidence, hrv, stress, resp_var,avg_time, total_time = run_pipeline(
                st.session_state.video_path
            )

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

        # Confidence color
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
        