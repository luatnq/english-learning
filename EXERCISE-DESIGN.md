# Cấu trúc bài tập kiểu sách từ vựng — 4 kỹ năng + Ngữ pháp + Xuất PDF

> Mở rộng từ `IDEA-RESEARCH.md`. Tài liệu này định nghĩa **một "unit" học giống một chương sách từ vựng thật**, có đủ đọc – nghe – viết – ngữ pháp, chạy được ở cả **2 chế độ**: học tương tác trên máy, và **in ra giấy làm bằng bút**.

---

## 1. Ý tưởng lớn: một "unit" = một chương sách

Các cuốn nổi tiếng (*4000 Essential English Words*, *English Vocabulary in Use*, *Oxford Word Skills*) đều theo một khuôn: **giới thiệu từ → luyện nhận diện → luyện dùng → đọc/nghe trong ngữ cảnh → tự sản sinh**. Ta chép đúng khuôn đó thành **7 section cố định** cho mỗi chủ đề:

| Section | Tên | Kỹ năng chính | Chấm thế nào |
|---|---|---|---|
| **A** | Từ mới (Word list) | Nhận diện | — (chỉ đọc + nghe mẫu) |
| **B** | Ghép & chọn nghĩa (Matching / MCQ) | Nhận diện | Tự động |
| **C** | Điền chỗ trống (Cloze) | Sản sinh có gợi ý | Tự động |
| **D** | Sắp xếp từ thành câu (Word order) | **Ngữ pháp** | Tự động |
| **E** | Nghe (Listening) | Nghe | Tự động (chép chính tả) / LLM |
| **F** | Đọc hiểu (Reading) | Đọc | Tự động + LLM |
| **G** | Viết (Writing) | Sản sinh tự do | **LLM chấm** |

Thứ tự A→G đi từ dễ đến khó, đúng nhịp "nhận diện → sản sinh" đã nói ở tài liệu gốc. Một unit ~15–20 từ, làm trọn trong 20–30 phút.

Mỗi section là một **exercise generator** trong `harness/exercises/`, đọc data chủ đề và sinh bài. Nhờ tách theo section, bạn bật/tắt hoặc thêm loại bài mà không phá phần khác.

---

## 2. Chi tiết từng loại bài tập (kèm ví dụ chủ đề "Family")

### Section A — Word list (giới thiệu từ)
Bảng từ: `word · IPA · loại từ · nghĩa Việt · câu ví dụ`. Bản digital có nút phát âm (TTS). Bản in có cột IPA + ô trống để tự viết nghĩa (ép nhớ chủ động thay vì chỉ đọc).

### Section B — Matching / Multiple choice
- **Matching:** nối cột Anh ↔ cột Việt (xáo thứ tự).
- **MCQ:** "*mother* means: (a) bố (b) **mẹ** (c) anh trai (d) bà".
> Chấm tự động. Đây là bước "làm nóng", nhận diện từ.

### Section C — Cloze (điền chỗ trống)
Câu có ngữ cảnh, khoét từ mục tiêu, có **word bank** ở đầu (dễ hơn cho A1–A2):
```
Word bank: mother · brother · parents · family
1. My ______ cooks dinner every evening.        (mother)
2. I have one older ______.                       (brother)
3. We are a small ______ of four.                 (family)
```

### Section D — Word order / sắp xếp từ (học ngữ pháp) ⭐
Đây chính là phần bạn muốn — vừa ôn từ vừa nắm **trật tự câu tiếng Anh** (S-V-O, vị trí tính từ, trợ động từ...). Cho các từ xáo trộn, người học sắp lại thành câu đúng:
```
1. [ cooks / mother / My / dinner ]        → My mother cooks dinner.
2. [ brother / have / I / a / big ]        → I have a big brother.
3. [ your / is / How / family / big ]?     → How big is your family?
```
Chấm tự động bằng cách so khớp với câu đúng; nếu sai, **Claude giải thích lỗi ngữ pháp bằng tiếng Việt** (vd: "tính từ *big* đứng trước danh từ"). Có thể nâng cấp thành **transformation** (đổi câu sang phủ định/nghi vấn) khi lên A2.

### Section E — Listening (nghe)
Ba dạng, tăng dần độ khó:
- **Nghe – chọn từ:** phát 1 từ → chọn/khoanh đúng từ trong 4 lựa chọn.
- **Nghe – chép chính tả (dictation):** phát 1 câu → viết lại. (Rèn nghe + chính tả cùng lúc; đáp án chính là transcript nên **chấm tự động** được.)
- **Nghe – trả lời câu hỏi:** phát 1 đoạn ngắn → trả lời câu hỏi hiểu.

Âm thanh do **TTS sinh sẵn thành file `.mp3`** khi build unit (xem §4 cách xử lý cho bản in).

### Section F — Reading (đọc hiểu)
Claude sinh **một đoạn ngắn A1–A2 chứa toàn bộ từ của unit** (giống phần "story" cuối mỗi unit của *4000 Essential Words*), kèm:
- 3–4 câu hỏi True/False hoặc chọn đáp án (chấm tự động).
- 1 câu hỏi mở "trả lời theo bạn" (LLM chấm nhẹ, khích lệ).

### Section G — Writing (viết)
- **Viết câu:** đặt câu với 3 từ bất kỳ trong unit.
- **Viết đoạn ngắn:** "Viết 3–4 câu về gia đình bạn." → **Claude chấm**: sửa lỗi, chấm sao 1–5, gợi ý câu tự nhiên hơn, giải thích bằng tiếng Việt.

---

## 3. Hai chế độ chạy: Digital vs. Print

Cùng một unit, hai đầu ra:

