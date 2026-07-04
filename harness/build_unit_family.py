#!/usr/bin/env python3
"""
Demo builder — Unit 1: Family (A1).
Sinh ra:
  - data/topics/01-family.json                 (nguồn nội dung, tái sử dụng)
  - dist/unit-01-family_worksheet.pdf          (đề in, có chỗ viết tay + QR nghe)
  - dist/unit-01-family_answers.pdf            (đáp án + giải thích ngữ pháp)
Font: DejaVu Sans (hỗ trợ tiếng Việt).
"""
import json, os, random
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, HRFlowable, KeepInFrame)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data", "topics")
DIST_DIR = os.path.join(ROOT, "dist")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DV", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DV-I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I")

# =========================================================
# NỘI DUNG UNIT (nguồn mở: từ nền NGSL; ví dụ do tự sinh)
# words: [word, ipa, pos, meaning_vi, example, example_vi, collocations[[en,vi]...]]
# =========================================================
UNIT = {
    "unit": 1, "topic": "family", "title_en": "Family", "title_vi": "Gia đình",
    "cefr": "A1", "minutes": 30,
    "source": "wordlist: NGSL (CC BY-SA 4.0); examples/exercises: original",
    "grammar": {
        "title_vi": "Ngữ pháp trọng tâm — Grammar focus",
        "intro_vi": "Unit này luyện các điểm ngữ pháp sau. Hãy áp dụng chúng khi làm phần D và phần Viết.",
        "points": [
            ["Sở hữu (my, your, his, her, our, their) đứng TRƯỚC danh từ.",
             "my mother · his sister · their son"],
            ["have / has: I·you·we·they + have ; he·she + has (nói về thành viên gia đình).",
             "I have a brother. · She has two children."],
            ["be + a/an + danh từ (nghề nghiệp / vai trò).",
             "My father is a doctor. · My sister is a student."],
            ["Danh từ số nhiều thêm -s.",
             "one brother → two brothers · one parent → two parents"],
        ],
    },
    "words": [
        ["family", "/ˈfæm.əl.i/", "n", "gia đình", "I love my family.", "Tôi yêu gia đình tôi.",
         [["a big family", "gia đình đông người"], ["a small family", "gia đình ít người"]]],
        ["mother", "/ˈmʌð.ər/", "n", "mẹ", "My mother cooks dinner every day.", "Mẹ tôi nấu bữa tối mỗi ngày.",
         [["my mother", "mẹ tôi"], ["a good mother", "một người mẹ tốt"]]],
        ["father", "/ˈfɑː.ðər/", "n", "bố / cha", "Her father works in a bank.", "Bố cô ấy làm ở ngân hàng.",
         [["my father", "bố tôi"], ["a young father", "một người bố trẻ"]]],
        ["parents", "/ˈpeə.rənts/", "n", "bố mẹ", "My parents live in Hanoi.", "Bố mẹ tôi sống ở Hà Nội.",
         [["my parents", "bố mẹ tôi"], ["live with parents", "sống với bố mẹ"]]],
        ["brother", "/ˈbrʌð.ər/", "n", "anh / em trai", "I have one older brother.", "Tôi có một anh trai.",
         [["an older brother", "anh trai"], ["a younger brother", "em trai"]]],
        ["sister", "/ˈsɪs.tər/", "n", "chị / em gái", "My sister is a student.", "Chị/em gái tôi là học sinh.",
         [["an older sister", "chị gái"], ["a younger sister", "em gái"]]],
        ["son", "/sʌn/", "n", "con trai", "They have a son and a daughter.", "Họ có một con trai và một con gái.",
         [["their only son", "con trai duy nhất"], ["a baby son", "con trai nhỏ"]]],
        ["daughter", "/ˈdɔː.tər/", "n", "con gái", "Their daughter is five years old.", "Con gái họ năm tuổi.",
         [["their only daughter", "con gái duy nhất"], ["a baby daughter", "con gái nhỏ"]]],
        ["grandmother", "/ˈɡræn.mʌð.ər/", "n", "bà", "My grandmother tells us stories.", "Bà tôi kể chuyện cho chúng tôi.",
         [["my grandmother", "bà tôi"], ["visit grandmother", "thăm bà"]]],
        ["grandfather", "/ˈɡræn.fɑː.ðər/", "n", "ông", "My grandfather likes tea.", "Ông tôi thích trà.",
         [["my grandfather", "ông tôi"], ["visit grandfather", "thăm ông"]]],
        ["husband", "/ˈhʌz.bənd/", "n", "chồng", "Her husband is a doctor.", "Chồng cô ấy là bác sĩ.",
         [["her husband", "chồng cô ấy"], ["a good husband", "một người chồng tốt"]]],
        ["wife", "/waɪf/", "n", "vợ", "His wife works at a school.", "Vợ anh ấy làm ở trường học.",
         [["his wife", "vợ anh ấy"], ["a good wife", "một người vợ tốt"]]],
        ["baby", "/ˈbeɪ.bi/", "n", "em bé", "The baby is sleeping now.", "Em bé đang ngủ.",
         [["a new baby", "em bé mới sinh"], ["have a baby", "sinh em bé"]]],
        ["aunt", "/ɑːnt/", "n", "cô / dì / bác gái", "My aunt lives near us.", "Cô/dì tôi sống gần chúng tôi.",
         [["my aunt", "cô/dì tôi"], ["visit my aunt", "thăm cô/dì"]]],
        ["uncle", "/ˈʌŋ.kəl/", "n", "chú / bác / cậu", "My uncle has a big car.", "Chú/bác tôi có một chiếc xe to.",
         [["my uncle", "chú/bác tôi"], ["visit my uncle", "thăm chú/bác"]]],
    ],
    "mcq": [
        ["\"mother\" means:", ["bố", "mẹ", "chị gái", "bà"], 1],
        ["\"son\" means:", ["con gái", "con trai", "chồng", "em bé"], 1],
        ["\"grandfather\" means:", ["ông", "bà", "chú", "bố"], 0],
        ["\"wife\" means:", ["vợ", "chồng", "cô", "con gái"], 0],
        ["\"aunt\" means:", ["chú", "ông", "cô / dì", "anh trai"], 2],
    ],
    "matching": [
        ["daughter", "con gái"], ["husband", "chồng"], ["baby", "em bé"],
        ["parents", "bố mẹ"], ["uncle", "chú / bác / cậu"], ["sister", "chị / em gái"],
    ],
    "cloze": {
        "bank": ["mother", "father", "parents", "brother", "sister",
                 "grandmother", "husband", "baby", "family", "uncle"],
        "items": [
            ["My ______ cooks dinner every day.", "mother"],
            ["I have one older ______.", "brother"],
            ["My ______ live in Hanoi.", "parents"],
            ["The ______ is sleeping now.", "baby"],
            ["I love my ______.", "family"],
            ["Her ______ is a doctor.", "husband"],
            ["My ______ works in a bank.", "father"],
            ["My ______ tells us stories.", "grandmother"],
            ["My ______ has a big car.", "uncle"],
            ["My ______ is a student.", "sister"],
        ],
    },
    "word_order": [
        [["cooks", "mother", "My", "dinner"], "My mother cooks dinner.",
         "Trật tự cơ bản: Chủ ngữ (My mother) + Động từ (cooks) + Tân ngữ (dinner)."],
        [["have", "I", "brother", "a", "big"], "I have a big brother.",
         "Tính từ (big) đứng TRƯỚC danh từ (brother): a big brother."],
        [["is", "sister", "My", "a", "student"], "My sister is a student.",
         "Câu với 'be': Chủ ngữ + is + a + danh từ. Danh từ đếm được số ít cần 'a'."],
        [["How", "big", "is", "your", "family"], "How big is your family?",
         "Câu hỏi với 'be': từ hỏi (How big) + is + chủ ngữ (your family)?"],
        [["does", "not", "like", "My", "grandfather", "coffee"], "My grandfather does not like coffee.",
         "Phủ định thì hiện tại: chủ ngữ số ít + does not + động từ nguyên thể (like)."],
        [["father", "My", "a", "is", "teacher"], "My father is a teacher.",
         "be + a + nghề nghiệp: My father is a teacher."],
        [["two", "have", "They", "children"], "They have two children.",
         "have + danh từ số nhiều: two children (số nhiều bất quy tắc của child)."],
        [["her", "loves", "She", "parents"], "She loves her parents.",
         "Sở hữu 'her' đứng trước danh từ: her parents."],
        [["is", "brother", "His", "ten", "years", "old"], "His brother is ten years old.",
         "Nói tuổi: Chủ ngữ + is + số + years old."],
        [["Do", "have", "you", "a", "sister"], "Do you have a sister?",
         "Câu hỏi thì hiện tại với 'you': Do + you + have + ...?"],
    ],
    "listening": {
        "dictation": [
            "My father works in a bank.",
            "They have two children.",
            "My grandmother is seventy years old.",
        ],
        "choose": [
            ["daughter", ["father", "daughter", "brother"]],
            ["uncle", ["aunt", "uncle", "cousin"]],
        ],
        "audio_placeholder_url": "https://github.com/<user>/english-learning/raw/main/dist/audio/unit01/",
    },
    "reading": {
        "text": ("This is my family. We are five people. My father works in a bank, "
                 "and my mother is a teacher. I have one brother and one sister. "
                 "My brother is ten years old. My grandmother lives with us. "
                 "She tells us stories every evening. I love my family very much."),
        "questions": [
            ["There are five people in the family.", True],
            ["The mother works in a bank.", False],
            ["The writer has two brothers.", False],
            ["The grandmother lives with them.", True],
            ["The grandmother tells stories in the morning.", False],
        ],
    },
    "writing": {
        "prompt": "Write about your family (3–5 sentences).",
        "prompt_vi": "Viết về gia đình bạn (3–5 câu).",
        "questions": [
            ["How many people are there in your family?", "Gia đình bạn có mấy người?"],
            ["Who are they?", "Họ là những ai?"],
            ["What does your father / mother do?", "Bố / mẹ bạn làm nghề gì?"],
            ["Do you have any brothers or sisters?", "Bạn có anh / chị / em không?"],
            ["Who do you love most in your family?", "Bạn yêu ai nhất trong gia đình?"],
        ],
        "grammar_reminder_vi": "Nhớ dùng: sở hữu (my/his/her), have/has, be + a + nghề nghiệp.",
        "model": ("This is my family. We are four people. My father is a driver and "
                  "my mother is a nurse. I have one younger sister. I love my family very much."),
    },
}

