# import streamlit as st
# import os
# import matplotlib.pyplot as plt
# from pipeline_runner import run_pipeline

# st.title("📹 rPPG Health Monitor")

# # =========================
# # 🧠 Session State
# # =========================
# if "video_path" not in st.session_state:
#     st.session_state.video_path = None

# # =========================
# # 🌍 Detect Cloud
# # =========================
# IS_CLOUD = os.environ.get("STREAMLIT_SERVER_PORT") is not None

# # =========================
# # 🔘 Mode Selection
# # =========================
# modes = ["Upload Video"]

# if IS_CLOUD:
#     modes.append("Webcam (Browser)")
# else:
#     modes.append("Record Video")

# mode = st.radio("Select Input Method:", modes)

# # =========================
# # 🔗 URL INPUT
# # =========================
# st.subheader("🔗 Or use video from URL")
# url = st.text_input("Paste video URL (.mp4)")

# if url:
#     st.session_state.video_path = url
#     st.success("URL loaded successfully!")

# # =========================
# # 📤 Upload Mode
# # =========================
# if mode == "Upload Video":
#     uploaded_file = st.file_uploader(
#         "Upload a face video (30–60 sec)", type=["mp4"]
#     )

#     if uploaded_file:
#         os.makedirs("output", exist_ok=True)

#         # 🔥 unique file name (prevents overwrite issues)
#         file_path = os.path.join("output", f"input_{uploaded_file.name}")

#         with open(file_path, "wb") as f:
#             f.write(uploaded_file.read())

#         st.success("Video uploaded successfully!")
#         st.session_state.video_path = file_path

# # =========================
# # 🎥 Local Recording (ONLY LOCAL)
# # =========================
# elif mode == "Record Video":

#     if IS_CLOUD:
#         st.error("⚠️ Webcam not supported in cloud. Use Upload or Browser Webcam.")
#         st.stop()   # 🔥 IMPORTANT

#     from pipeline.recorder import record_video

#     if st.button("Start Recording"):
#         path = record_video()

#         if path:
#             st.session_state.video_path = path

# # =========================
# # 🌐 Browser Webcam (CLOUD)
# # =========================
# elif mode == "Webcam (Browser)":
#     try:
#         from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
#         import av

#         class VideoProcessor(VideoProcessorBase):
#             def __init__(self):
#                 self.frames = []

#             def recv(self, frame):
#                 img = frame.to_ndarray(format="bgr24")
#                 self.frames.append(img)
#                 return av.VideoFrame.from_ndarray(img, format="bgr24")

#         ctx = webrtc_streamer(
#             key="webcam",
#             video_processor_factory=VideoProcessor
#         )

#         if st.button("Stop & Save Recording"):
#             if ctx.video_processor and ctx.video_processor.frames:

#                 import cv2  # ✅ lazy import (only when needed)

#                 frames = ctx.video_processor.frames

#                 os.makedirs("output", exist_ok=True)
#                 path = os.path.join("output", "webcam.mp4")

#                 h, w, _ = frames[0].shape

#                 out = cv2.VideoWriter(
#                     path,
#                     cv2.VideoWriter_fourcc(*'mp4v'),
#                     30,
#                     (w, h)
#                 )

#                 for f in frames:
#                     out.write(f)

#                 out.release()

#                 st.session_state.video_path = path
#                 st.success("Webcam video saved!")

#     except Exception:
#         st.error("Webcam not supported in this environment")

        
# # =========================
# # ▶️ Run Analysis
# # =========================
# if st.session_state.video_path:

#     st.info(f"Using video: {st.session_state.video_path}")

#     if st.button("Run Analysis"):
#         with st.spinner("Processing..."):

#             results, final_bpm, confidence, hrv, stress, resp_var, avg_time, total_time = run_pipeline(
#                 st.session_state.video_path
#             )

#         # =========================
#         # ❌ No data case
#         # =========================
#         if len(results) == 0:
#             st.error("❌ No valid data extracted. Try better lighting / stable face.")
#         else:
#             st.subheader("📊 Chunk Results")

#             for r in results:
#                 st.write(
#                     f"Chunk {r['chunk']}: BPM={r['bpm']} | Resp={r['resp']} | Time={r['time']}s"
#                 )

#             # =========================
#             # 🧠 Final Metrics
#             # =========================
#             st.success(f"❤️ Final BPM: {final_bpm}")
#             st.info(f"📊 Confidence: {confidence}%")
#             st.info(f"📉 HRV: {hrv}")
#             st.info(f"🫁 Breathing Stability: {resp_var}")
#             st.info(f"😓 Stress Level: {stress}")

