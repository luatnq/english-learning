#!/usr/bin/env python3
"""
build_unit.py <unit.json> [--no-audio] [--no-pdf]

LỆNH GÓI DUY NHẤT để dựng một unit từ file nội dung JSON:

    validate  →  manifest  →  PDF (worksheet+answers)  →  audio (mp3)

Nguyên tắc:
- validate + manifest chỉ dùng thư viện chuẩn ⇒ LUÔN chạy ⇒ website (sản phẩm chính)
  cập nhật ngay, không cần cài gì.
- PDF cần reportlab/qrcode, audio cần edge-tts/ffmpeg. Thiếu deps → BỎ QUA phần đó,
  in hướng dẫn bật, KHÔNG phá cả build. Ưu tiên dùng ./.venv nếu có.

Chạy:  python3 harness/build_unit.py data/topics/05-food.json
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def venv_python():
    """Trả về interpreter có reportlab (ưu tiên ./.venv), else None cho phần PDF."""
    cand = os.path.join(ROOT, ".venv", "bin", "python")
    for py in (cand, sys.executable):
        if os.path.isfile(py):
            r = subprocess.run([py, "-c", "import reportlab, qrcode"],
                               capture_output=True)
            if r.returncode == 0:
                return py
    return None


def step(title, cmd):
    print(f"\n── {title} ──")
    return subprocess.run(cmd).returncode


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    json_path = args[0]
    no_audio = "--no-audio" in argv
    no_pdf = "--no-pdf" in argv
    py = sys.executable

    print(f"═══ build_unit: {os.path.relpath(json_path, ROOT)} ═══")

    # 1) VALIDATE (gate) — stdlib
    if step("validate", [py, os.path.join(HERE, "validate_unit.py"), json_path]) != 0:
        print("\n✗ Dừng: JSON không hợp lệ. Sửa lỗi rồi chạy lại.")
        return 1

    # 2) MANIFEST — stdlib (đăng ký unit cho website ngay)
    step("manifest", [py, os.path.join(HERE, "add_to_manifest.py"), json_path])

    # 3) PDF — cần reportlab/qrcode
    if no_pdf:
        print("\n── PDF ── (bỏ qua theo --no-pdf)")
    else:
        pdf_py = venv_python()
        if pdf_py:
            step("PDF", [pdf_py, os.path.join(HERE, "render_pdf.py"), json_path])
        else:
            print("\n── PDF ── ⚠ thiếu reportlab/qrcode → BỎ QUA.")
            print("  Bật PDF:  python3 -m venv .venv && .venv/bin/pip install reportlab 'qrcode[pil]'")

    # 4) AUDIO — cần edge-tts + mạng (build_audio tự degrade nếu thiếu)
    if no_audio:
        print("\n── audio ── (bỏ qua theo --no-audio)")
    else:
        audio_py = venv_python() or py
        step("audio", [audio_py, os.path.join(HERE, "build_audio.py"), json_path])

    print("\n✓ Xong. Xem web:  python3 -m http.server 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
