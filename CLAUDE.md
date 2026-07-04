# CLAUDE.md — Ngữ cảnh dự án `english-learning`

> File này để Claude Code (và bất kỳ AI/người mới nào) hiểu nhanh dự án. Đọc file này trước khi làm việc.
> Tài liệu thiết kế sâu hơn: `IDEA-RESEARCH.md`, `EXERCISE-DESIGN.md`, `SOURCING-AND-LICENSING.md`, `README.md`.

## 1. Dự án là gì

Một **bộ học từ vựng tiếng Anh theo chủ đề** (kiểu sách từ vựng), gồm:
- **Website tĩnh** (`index.html` + `assets/`) để học online: nghe, làm bài, **tự kiểm tra đáp án**. Deploy bằng **GitHub Pages**, dùng được ở nhiều thiết bị.
- **Harness** (`harness/*.py`) để sinh nội dung: file dữ liệu unit (JSON), **worksheet PDF + answer key** để in, và **audio mp3** cho phần nghe.

Người dùng: người học **trình độ A1–A2** (sơ cấp), tiếng Việt là ngôn ngữ mẹ đẻ nên nội dung có tiếng Việt hỗ trợ.

## 2. Nguyên tắc & ràng buộc (QUAN TRỌNG)

- **KHÔNG có AI chấm bài.** Website chỉ tự chấm bằng cách so đáp án (matching, MCQ, cloze, word-order, dictation, T/F). Phần viết chỉ hiện **câu hỏi gợi ý + bài mẫu**, không chấm.
- **Nội dung bài tập do người dùng tạo** bằng harness + Claude, lưu thành `data/topics/<id>.json`. Website đọc JSON để render — thêm unit KHÔNG cần sửa code.
- **Bản quyền (repo public):** từ vựng lấy nền **NGSL** (CC BY-SA 4.0), tự nhóm chủ đề. KHÔNG chép cấu trúc/nội dung sách có bản quyền (người dùng học *Collins Work on Your Vocabulary* nhưng chỉ tham khảo cá nhân). Ví dụ/bài tập/audio là nội dung tự sinh. Chi tiết: `SOURCING-AND-LICENSING.md`.
- **Giấy phép:** code = MIT; nội dung học = CC BY-SA 4.0.
- **Giữ đơn giản.** Vanilla JS, không framework, không build step cho web. Ưu tiên chạy được hơn là hoa mỹ.

## 3. Cấu trúc thư mục

```
index.html                 # web: trang chủ + trang unit (hash router #/  và  #/unit/<id>)
assets/app.js              # toàn bộ logic render + tự chấm (vanilla JS)
assets/style.css
data/
  units.json               # MANIFEST: danh sách unit cho website đọc
  topics/<id>.json         # nội dung từng unit (NGUỒN CHÂN LÝ)
harness/
  build_unit_family.py     # (demo) định nghĩa nội dung Unit 1 + render JSON & PDF
  build_audio.py           # sinh audio mp3 từ unit.json bằng edge-tts
dist/
  unit-01-family_worksheet.pdf
  unit-01-family_answers.pdf
  audio/unit01/            # e1_*.mp3 (dictation), e2_*.mp3 (choose), reading.mp3, words/<slug>.mp3
progress/                  # (tùy chọn) tiến độ cá nhân — .gitignore, KHÔNG public
```

## 4. Cấu trúc một unit — `data/topics/<id>.json`

Đây là hợp đồng dữ liệu (data contract). Website và PDF đều đọc đúng các trường này. Mảng dùng **thứ tự cố định** (không phải object) cho gọn:

```jsonc
{
  "unit": 1, "topic": "family", "title_en": "Family", "title_vi": "Gia đình",
  "cefr": "A1", "minutes": 30,
  "source": "wordlist: NGSL (CC BY-SA 4.0); examples/exercises: original",

  "grammar": {                          // Box "Ngữ pháp trọng tâm" đầu unit
    "title_vi": "Ngữ pháp trọng tâm — Grammar focus",
    "intro_vi": "…",
    "points": [ ["mô tả điểm ngữ pháp (vi)", "ví dụ minh hoạ (en)"], … ]
  },

  "words": [
    // [ word, ipa, pos, meaning_vi, example_en, example_vi, collocations ]
    // collocations = [ [phrase_en, phrase_vi], … ]  (thường 2 cụm/từ)
    ["family","/ˈfæm.əl.i/","n","gia đình","I love my family.","Tôi yêu gia đình tôi.",
      [["a big family","gia đình đông người"],["a small family","gia đình ít người"]]],
    …
  ],

  "mcq": [ ["\"mother\" means:", ["bố","mẹ","chị gái","bà"], 1], … ],   // [câu, [4 lựa chọn], index_đúng]
  "matching": [ ["daughter","con gái"], … ],                           // [en, vi]

  "cloze": {
    "bank": ["mother","father", …],
    "items": [ ["My ______ cooks dinner every day.", "mother"], … ]    // "______" = chỗ trống; phần tử 2 = đáp án
  },

  "word_order": [
    // [ [tokens xáo trộn], câu_đúng, giải_thích_ngữ_pháp_vi ]
    [["cooks","mother","My","dinner"], "My mother cooks dinner.", "Chủ ngữ + Động từ + Tân ngữ."], …
  ],

  "listening": {
    "dictation": [ "My father works in a bank.", … ],                  // transcript = đáp án; audio e1_<n>.mp3
    "choose":    [ ["daughter", ["father","daughter","brother"]], … ], // [từ_phát_ra, [lựa chọn]]; audio e2_<n>.mp3
    "audio_placeholder_url": "https://github.com/<user>/english-learning/raw/main/dist/audio/unit01/"
  },

  "reading": {
    "text": "…",
    "questions": [ ["There are five people in the family.", true], … ] // [câu, đúng?(bool)]  → T/F
  },

  "writing": {
    "prompt": "Write about your family (3–5 sentences).",
    "prompt_vi": "Viết về gia đình bạn (3–5 câu).",
    "questions": [ ["How many people are there in your family?", "Gia đình bạn có mấy người?"], … ], // câu hỏi gợi ý
    "grammar_reminder_vi": "Nhớ dùng: sở hữu (my/his/her), have/has, be + a + nghề nghiệp.",
    "model": "…"                                                       // bài mẫu (hiện khi bấm "Xem bài mẫu")
  }
}
```