#             # ⚡ Performance
#             st.info(f"⚡ Avg Processing Time: {avg_time}s")
#             st.info(f"⚡ Total Processing Time: {total_time}s")

#             # =========================
#             # 🎯 Confidence Indicator
#             # =========================
#             if confidence > 80:
#                 st.success("🟢 High confidence")
#             elif confidence > 50:
#                 st.warning("🟡 Moderate confidence")
#             else:
#                 st.error("🔴 Low confidence")

#             # =========================
#             # 📈 BPM Graph
#             # =========================
#             bpms = [r["bpm"] for r in results]

#             fig, ax = plt.subplots()
#             ax.plot(bpms, marker='o')
#             ax.set_title("BPM over Time")
#             ax.set_xlabel("Chunk")
#             ax.set_ylabel("BPM")

#             st.pyplot(fig)







import streamlit as st
import os
import matplotlib.pyplot as plt
from pipeline_runner import run_pipeline
from streamlit_webrtc import webrtc_streamer, WebRtcMode

import streamlit.components.v1 as components
import base64
import uuid


st.title("📹 rPPG Health Monitor")

st.info("💡 Use Upload, URL, or Browser Webcam (works in cloud)")

# =========================
# 🧠 Session State
# =========================
if "video_path" not in st.session_state:
    st.session_state.video_path = None

# =========================
# 🔘 Mode Selection
# =========================
mode = st.radio(
    "Select Input Method:",
    ["Upload Video", "Webcam (Browser)"]
)

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

        path = os.path.join("output", uploaded_file.name)

        with open(path, "wb") as f:
            f.write(uploaded_file.read())

        st.session_state.video_path = path
        st.success("Video uploaded successfully!")

# =========================
# 🌐 Webcam (Browser)
# =========================
# elif mode == "Webcam (Browser)":
#     st.info("📸 Capture video using browser camera")

#     img_file = st.camera_input("Take a picture")

#     if img_file:
#         os.makedirs("output", exist_ok=True)

#         path = "output/capture.jpg"

#         with open(path, "wb") as f:
#             f.write(img_file.getbuffer())

#         st.session_state.video_path = path
#         st.success("Image captured!")        



# elif mode == "Webcam (Browser)":
#     st.info("📸 Record a 60-second video for analysis.")

#     # JavaScript + HTML Component for Recording
#     video_recorder_html = """
#     <div style="text-align: center;">
#         <video id="preview" width="100%" autoplay muted style="background: #000; border-radius: 10px;"></video>
#         <div style="margin-top: 10px;">
#             <button id="startBtn" style="padding: 10px 20px; background: #ff4b4b; color: white; border: none; border-radius: 5px; cursor: pointer;">🔴 Start Recording (60s)</button>
#             <p id="status" style="margin-top: 10px; font-family: sans-serif; color: #555;"></p>
#         </div>
#     </div>

#     <script>
#         const startBtn = document.getElementById('startBtn');
#         const preview = document.getElementById('preview');
#         const status = document.getElementById('status');
        
#         let recorder;
#         let chunks = [];

#         async function startRecording() {
#             const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
#             preview.srcObject = stream;
            
#             recorder = new MediaRecorder(stream);
#             recorder.ondataavailable = (e) => chunks.push(e.data);
#             recorder.onstop = async () => {
#                 const blob = new Blob(chunks, { type: 'video/mp4' });
#                 const reader = new FileReader();
#                 reader.readAsDataURL(blob);
#                 reader.onloadend = () => {
#                     // Send the base64 data back to Streamlit
#                     window.parent.postMessage({
#                         type: 'streamlit:setComponentValue',
#                         value: reader.result
#                     }, '*');
#                 };
#                 stream.getTracks().forEach(track => track.stop());
#                 status.innerText = "✅ Recording Finished! Processing...";
#             };

#             recorder.start();
#             status.innerText = "Recording... 60 seconds remaining";
            
#             // Auto-stop after 60 seconds
#             setTimeout(() => {
#                 if(recorder.state === "recording") {
#                     recorder.stop();
#                 }
#             }, 60000); 
#         }

#         startBtn.onclick = startRecording;
#     </script>
#     """

#     # Render the recorder and capture the base64 output
#     video_data = components.html(video_recorder_html, height=450)

#     # Use a session state hack to catch the data from the component
#     # In a real app, you might use 'streamlit_js_eval' or a custom component 
#     # but for simplicity, we can use a text_input or a hidden trigger.
#     # Here, we'll assume you use the uploaded_file logic once the JS returns the data:
    
