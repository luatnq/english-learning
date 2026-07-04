#!/usr/bin/env python3
"""
render_pdf.py <unit.json> [--out dist]

Builder PDF TỔNG QUÁT — đọc bất kỳ data/topics/<id>.json và xuất:
  - dist/<stem>_worksheet.pdf   (đề in: chỗ viết tay + QR nghe)
  - dist/<stem>_answers.pdf     (đáp án + giải thích ngữ pháp)
trong đó <stem> = tên file JSON không đuôi (vd "01-family" -> unit-01-family_*.pdf).

KHÔNG chứa nội dung unit — nội dung nằm hoàn toàn trong file JSON (data contract §4 CLAUDE.md).
Font: tự dò DejaVu (Linux) hoặc Arial (macOS); fallback Arial Unicode để hỗ trợ tiếng Việt.
Cần: reportlab, qrcode[pil].
"""
import json, os, random, sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, HRFlowable)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


# ---------- Font resolution (cross-platform, hỗ trợ tiếng Việt) ----------
def _first_existing(paths):
    for p in paths:
        if p and os.path.isfile(p):
            return p
    return None

def register_fonts():
    """Đăng ký family 'DV' (normal/bold/italic). Trả về tên family."""
    families = [
        # (normal, bold, italic) — thử lần lượt
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial Italic.ttf"),
        ("/Library/Fonts/Arial.ttf",
         "/Library/Fonts/Arial Bold.ttf",
         "/Library/Fonts/Arial Italic.ttf"),
    ]
    unicode_fallback = _first_existing([
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ])
    normal = bold = italic = None
    for n, b, i in families:
        if os.path.isfile(n):
            normal = n
            bold = b if os.path.isfile(b) else n
            italic = i if os.path.isfile(i) else n
            break
    if not normal:
        normal = bold = italic = unicode_fallback
    if not normal:
        sys.exit("✗ Không tìm thấy font Unicode nào (DejaVu/Arial). "
                 "Cài font DejaVu hoặc chạy trên máy có Arial Unicode.")
    pdfmetrics.registerFont(TTFont("DV", normal))
    pdfmetrics.registerFont(TTFont("DV-B", bold))
    pdfmetrics.registerFont(TTFont("DV-I", italic))
    pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I")


# ---------- Styles ----------
def style(name, **kw):
    base = dict(fontName="DV", fontSize=10, leading=14, spaceAfter=2)
    base.update(kw)
    return ParagraphStyle(name, **base)


