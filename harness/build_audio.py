#!/usr/bin/env python3
"""
build_audio.py <unit.json>

Sinh audio TTS cho MỘT unit bất kỳ. Đọc data/topics/<id>.json, xuất mp3 vào
dist/audio/unit<NN>/ theo quy ước tên file (§6 CLAUDE.md):
  e1_<i>.mp3   dictation (E1)
  e2_<i>.mp3   listen & choose (E2)
  reading.mp3  đoạn đọc (F)
  words/<slug>.mp3  phát âm "từ + câu ví dụ"

Giọng en-US-AriaNeural, tốc độ -12% (hợp A1–A2).
Cần: edge-tts + mạng (ghi mp3 trực tiếp, KHÔNG cần ffmpeg). Thiếu → in hướng dẫn, thoát mã 3 (không phá build).
"""
import asyncio, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

VOICE = "en-US-AriaNeural"
RATE = "-12%"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def jobs_for(U, out):
    jobs = []  # (text, path)
    lis = U.get("listening", {})
    for i, tr in enumerate(lis.get("dictation", []), 1):
        jobs.append((tr, os.path.join(out, f"e1_{i}.mp3")))
    for i, ch in enumerate(lis.get("choose", []), 1):
        jobs.append((ch[0], os.path.join(out, f"e2_{i}.mp3")))
    if U.get("reading", {}).get("text"):
        jobs.append((U["reading"]["text"], os.path.join(out, "reading.mp3")))
    for w in U.get("words", []):
        # schema: [word, ipa, pos, meaning_vi, example_en, ...] — dùng index, KHÔNG unpack cứng
        word, example = w[0], w[4]
        jobs.append((f"{word}. {example}", os.path.join(out, "words", f"{slug(word)}.mp3")))
    return jobs


async def run(jobs):
    import edge_tts
    ok = fail = 0
    for text, path in jobs:
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)
            ok += 1
            print(f"  ✓ {os.path.relpath(path, ROOT)}")
        except Exception as e:
            fail += 1
            print(f"  ✗ {os.path.relpath(path, ROOT)}  ({e})")
    return ok, fail


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    json_path = argv[0]
    with open(json_path, encoding="utf-8") as f:
        U = json.load(f)
    stem = os.path.splitext(os.path.basename(json_path))[0]   # theo id file (khớp audioDir manifest)
    out = os.path.join(ROOT, "dist", "audio", stem)
    os.makedirs(os.path.join(out, "words"), exist_ok=True)

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("⚠ edge-tts chưa cài → BỎ QUA audio.")
        print("  Bật audio:  .venv/bin/pip install edge-tts   (cần mạng; không cần ffmpeg)")
        return 3

    jobs = jobs_for(U, out)
    ok, fail = asyncio.run(run(jobs))
    print(f"\n{'✓' if fail == 0 else '⚠'} audio: {ok} ok, {fail} fail  →  {os.path.relpath(out, ROOT)}")
    return 0 if fail == 0 else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
