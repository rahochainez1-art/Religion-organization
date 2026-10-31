import sys, subprocess, numpy as np, sherpa_onnx, time
src, out = sys.argv[1], sys.argv[2]
M = __import__("os").environ.get("WHISPER_DIR","/tmp/whisper-small/")
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=M + "small-encoder.int8.onnx", decoder=M + "small-decoder.int8.onnx",
    tokens=M + "small-tokens.txt", language="fr", task="transcribe", num_threads=int(__import__("os").environ.get("NT","2")))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
sr = 16000
# cut near quiet points, ~25s chunks
win = int(0.1 * sr)
pos, chunks = 0, []
while pos < len(a):
    end = min(pos + 25 * sr, len(a))
    if end < len(a):
        lo, hi = pos + 18 * sr, min(pos + 28 * sr, len(a))
        seg = a[lo:hi]
        n = len(seg) // win
        e = (seg[:n * win].reshape(n, win) ** 2).mean(1)
        end = lo + int(e.argmin()) * win + win // 2
    chunks.append((pos, end)); pos = end
t0 = time.time()
with open(out, "w") as f:
    for i, (s, e) in enumerate(chunks):
        st = rec.create_stream(); st.accept_waveform(sr, a[s:e]); rec.decode_stream(st)
        m, sec = divmod(int(s / sr), 60)
        f.write(f"[{m:02d}:{sec:02d}] {st.result.text.strip()}\n"); f.flush()
        print(f"{i+1}/{len(chunks)} {time.time()-t0:.0f}s", flush=True)