with open(os.path.join(DATA_DIR, "01-family.json"), "w", encoding="utf-8") as f:
    json.dump(UNIT, f, ensure_ascii=False, indent=2)

# ---------- Styles ----------
def style(name, **kw):
    base = dict(fontName="DV", fontSize=10, leading=14, spaceAfter=2)
    base.update(kw); return ParagraphStyle(name, **base)
H_TITLE = style("t", fontName="DV-B", fontSize=16, leading=20, alignment=TA_CENTER)
H_SUB   = style("s", fontSize=9.5, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"))
H_SEC   = style("sec", fontName="DV-B", fontSize=11.5, leading=15, textColor=colors.HexColor("#1f4e79"), spaceBefore=8, spaceAfter=4)
P       = style("p"); P_I = style("pi", fontName="DV-I", textColor=colors.HexColor("#444444"), fontSize=9)
P_SM    = style("psm", fontSize=9, leading=12)
P_COLLO = style("collo", fontName="DV-I", fontSize=8, leading=10, textColor=colors.HexColor("#2f6db3"))

def qr_image(url, size_mm=22):
    q = qrcode.make(url); path = os.path.join(DIST_DIR, "_qr_unit01.png"); q.save(path)
    return Image(path, width=size_mm*mm, height=size_mm*mm)

def header(story):
    story.append(Paragraph(f"UNIT {UNIT['unit']} · {UNIT['title_en'].upper()} ({UNIT['title_vi']})", H_TITLE))
    story.append(Paragraph(f"Level {UNIT['cefr']}  ·  ~{UNIT['minutes']} min  ·  {len(UNIT['words'])} words", H_SUB))
    story.append(Spacer(1, 4)); story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1f4e79")))
    story.append(Spacer(1, 6))

def grammar_box(story):
    g = UNIT["grammar"]
    inner = [Paragraph(f"<b>{g['title_vi']}</b>", style("gt", fontSize=10.5, textColor=colors.HexColor("#1f4e79"))),
             Paragraph(f"<i>{g['intro_vi']}</i>", P_I)]
    for i,(txt, ex) in enumerate(g["points"], 1):
        inner.append(Paragraph(f"<b>{i}.</b> {txt}", P_SM))
        inner.append(Paragraph(f"    <font color='#2f6db3'>▸ {ex}</font>", P_SM))
    box = Table([[inner]], colWidths=[None])
    box.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#eef4fb")),
                             ("BOX",(0,0),(-1,-1),0.6,colors.HexColor("#9fbfe0")),
                             ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
                             ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story.append(box); story.append(Spacer(1, 4))

def sec(story, letter, title): story.append(Paragraph(f"{letter}. {title}", H_SEC))

TS_GRID = TableStyle([
    ("FONT",(0,0),(-1,-1),"DV",9), ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#bbbbbb")),
    ("VALIGN",(0,0),(-1,-1),"TOP"),
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e8eef6")), ("FONT",(0,0),(-1,0),"DV-B",9),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f6f8fb")]),
    ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
])

