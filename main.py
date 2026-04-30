from pipeline_runner import run_pipeline

video_path = "output/input.mp4"   # ✅ FIXED PATH

results, final_bpm, *_ = run_pipeline(video_path)

if len(results) == 0:
    print("❌ No valid data")
    exit()

print("\n📊 Results:")
for r in results:
    print(f"Chunk {r['chunk']}: BPM={r['bpm']} | Resp={r['resp']} | Time={r['time']}s")

print("\n📈 Final BPM:", final_bpm)