#     video_base64 = st.text_input("Internal Video Buffer (Hidden)", key="vid_buffer", label_visibility="collapsed")

#     if video_base64:
#         # Decode the base64 string
#         header, encoded = video_base64.split(",", 1)
#         data = base64.b64decode(encoded)
        
#         os.makedirs("output", exist_ok=True)
#         path = "output/webcam_record.mp4"
        
#         with open(path, "wb") as f:
#             f.write(data)
        
#         st.session_state.video_path = path
#         st.success("Video recorded and saved!")


# # =========================
# # ▶️ Run Analysis
# # =========================
# if st.session_state.video_path:

#     st.info(f"Using: {st.session_state.video_path}")

#     if st.button("Run Analysis"):
#         with st.spinner("Processing..."):

#             output = run_pipeline(
#                 st.session_state.video_path
#             )

#             results = output.get("results", [])

#         if len(results) == 0:
#             st.error("❌ No valid data extracted. Try better lighting.")
#         else:
#             st.subheader("📊 Results")

#             for r in results:
#                 st.write(
#                     f"Chunk {r['chunk']}: BPM={r['bpm']} | Resp={r['resp']} | Time={r['time']}s"
#                 )

#             st.success(f"❤️ BPM: {final_bpm}")
#             st.info(f"📊 Confidence: {confidence}%")
#             st.info(f"📉 HRV: {hrv}")
#             st.info(f"🫁 Resp Stability: {resp_var}")
#             st.info(f"😓 Stress: {stress}")

#             st.info(f"⚡ Avg Time: {avg_time}s")
#             st.info(f"⚡ Total Time: {total_time}s")

#             # Graph
#             bpms = [r["bpm"] for r in results]

#             fig, ax = plt.subplots()
#             ax.plot(bpms, marker='o')
#             ax.set_title("BPM over Time")
#             st.pyplot(fig)







elif mode == "Webcam (Browser)":
    st.info("📸 Record a 60-second video")

    # We use a Data URI to pass the HTML to st.iframe
    recorder_html = """
    <html>
      <body style="margin:0; font-family:sans-serif;">
        <video id="p" width="100%" autoplay muted style="background:#000; border-radius:8px;"></video>
        <button id="b" style="width:100%; margin-top:10px; padding:12px; background:#ff4b4b; color:#fff; border:none; cursor:pointer;">🔴 Start 60s Recording</button>
        <script>
          const b=document.getElementById('b'), p=document.getElementById('p');
          let r, c=[];
          b.onclick = async () => {
            const s = await navigator.mediaDevices.getUserMedia({video:true});
            p.srcObject = s;
            r = new MediaRecorder(s);
            r.ondataavailable = e => c.push(e.data);
            r.onstop = () => {
              const blob = new Blob(c, {type:'video/mp4'});
              const reader = new FileReader();
              reader.readAsDataURL(blob);
              reader.onloadend = () => {
                window.parent.postMessage({type:'streamlit:setComponentValue', value:reader.result}, '*');
              };
              s.getTracks().forEach(t => t.stop());
            };
            r.start();
            setTimeout(() => r.stop(), 60000);
            b.innerText = "Recording... (60s)";
            b.disabled = true;
          };
        </script>
      </body>
    </html>
    """
    
    # Using st.iframe as requested by the 2026 Streamlit update
    video_data = st.iframe(
        f"data:text/html;base64,{base64.b64encode(recorder_html.encode()).decode()}",
        height=400
    )

    # Use a text input to receive the Base64 data from the iframe
    # (Hidden in UI, used to bridge JS to Python)
    video_base64 = st.text_input("Data Bridge", key="bridge", label_visibility="collapsed")

    if video_base64:
        header, encoded = video_base64.split(",", 1)
        data = base64.b64decode(encoded)
        path = "output/capture.mp4"
        with open(path, "wb") as f:
            f.write(data)
        st.session_state.video_path = path
        st.success("Video Captured!")

# =========================
# ▶️ Run Analysis (With Fix for Unpacking)
# =========================
if st.session_state.video_path and st.button("Run Analysis"):
    with st.spinner("Processing..."):
        # Catch the result as a single object first to prevent ValueError
        pipeline_output = run_pipeline(st.session_state.video_path)
        
        # Verify if it's a tuple/list of the right length
        if isinstance(pipeline_output, (list, tuple)) and len(pipeline_output) >= 2:
            results, final_bpm, *others = pipeline_output # *others handles extra values
            # ... rest of your display logic
        else:
            st.error("Pipeline returned unexpected data format.")