def build(answers: bool):
    fname = "unit-01-family_answers.pdf" if answers else "unit-01-family_worksheet.pdf"
    doc = SimpleDocTemplate(os.path.join(DIST_DIR, fname), pagesize=A4,
                            topMargin=13*mm, bottomMargin=13*mm, leftMargin=14*mm, rightMargin=14*mm,
                            title=f"Unit 1 Family {'Answers' if answers else 'Worksheet'}")
    letters = list("abcdefgh")
    S = []; header(S)
    if answers:
        S.append(Paragraph("ANSWER KEY — Đáp án & giải thích", style("ak", fontName="DV-B", fontSize=11, textColor=colors.HexColor("#a33"))))
        S.append(Spacer(1, 4))
    grammar_box(S)

    # --- A. Words + collocations ---
    sec(S, "A", "New words & phrases — Từ mới & cụm từ")
    if not answers:
        S.append(Paragraph("Nghe/đọc, <b>tự viết nghĩa</b>, và học thuộc các cụm từ (phrases) để nhớ tốt hơn.", P_I))
    head = ["Word", "IPA", "", "Nghĩa (tự viết)" if not answers else "Nghĩa", "Example & phrases"]
    rows = [head]
    for w in UNIT["words"]:
        word, ipa, pos, mvi, ex, exvi, collos = w
        meaning = mvi if answers else ""
        collo_html = "<br/>".join(f"<font color='#2f6db3' size='8'>▸ {c[0]} — {c[1]}</font>" for c in collos)
        ex_cell = Paragraph(f"{ex}<br/>{collo_html}", P_SM)
        rows.append([Paragraph(f"<b>{word}</b>", P_SM), Paragraph(ipa, P_SM),
                     pos, Paragraph(meaning, P_SM), ex_cell])
    t = Table(rows, colWidths=[28*mm, 26*mm, 7*mm, 30*mm, None]); t.setStyle(TS_GRID); S.append(t)

    # --- B. Matching + MCQ ---
    sec(S, "B", "Match & choose — Nối và chọn")
    rng = random.Random(7)
    right_items = [vi for en,vi in UNIT["matching"]]
    shuffled = list(enumerate(right_items)); rng.shuffle(shuffled)
    right = [f"{letters[i]}. {vi}" for i,(orig,vi) in enumerate(shuffled)]
    orig_to_letter = {orig_i: letters[new_i] for new_i,(orig_i,vi) in enumerate(shuffled)}
    left = [f"{i+1}. {en}" for i,(en,vi) in enumerate(UNIT["matching"])]
    mtable = [[Paragraph("Nối:", style("b1", fontName="DV-B", fontSize=9)), ""]]
    for i in range(len(left)):
        ans = f"  → ({orig_to_letter[i]})" if answers else "  → (   )"
        mtable.append([Paragraph(left[i]+ans, P_SM), Paragraph(right[i], P_SM)])
    mt = Table(mtable, colWidths=[85*mm, None]); mt.setStyle(TableStyle([
        ("FONT",(0,0),(-1,-1),"DV",9),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1)]))
    S.append(mt); S.append(Spacer(1, 3))
    S.append(Paragraph("Choose the correct meaning:", style("mcqh", fontName="DV-B", fontSize=9)))
    for i,(q,opts,ci) in enumerate(UNIT["mcq"]):
        parts = [f"{letters[j]}) {o} " + ("<b>[✓]</b>" if (answers and j==ci) else "( )") for j,o in enumerate(opts)]
        S.append(Paragraph(f"{i+1}. {q}  " + "   ".join(parts), P_SM))

    # --- C. Cloze ---
    sec(S, "C", "Fill in the blanks — Điền chỗ trống")
    S.append(Paragraph("Word bank: <b>" + " · ".join(UNIT["cloze"]["bank"]) + "</b>", P_SM))
    for i,(sent, ans) in enumerate(UNIT["cloze"]["items"]):
        if answers: sent = sent.replace("______", f"<b>{ans}</b>")
        S.append(Paragraph(f"{i+1}. {sent}", P_SM))

    # --- D. Word order ---
    sec(S, "D", "Put words in order — Sắp xếp từ (ngữ pháp)")
    for i,(toks, ans, note) in enumerate(UNIT["word_order"]):
        jumble = " / ".join(toks)
        if answers:
            S.append(Paragraph(f"{i+1}. [ {jumble} ]", P_SM))
            S.append(Paragraph(f"   → <b>{ans}</b>", P_SM))
            S.append(Paragraph(f"   <i>Ngữ pháp: {note}</i>", P_I))
        else:
            S.append(Paragraph(f"{i+1}. [ {jumble} ]", P_SM))
            S.append(Paragraph("   → " + "_"*58, P_SM))

    # --- E. Listening ---
    sec(S, "E", "Listening — Nghe")
    lis = UNIT["listening"]
    if not answers:
        qr = qr_image(lis["audio_placeholder_url"])
        note = Paragraph("Quét mã QR để nghe audio, rồi làm bài bên dưới.<br/>"
                         "<i>(Audio .mp3 đã sinh trong dist/audio/unit01 — QR trỏ tới thư mục audio trên repo.)</i>", P_SM)
        et = Table([[qr, note]], colWidths=[26*mm, None]); et.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        S.append(et)
    S.append(Paragraph("E1. Listen and write (dictation) — Nghe và chép lại:", style("e1", fontName="DV-B", fontSize=9)))
    for i, tr in enumerate(lis["dictation"]):
        S.append(Paragraph(f"{i+1}. <b>{tr}</b>" if answers else f"{i+1}. " + "_"*60, P_SM))
    S.append(Paragraph("E2. Listen and choose — Nghe và chọn từ đúng:", style("e2", fontName="DV-B", fontSize=9)))
    for i,(ans, opts) in enumerate(lis["choose"]):
        parts = [f"{o} " + ("<b>[✓]</b>" if (answers and o==ans) else "( )") for o in opts]
        S.append(Paragraph(f"{i+1}. " + "   ".join(parts), P_SM))

    # --- F. Reading ---
    sec(S, "F", "Reading — Đọc hiểu")
    S.append(Paragraph(UNIT["reading"]["text"], P)); S.append(Spacer(1, 2))
    S.append(Paragraph("True (T) or False (F)?", style("tf", fontName="DV-B", fontSize=9)))
    for i,(q, val) in enumerate(UNIT["reading"]["questions"]):
        if answers: S.append(Paragraph(f"{i+1}. {q}   → <b>{'T' if val else 'F'}</b>", P_SM))
        else: S.append(Paragraph(f"{i+1}. {q}   (T / F)", P_SM))

    # --- G. Writing (guiding questions) ---
    sec(S, "G", "Writing — Viết")
    wr = UNIT["writing"]
    S.append(Paragraph(f"<b>{wr['prompt']}</b>  <i>({wr['prompt_vi']})</i>", P_SM))
    S.append(Paragraph("Trả lời các câu hỏi gợi ý sau để viết thành đoạn:", P_I))
    for i,(qen, qvi) in enumerate(wr["questions"], 1):
        S.append(Paragraph(f"{i}. {qen} <font color='#666666'>({qvi})</font>", P_SM))
    S.append(Paragraph(f"<i>{wr['grammar_reminder_vi']}</i>", P_I))
    if answers:
        S.append(Paragraph("Model answer — bài mẫu:", style("mw", fontName="DV-B", fontSize=9)))
        S.append(Paragraph(wr["model"], P_I))
    else:
        for _ in range(5):
            S.append(Spacer(1, 3)); S.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#cccccc")))

    S.append(Spacer(1, 8)); S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1f4e79")))
    S.append(Paragraph("Vocabulary: NGSL (CC BY-SA 4.0). Examples, phrases, exercises & layout: original.", P_I))
    doc.build(S)
    return os.path.join(DIST_DIR, fname)

print("OK:", build(False)); print("OK:", build(True))
print("JSON:", os.path.join(DATA_DIR, "01-family.json"))
