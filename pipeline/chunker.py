def create_chunks(frames, fps, chunk_duration=5):
    if len(frames) == 0:
        print("❌ No frames available for chunking")
        return []

    chunk_size = int(fps * chunk_duration)
    chunks = []

    for i in range(0, len(frames), chunk_size):
        chunk = frames[i:i + chunk_size]
        if len(chunk) == chunk_size:
            chunks.append(chunk)

    print(f"✅ Created {len(chunks)} chunks")
    return chunks