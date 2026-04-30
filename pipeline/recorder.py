import cv2
import time
import os

def record_video(output_path="output/recorded.mp4", min_sec=25, max_sec=65):
    os.makedirs("output", exist_ok=True)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot access camera")
        return None

    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(3))
    height = int(cap.get(4))

    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (width, height)
    )

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    start_time = time.time()
    no_face_start = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        elapsed = time.time() - start_time

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw face box
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        # Timer
        cv2.putText(
            frame,
            f"Time: {int(elapsed)}s",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

        # Require exactly ONE face
        if len(faces) != 1:
            if no_face_start is None:
                no_face_start = time.time()
            elif time.time() - no_face_start > 3:
                print("⚠️ Invalid face count — stopping")
                break
        else:
            no_face_start = None

        out.write(frame)
        cv2.imshow("Recording", frame)

        key = cv2.waitKey(1) & 0xFF

        if elapsed > 30 and key == ord('q'):
            break

        if elapsed >= 60:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    duration = time.time() - start_time

    if duration < min_sec or duration > max_sec:
        print("❌ Invalid duration")
        return None

    return output_path