def build_pdf(UNIT, stem, dist_dir, answers: bool):
    H_TITLE = style("t", fontName="DV-B", fontSize=16, leading=20, alignment=TA_CENTER)
    H_SUB = style("s", fontSize=9.5, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"))
    H_SEC = style("sec", fontName="DV-B", fontSize=11.5, leading=15, textColor=colors.HexColor("#1f4e79"), spaceBefore=8, spaceAfter=4)
    P = style("p")
    P_I = style("pi", fontName="DV-I", textColor=colors.HexColor("#444444"), fontSize=9)
    P_SM = style("psm", fontSize=9, leading=12)

    TS_GRID = TableStyle([
        ("FONT", (0, 0), (-1, -1), "DV", 9), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef6")), ("FONT", (0, 0), (-1, 0), "DV-B", 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ])
    letters = list("abcdefghijklmnop")

    def sec(S, letter, title):
        S.append(Paragraph(f"{letter}. {title}", H_SEC))

    def header(S):
        S.append(Paragraph(f"UNIT {UNIT['unit']} · {UNIT['title_en'].upper()} ({UNIT['title_vi']})", H_TITLE))
        S.append(Paragraph(f"Level {UNIT['cefr']}  ·  ~{UNIT['minutes']} min  ·  {len(UNIT['words'])} words", H_SUB))
        S.append(Spacer(1, 4))
        S.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1f4e79")))
        S.append(Spacer(1, 6))

    def grammar_box(S):
        g = UNIT.get("grammar")
        if not g:
            return
        inner = [Paragraph(f"<b>{g['title_vi']}</b>", style("gt", fontSize=10.5, textColor=colors.HexColor("#1f4e79"))),
                 Paragraph(f"<i>{g['intro_vi']}</i>", P_I)]
        for i, (txt, ex) in enumerate(g["points"], 1):
            inner.append(Paragraph(f"<b>{i}.</b> {txt}", P_SM))
            inner.append(Paragraph(f"    <font color='#2f6db3'>▸ {ex}</font>", P_SM))
        box = Table([[inner]], colWidths=[None])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef4fb")),
                                 ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#9fbfe0")),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                                 ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        S.append(box)
        S.append(Spacer(1, 4))

    def qr_image(url, size_mm=22):
        import qrcode
        q = qrcode.make(url)
        path = os.path.join(dist_dir, f"_qr_{stem}.png")
        q.save(path)
        return Image(path, width=size_mm * mm, height=size_mm * mm)

    fname = f"unit-{stem}_answers.pdf" if answers else f"unit-{stem}_worksheet.pdf"
    doc = SimpleDocTemplate(os.path.join(dist_dir, fname), pagesize=A4,
                            topMargin=13 * mm, bottomMargin=13 * mm, leftMargin=14 * mm, rightMargin=14 * mm,
                            title=f"Unit {UNIT['unit']} {UNIT['title_en']} {'Answers' if answers else 'Worksheet'}")
    S = []
    header(S)
    if answers:
        S.append(Paragraph("ANSWER KEY — Đáp án & giải thích", style("ak", fontName="DV-B", fontSize=11, textColor=colors.HexColor("#a33"))))
        S.append(Spacer(1, 4))
    grammar_box(S)

    # --- A. Words + collocations ---
    sec(S, "A", "New words & phrases — Từ mới & cụm từ")
    if not answers:
        S.append(Paragraph("Nghe/đọc, <b>tự viết nghĩa</b>, và học thuộc các cụm từ (phrases) để nhớ tốt hơn.", P_I))
    head = ["Word", "IPA", "", "Nghĩa" if answers else "Nghĩa (tự viết)", "Example & phrases"]
    rows = [head]
    for w in UNIT["words"]:
        word, ipa, pos, mvi, ex, exvi, collos = w
        meaning = mvi if answers else ""
        collo_html = "<br/>".join(f"<font color='#2f6db3' size='8'>▸ {c[0]} — {c[1]}</font>" for c in collos)
        ex_cell = Paragraph(f"{ex}<br/>{collo_html}", P_SM)
        rows.append([Paragraph(f"<b>{word}</b>", P_SM), Paragraph(ipa, P_SM),
                     pos, Paragraph(meaning, P_SM), ex_cell])
    t = Table(rows, colWidths=[28 * mm, 26 * mm, 7 * mm, 30 * mm, None])
    t.setStyle(TS_GRID)
    S.append(t)

    # --- B. Matching + MCQ ---
    sec(S, "B", "Match & choose — Nối và chọn")
    rng = random.Random(7)
    right_items = [vi for en, vi in UNIT["matching"]]
    shuffled = list(enumerate(right_items))
    rng.shuffle(shuffled)
    right = [f"{letters[i]}. {vi}" for i, (orig, vi) in enumerate(shuffled)]
    orig_to_letter = {orig_i: letters[new_i] for new_i, (orig_i, vi) in enumerate(shuffled)}
    left = [f"{i + 1}. {en}" for i, (en, vi) in enumerate(UNIT["matching"])]
    mtable = [[Paragraph("Nối:", style("b1", fontName="DV-B", fontSize=9)), ""]]
    for i in range(len(left)):
        ans = f"  → ({orig_to_letter[i]})" if answers else "  → (   )"
        mtable.append([Paragraph(left[i] + ans, P_SM), Paragraph(right[i], P_SM)])
    mt = Table(mtable, colWidths=[85 * mm, None])
    mt.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "DV", 9), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    S.append(mt)
    S.append(Spacer(1, 3))
    S.append(Paragraph("Choose the correct meaning:", style("mcqh", fontName="DV-B", fontSize=9)))
    for i, (q, opts, ci) in enumerate(UNIT["mcq"]):
        parts = [f"{letters[j]}) {o} " + ("<b>[✓]</b>" if (answers and j == ci) else "( )") for j, o in enumerate(opts)]
        S.append(Paragraph(f"{i + 1}. {q}  " + "   ".join(parts), P_SM))

    # --- C. Cloze ---
    sec(S, "C", "Fill in the blanks — Điền chỗ trống")
    S.append(Paragraph("Word bank: <b>" + " · ".join(UNIT["cloze"]["bank"]) + "</b>", P_SM))
    for i, (sent, ans) in enumerate(UNIT["cloze"]["items"]):
        if answers:
            sent = sent.replace("______", f"<b>{ans}</b>")
        S.append(Paragraph(f"{i + 1}. {sent}", P_SM))

    # --- D. Word order ---
    sec(S, "D", "Put words in order — Sắp xếp từ (ngữ pháp)")
    for i, (toks, ans, note) in enumerate(UNIT["word_order"]):
        jumble = " / ".join(toks)
        if answers:
            S.append(Paragraph(f"{i + 1}. [ {jumble} ]", P_SM))
            S.append(Paragraph(f"   → <b>{ans}</b>", P_SM))
            S.append(Paragraph(f"   <i>Ngữ pháp: {note}</i>", P_I))
        else:
            S.append(Paragraph(f"{i + 1}. [ {jumble} ]", P_SM))
            S.append(Paragraph("   → " + "_" * 58, P_SM))

    # --- E. Listening ---
    sec(S, "E", "Listening — Nghe")
    lis = UNIT["listening"]
    if not answers:
        qr = qr_image(lis["audio_placeholder_url"])
        note = Paragraph("Quét mã QR để nghe audio, rồi làm bài bên dưới.<br/>"
                         "<i>(Audio .mp3 trong dist/audio/ — QR trỏ tới thư mục audio trên repo.)</i>", P_SM)
        et = Table([[qr, note]], colWidths=[26 * mm, None])
        et.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        S.append(et)
    S.append(Paragraph("E1. Listen and write (dictation) — Nghe và chép lại:", style("e1", fontName="DV-B", fontSize=9)))
    for i, tr in enumerate(lis["dictation"]):
        S.append(Paragraph(f"{i + 1}. <b>{tr}</b>" if answers else f"{i + 1}. " + "_" * 60, P_SM))
    S.append(Paragraph("E2. Listen and choose — Nghe và chọn từ đúng:", style("e2", fontName="DV-B", fontSize=9)))
    for i, (ans, opts) in enumerate(lis["choose"]):
        parts = [f"{o} " + ("<b>[✓]</b>" if (answers and o == ans) else "( )") for o in opts]
        S.append(Paragraph(f"{i + 1}. " + "   ".join(parts), P_SM))

    # --- F. Reading ---
    sec(S, "F", "Reading — Đọc hiểu")
    S.append(Paragraph(UNIT["reading"]["text"], P))
    S.append(Spacer(1, 2))
    S.append(Paragraph("True (T) or False (F)?", style("tf", fontName="DV-B", fontSize=9)))
    for i, (q, val) in enumerate(UNIT["reading"]["questions"]):
        if answers:
            S.append(Paragraph(f"{i + 1}. {q}   → <b>{'T' if val else 'F'}</b>", P_SM))
        else:
            S.append(Paragraph(f"{i + 1}. {q}   (T / F)", P_SM))

    # --- G. Writing ---
    sec(S, "G", "Writing — Viết")
    wr = UNIT["writing"]
    S.append(Paragraph(f"<b>{wr['prompt']}</b>  <i>({wr['prompt_vi']})</i>", P_SM))
    S.append(Paragraph("Trả lời các câu hỏi gợi ý sau để viết thành đoạn:", P_I))
    for i, (qen, qvi) in enumerate(wr["questions"], 1):
        S.append(Paragraph(f"{i}. {qen} <font color='#666666'>({qvi})</font>", P_SM))
    S.append(Paragraph(f"<i>{wr['grammar_reminder_vi']}</i>", P_I))
    if answers:
        S.append(Paragraph("Model answer — bài mẫu:", style("mw", fontName="DV-B", fontSize=9)))
        S.append(Paragraph(wr["model"], P_I))
    else:
        for _ in range(5):
            S.append(Spacer(1, 3))
            S.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#cccccc")))

    S.append(Spacer(1, 8))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1f4e79")))
    S.append(Paragraph(UNIT.get("source", "Vocabulary: NGSL (CC BY-SA 4.0). Examples & exercises: original."), P_I))
    doc.build(S)
    return os.path.join(dist_dir, fname)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    json_path = argv[0]
    dist_dir = os.path.join(ROOT, "dist")
    if "--out" in argv:
        dist_dir = argv[argv.index("--out") + 1]
    os.makedirs(dist_dir, exist_ok=True)

    with open(json_path, encoding="utf-8") as f:
        UNIT = json.load(f)
    stem = os.path.splitext(os.path.basename(json_path))[0]  # "01-family"

    register_fonts()
    ws = build_pdf(UNIT, stem, dist_dir, answers=False)
    ak = build_pdf(UNIT, stem, dist_dir, answers=True)
    print(f"✓ worksheet: {os.path.relpath(ws, ROOT)}")
    print(f"✓ answers  : {os.path.relpath(ak, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