### Manifest — `data/units.json`
Website đọc file này để hiện các thẻ unit ở trang chủ:
```jsonc
[ { "id":"01-family", "title_en":"Family", "title_vi":"Gia đình", "cefr":"A1",
    "words":15, "json":"data/topics/01-family.json",
    "audioDir":"dist/audio/unit01/",
    "worksheet":"dist/unit-01-family_worksheet.pdf",
    "answers":"dist/unit-01-family_answers.pdf" } ]
```

## 5. Website (render 8 phần)

`assets/app.js` là SPA nhỏ, router theo hash. Mỗi unit render theo thứ tự: **Box ngữ pháp** → **A** New words & phrases (bảng từ + collocations, nút 🔊, ẩn/hiện nghĩa) → **B** Matching + MCQ → **C** Cloze (10) → **D** Word order (10, hiện giải thích ngữ pháp khi kiểm tra) → **E** Listening (E1 dictation + E2 choose, có nút ▶) → **F** Reading (▶ nghe + T/F) → **G** Writing (câu hỏi gợi ý + nhắc ngữ pháp + textarea + nút "Xem bài mẫu").

Tự chấm: nút **"Kiểm tra"** mỗi phần → tô xanh/đỏ + hiện điểm `x/n`. So khớp chuẩn hoá bằng `App.norm()` (lowercase, bỏ dấu câu, gộp khoảng trắng).

Website dùng `fetch()` → **phải chạy qua web server** (không mở `file://`). Test local: `python3 -m http.server 8000`.

## 6. Audio — quy ước tên file

Trong `dist/audio/unit<NN>/`:
- `e1_<i>.mp3` — câu dictation thứ i (Section E1).
- `e2_<i>.mp3` — từ "listen & choose" thứ i (E2).
- `reading.mp3` — đoạn đọc Section F.
- `words/<slug>.mp3` — phát âm từng từ ("từ + câu ví dụ"). `slug` = lowercase, ký tự không phải a-z0-9 → `-`.

Sinh bằng `harness/build_audio.py` (edge-tts, giọng `en-US-AriaNeural`, `rate="-12%"`). Cần mạng + `ffmpeg`.

## 7. Quy trình thêm một unit mới (end-to-end)

1. Tạo `data/topics/<id>.json` đúng schema mục 4 (dùng Claude sinh nội dung; từ vựng lấy từ NGSL).
2. Sinh audio: chỉnh `build_audio.py` trỏ tới unit mới → `python3 harness/build_audio.py`.
3. Sinh worksheet + answer PDF (xem mục 8 — hiện đang gắn với Unit 1, cần tổng quát hoá).
4. Thêm một mục vào `data/units.json`.
5. Xong — website tự hiện thẻ unit mới; không sửa code web.

## 8. Nợ kỹ thuật / việc nên làm tiếp (cho Claude Code)

- **Tổng quát hoá builder PDF.** Hiện `harness/build_unit_family.py` **vừa chứa nội dung Unit 1 vừa render PDF**. Nên tách thành: (a) nội dung chỉ nằm trong `data/topics/*.json`; (b) một script chung `harness/render_pdf.py <unit.json>` đọc JSON bất kỳ và xuất worksheet + answer key. Tương tự, `build_audio.py` nên nhận tham số `<unit.json>` thay vì hard-code Unit 1.
- **Cập nhật QR.** Sau khi deploy Pages, thay `<user>`/repo trong `audio_placeholder_url` để QR trỏ đúng audio, rồi build lại PDF.
- **Thêm unit:** Food, House, Daily routine… theo đúng khuôn Unit 1.
- **Spaced repetition (tuỳ chọn):** lưu tiến độ trong `localStorage`, lên lịch ôn từ (bắt đầu SM-2). Chưa làm.
- Giữ nguyên tắc mục 2 khi mở rộng (không AI chấm, nguồn mở, đơn giản).

## 9. Lệnh hay dùng

```bash
# chạy web local
python3 -m http.server 8000

# sinh lại Unit 1 (JSON + PDF)
python3 harness/build_unit_family.py

# sinh audio
python3 harness/build_audio.py

# yêu cầu: pip install reportlab qrcode[pil] edge-tts  ; và ffmpeg, font DejaVu
```

## 10. Trạng thái hiện tại

Xong: 3 tài liệu thiết kế; **Unit 1 Family** đầy đủ (JSON + 2 PDF + 21 mp3); website tĩnh (đã test bằng jsdom). Chưa: push GitHub + bật Pages; tổng quát hoá builder; thêm unit khác.