**Chế độ Digital (interactive):**
- Làm trực tiếp, phát audio bằng loa, LLM chấm bài viết ngay.
- Kết quả cập nhật vào SRS (`progress/srs.json`) → lịch ôn thông minh.

**Chế độ Print (worksheet PDF):**
- Xuất **2 file**: `unit-01-family_worksheet.pdf` (đề, có chỗ trống để viết tay) và `unit-01-family_answers.pdf` (đáp án + giải thích).
- Không có SRS realtime; sau khi làm giấy xong có thể nhập nhanh kết quả để cập nhật lịch (tuỳ chọn).

Điểm mấu chốt: **cùng một `unit.json` sinh ra cả hai** — chỉ khác renderer. Không viết nội dung hai lần.

---

## 4. Xử lý "nghe trên giấy in" (vấn đề khó nhất)

Tờ giấy không phát tiếng, nên bản Print dùng 3 cách kết hợp:

1. **File audio đi kèm:** khi export, sinh thư mục `audio/unit-01/` chứa các `.mp3`. Bạn mở trên điện thoại/máy tính và làm bài giấy song song — đúng kiểu "sách + đĩa CD" ngày xưa.
2. **Mã QR trên worksheet:** mỗi bài nghe in kèm một **QR code** trỏ tới file audio tương ứng (đặt trong thư mục chia sẻ hoặc local server). Quét là nghe — không cần tìm file thủ công.
3. **Dictation là chủ lực cho bản in:** vì đáp án chép chính tả = transcript, người học tự đối chiếu với answer key rất dễ, không cần chấm máy.

> Nếu không muốn phụ thuộc audio, worksheet in có thể thay Section E bằng bài "đọc to" (đọc câu, tự kiểm phát âm bằng transcript IPA) — nhưng khuyến nghị giữ audio + QR vì rèn nghe thật.

---

## 5. Bố cục một tờ worksheet in (phác thảo)

```
┌──────────────────────────────────────────────┐
│  UNIT 1 · FAMILY (Gia đình)          A1  ⏱25' │
├──────────────────────────────────────────────┤
│  A. New words   mother /ˈmʌðər/  (n) mẹ ____  │   ← cột nghĩa để trống
│                 father /ˈfɑːðər/ (n) ___ ____  │
│  ...                                           │
│  B. Match:   1-mother  ( )   a. anh/em trai    │
│              2-brother ( )   b. mẹ             │
│  C. Cloze:   My ______ cooks dinner.           │
│  D. Order:   [cooks/mother/My/dinner] ______   │
│  E. Listen ▶ [QR]  Write what you hear: ______ │
│  F. Read:   <đoạn văn>  →  T/F questions        │
│  G. Write:  3–4 sentences about your family:    │
│             ________________________________    │
└──────────────────────────────────────────────┘
```
Answer key in riêng, kèm giải thích ngữ pháp phần D và gợi ý phần G.

---

## 6. Pipeline kỹ thuật

```
unit.json  ──►  build_unit.py
                 ├─ sinh nội dung còn thiếu (đoạn đọc, câu hỏi) qua Claude
                 ├─ sinh audio TTS  ──►  audio/unit-01/*.mp3  (+ QR)
                 ├─ render Digital  ──►  phiên học tương tác
                 └─ render Print    ──►  worksheet.pdf + answers.pdf
```

- **Sinh nội dung động** (đoạn đọc, câu hỏi, transcript): Claude, một lần lúc build, rồi cache vào `unit.json` để lần sau in lại không cần gọi lại.
- **TTS:** có thể dùng thư viện offline (vd `edge-tts`, `piper`) để tạo mp3; chọn giọng chuẩn, tốc độ chậm cho A1–A2.
- **Xuất PDF:** dùng **`pdf` skill** có sẵn của mình — tạo worksheet bố cục sạch, khoảng trống viết tay hợp lý, và QR code cho bài nghe.
- **QR:** thư viện `qrcode` (Python) trỏ tới đường dẫn audio.

---

## 7. Tác động lên cấu trúc data

Bổ sung nhẹ vào `unit.json` so với bản ở tài liệu gốc — thêm phần nội dung sinh sẵn để tái tạo được worksheet:

```jsonc
{
  "topic": "family",
  "cefr": "A1",
  "words": [ /* như cũ: word, ipa, meaning_vi, example... */ ],
  "generated": {                       // Claude sinh 1 lần, cache lại
    "reading": { "text": "...", "questions": [ /* T/F */ ] },
    "listening": [ { "audio": "audio/unit-01/e1.mp3",
                     "transcript": "My mother cooks dinner." } ],
    "word_order": [ { "tokens": ["cooks","mother","My","dinner"],
                      "answer": "My mother cooks dinner.",
                      "grammar_note_vi": "Chủ ngữ + động từ + tân ngữ." } ]
  }
}
```

---

## 8. Đề xuất roadmap cập nhật

**MVP+ (làm ngay):** dựng **1 unit "Family" hoàn chỉnh** đủ 7 section, xuất ra **worksheet PDF + answer key** thật để bạn in thử. Đây là cách nhanh nhất kiểm chứng cả trải nghiệm giấy.

**Sau đó:** thêm TTS + QR cho phần nghe → chế độ digital chấm bằng LLM → nhân bản sang 5 chủ đề đầu.

---

## Kết luận ngắn

Cấu trúc 7-section (A→G) cho bạn đúng cảm giác một cuốn sách từ vựng: có đọc, nghe, viết, và phần **sắp xếp từ để học ngữ pháp**. Mấu chốt thiết kế là **một `unit.json` → hai đầu ra** (digital + PDF in), và **giải bài nghe trên giấy bằng audio + QR + chép chính tả**. Bước tiếp hợp lý nhất là mình dựng thử một unit hoàn chỉnh và xuất PDF để bạn cầm trên tay đánh giá.
