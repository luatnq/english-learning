#!/usr/bin/env python3
"""
add_to_manifest.py <unit.json>

Thêm/cập nhật một mục trong data/units.json (MANIFEST website đọc để hiện thẻ unit).
Idempotent theo 'id' (chạy lại không tạo trùng). Sắp xếp theo id (⇒ đúng thứ tự unit).
Chỉ dùng thư viện chuẩn.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(ROOT, "data", "units.json")


def entry_for(json_path):
    stem = os.path.splitext(os.path.basename(json_path))[0]      # "01-family" / "01-family-p2"
    with open(json_path, encoding="utf-8") as f:
        U = json.load(f)
    return {
        "id": stem,
        "title_en": U["title_en"],
        "title_vi": U["title_vi"],
        "cefr": U.get("cefr", ""),
        "words": len(U.get("words", [])),
        "json": f"data/topics/{stem}.json",
        "audioDir": f"dist/audio/{stem}/",       # theo id file ⇒ variant không đụng nhau
        "worksheet": f"dist/unit-{stem}_worksheet.pdf",
        "answers": f"dist/unit-{stem}_answers.pdf",
    }


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    e = entry_for(argv[0])

    units = []
    if os.path.isfile(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            units = json.load(f)

    units = [u for u in units if u.get("id") != e["id"]]   # bỏ bản cũ nếu có
    units.append(e)
    units.sort(key=lambda u: u.get("id", ""))              # theo id "NN-topic"

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"✓ manifest: {e['id']} ({len(units)} unit trong units.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
