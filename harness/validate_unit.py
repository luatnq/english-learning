#!/usr/bin/env python3
"""
validate_unit.py <unit.json>

Kiểm tra một file data/topics/<id>.json có ĐÚNG data contract (§4 CLAUDE.md) không.
Chỉ dùng thư viện chuẩn — chạy được ở mọi nơi, không cần cài gì.

- ERROR  (chặn build): thiếu key, sai kiểu, index ngoài phạm vi, chỗ trống cloze thiếu…
- WARNING (không chặn): số lượng khác khuyến nghị, đáp án cloze không có trong word bank…

Exit code: 0 nếu không có ERROR, 1 nếu có.
"""
import json, os, re, sys

errors, warnings = [], []


def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)


def is_str(x): return isinstance(x, str) and x.strip() != ""
def is_pair(x): return isinstance(x, list) and len(x) == 2


def check(U):
    # --- Top-level ---
    for k in ("unit", "topic", "title_en", "title_vi", "cefr", "minutes"):
        if k not in U:
            err(f"thiếu key top-level '{k}'")
    if not isinstance(U.get("unit"), int):
        err("'unit' phải là số nguyên")
    if U.get("cefr") not in ("A1", "A2", "B1", "B2", None):
        warn(f"'cefr'={U.get('cefr')!r} lạ (kỳ vọng A1/A2)")

    # --- Grammar (tùy chọn nhưng nên có) ---
    g = U.get("grammar")
    if g:
        for k in ("title_vi", "intro_vi", "points"):
            if k not in g:
                err(f"grammar thiếu '{k}'")
        for i, p in enumerate(g.get("points", [])):
            if not is_pair(p):
                err(f"grammar.points[{i}] phải là [mô_tả_vi, ví_dụ_en]")
    else:
        warn("không có box 'grammar' (nên có cho A1/A2)")

    # --- Words: [word, ipa, pos, meaning_vi, example_en, example_vi, collocations] ---
    words = U.get("words")
    if not isinstance(words, list) or not words:
        err("'words' phải là list không rỗng")
    else:
        if len(words) < 8:
            warn(f"chỉ {len(words)} từ (khuyến nghị ~12–15)")
        for i, w in enumerate(words):
            if not isinstance(w, list) or len(w) != 7:
                err(f"words[{i}] phải có ĐÚNG 7 phần tử (đang {len(w) if isinstance(w, list) else '?'})")
                continue
            word, ipa, pos, mvi, ex, exvi, collos = w
            if not is_str(word): err(f"words[{i}][0] (word) rỗng")
            if not is_str(mvi): err(f"words[{i}][3] (meaning_vi) rỗng")
            if not is_str(ex): err(f"words[{i}][4] (example_en) rỗng")
            if not isinstance(collos, list):
                err(f"words[{i}][6] (collocations) phải là list")
            else:
                for j, c in enumerate(collos):
                    if not is_pair(c):
                        err(f"words[{i}].collocations[{j}] phải là [phrase_en, phrase_vi]")

    word_set = {w[0].lower() for w in words if isinstance(w, list) and w and is_str(w[0])} if isinstance(words, list) else set()

    # --- MCQ: [question, [options...], correct_index] ---
    for i, m in enumerate(U.get("mcq", [])):
        if not (isinstance(m, list) and len(m) == 3):
            err(f"mcq[{i}] phải là [câu, [lựa chọn], index_đúng]")
            continue
        q, opts, ci = m
        if not (isinstance(opts, list) and len(opts) >= 2):
            err(f"mcq[{i}] cần ≥2 lựa chọn")
        if not (isinstance(ci, int) and 0 <= ci < len(opts)):
            err(f"mcq[{i}] correct_index={ci} ngoài phạm vi 0..{len(opts) - 1 if isinstance(opts, list) else '?'}")

    # --- Matching: [en, vi] ---
    for i, p in enumerate(U.get("matching", [])):
        if not is_pair(p):
            err(f"matching[{i}] phải là [en, vi]")

    # --- Cloze: {bank:[...], items:[[sentence, answer]...]} ---
    cz = U.get("cloze")
    if cz:
        bank = cz.get("bank", [])
        if not isinstance(bank, list) or not bank:
            err("cloze.bank phải là list không rỗng")
        for i, it in enumerate(cz.get("items", [])):
            if not is_pair(it):
                err(f"cloze.items[{i}] phải là [câu_có_chỗ_trống, đáp_án]")
                continue
            sent, ans = it
            if "______" not in sent:
                err(f"cloze.items[{i}] thiếu chỗ trống '______'")
            if isinstance(bank, list) and is_str(ans) and ans not in bank:
                warn(f"cloze.items[{i}] đáp án '{ans}' không có trong word bank")
    else:
        warn("không có phần 'cloze'")

    # --- Word order: [tokens, sentence, note] ---
    for i, wo in enumerate(U.get("word_order", [])):
        if not (isinstance(wo, list) and len(wo) == 3):
            err(f"word_order[{i}] phải là [[tokens], câu_đúng, giải_thích_vi]")
            continue
        toks, ans, note = wo
        if not (isinstance(toks, list) and toks):
            err(f"word_order[{i}] tokens rỗng")
        elif is_str(ans):
            a = re.sub(r"[^\w\s]", "", ans.lower()).split()
            t = sorted(x.lower() for x in toks)
            if sorted(a) != t:
                warn(f"word_order[{i}] tokens không khớp câu đúng (kiểm tra lại thứ tự/từ)")

    # --- Listening ---
    lis = U.get("listening")
    if lis:
        if not isinstance(lis.get("dictation"), list) or not lis["dictation"]:
            err("listening.dictation phải là list không rỗng")
        for i, ch in enumerate(lis.get("choose", [])):
            if not (isinstance(ch, list) and len(ch) == 2 and isinstance(ch[1], list)):
                err(f"listening.choose[{i}] phải là [từ_đúng, [lựa chọn]]")
            elif ch[0] not in ch[1]:
                err(f"listening.choose[{i}] đáp án '{ch[0]}' không nằm trong lựa chọn")
        if not is_str(lis.get("audio_placeholder_url")):
            warn("listening.audio_placeholder_url trống (QR sẽ sai)")
        elif "<user>" in lis["audio_placeholder_url"]:
            warn("listening.audio_placeholder_url còn placeholder '<user>' — sửa thành username thật")
    else:
        err("thiếu phần 'listening'")

    # --- Reading ---
    rd = U.get("reading")
    if rd:
        if not is_str(rd.get("text")):
            err("reading.text rỗng")
        for i, q in enumerate(rd.get("questions", [])):
            if not (isinstance(q, list) and len(q) == 2 and isinstance(q[1], bool)):
                err(f"reading.questions[{i}] phải là [câu, true/false]")
    else:
        err("thiếu phần 'reading'")

    # --- Writing ---
    wr = U.get("writing")
    if wr:
        for k in ("prompt", "prompt_vi", "questions", "grammar_reminder_vi", "model"):
            if k not in wr:
                err(f"writing thiếu '{k}'")
        for i, q in enumerate(wr.get("questions", [])):
            if not is_pair(q):
                err(f"writing.questions[{i}] phải là [câu_hỏi_en, câu_hỏi_vi]")
    else:
        err("thiếu phần 'writing'")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    path = argv[0]
    try:
        with open(path, encoding="utf-8") as f:
            U = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ JSON không hợp lệ: {e}")
        return 1
    except FileNotFoundError:
        print(f"✗ Không tìm thấy file: {path}")
        return 1

    check(U)
    name = os.path.basename(path)
    for w in warnings:
        print(f"  ⚠ {w}")
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n✗ {name}: {len(errors)} lỗi, {len(warnings)} cảnh báo — SỬA trước khi build.")
        return 1
    print(f"✓ {name}: hợp lệ ({len(warnings)} cảnh báo).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
