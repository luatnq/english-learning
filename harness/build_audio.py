#!/usr/bin/env python3
"""
Sinh audio TTS cho một unit (mặc định Unit 1: Family).
Đọc data/topics/01-family.json, xuất mp3 vào dist/audio/unit01/.
Giọng: en-US-AriaNeural, tốc độ chậm (-12%) hợp A1-A2.
Yêu cầu: edge-tts (cần mạng), ffmpeg.
"""
import os, json, asyncio, re
import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UNIT_JSON = os.path.join(ROOT, "data", "topics", "01-family.json")
OUT = os.path.join(ROOT, "dist", "audio", "unit01")
os.makedirs(os.path.join(OUT, "words"), exist_ok=True)

VOICE = "en-US-AriaNeural"
RATE = "-12%"      # chậm lại cho người mới

with open(UNIT_JSON, encoding="utf-8") as f:
    U = json.load(f)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

# (text, output_path)
jobs = []
# E1 — dictation
for i, tr in enumerate(U["listening"]["dictation"], 1):
    jobs.append((tr, os.path.join(OUT, f"e1_{i}.mp3")))
# E2 — listen & choose (single word phát ra)
for i, (ans, opts) in enumerate(U["listening"]["choose"], 1):
    jobs.append((ans, os.path.join(OUT, f"e2_{i}.mp3")))
# Reading passage
jobs.append((U["reading"]["text"], os.path.join(OUT, "reading.mp3")))
# Per-word pronunciation (section A) — từ + câu ví dụ
for w in U["words"]:
    word, ipa, pos, mvi, ex, exvi = w
    jobs.append((f"{word}. {ex}", os.path.join(OUT, "words", f"{slug(word)}.mp3")))

async def synth(text, path):
    com = edge_tts.Communicate(text, VOICE, rate=RATE)
    await com.save(path)

async def main():
    ok, fail = 0, 0
    for text, path in jobs:
        try:
            await synth(text, path)
            ok += 1
            print(f"  ✓ {os.path.relpath(path, ROOT)}")
        except Exception as e:
            fail += 1
            print(f"  ✗ {os.path.relpath(path, ROOT)}  ({e})")
    print(f"\nDone: {ok} ok, {fail} failed  →  {os.path.relpath(OUT, ROOT)}")

if __name__ == "__main__":
    asyncio.run(main())
