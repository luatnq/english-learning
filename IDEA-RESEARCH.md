# English Learning Harness — Nghiên cứu ý tưởng & Đề xuất thiết kế

> Mục tiêu: học tiếng Anh theo **chủ đề** giống các cuốn sách từ vựng nổi tiếng, có **bài tập luyện nhiều kỹ năng**, và một **cơ chế ôn tập giúp nhớ từ lâu**. Dạng: **project + harness** chạy local. Trình độ người học: **A1–A2 (sơ cấp)**.

---

## 1. Tóm tắt nhanh (TL;DR)

Ý tưởng rất khả thi và hợp với thế mạnh của một harness dùng LLM: thay vì chỉ là app flashcard tĩnh, bạn có một "gia sư" biết chấm bài viết, tạo bài tập vô hạn theo chủ đề, và giải thích bằng tiếng Việt khi cần.

Đề xuất cốt lõi:

- **Data là trung tâm, không phải code.** Mỗi chủ đề là một file (JSON/YAML) chứa danh sách từ + ví dụ. Harness đọc data để sinh bài tập và lên lịch ôn.
- **Một engine spaced repetition** (SM-2 để bắt đầu, có thể nâng lên FSRS) quyết định *hôm nay ôn từ nào*.
- **Bài tập đa dạng dựa trên "retrieval practice"** — ép não nhớ lại từ, đây là yếu tố khoa học quan trọng nhất để nhớ lâu.
- **LLM (Claude) làm 3 việc máy móc khó làm:** chấm bài viết/dịch, tạo câu ví dụ mới theo ngữ cảnh, và giải thích lỗi bằng tiếng Việt.
- **Bắt đầu nhỏ (MVP):** 1 engine ôn tập + 3 loại bài tập + 5 chủ đề đầu tiên. Mở rộng dần.

---

## 2. Cơ sở khoa học (vì sao thiết kế thế này)

Ba nguyên lý được nghiên cứu ngôn ngữ ủng hộ mạnh, và chúng định hình toàn bộ kiến trúc:

**a) Retrieval practice (luyện nhớ lại) > đọc lại.** Việc *chủ động lôi từ ra khỏi trí nhớ* hiệu quả hơn nhiều so với đọc lại danh sách. Đây gọi là "retrieval practice effect". Vì vậy harness ưu tiên bài tập bắt bạn *sản sinh* từ (điền chỗ trống, dịch, viết câu) hơn là chỉ nhận diện (chọn đáp án).

**b) Spaced repetition (ôn ngắt quãng).** Ôn lại từ *ngay trước khi sắp quên* giúp trí nhớ bền hơn nhiều so với ôn dồn. Đây là lý do cần một thuật toán lên lịch thay vì học tuần tự.

**c) Học theo chủ đề + ngữ cảnh.** Từ được nhóm theo chủ đề (gia đình, đồ ăn, công việc...) và luôn xuất hiện trong câu/đoạn có nghĩa, giống cách *English Vocabulary in Use* và *4000 Essential English Words* làm — mỗi unit ~20 từ, có ví dụ và một đoạn văn/truyện chứa các từ đó ở cuối.

Ba nguyên lý này gộp lại thành công thức: **từ theo chủ đề → gặp trong ngữ cảnh → bị ép nhớ lại nhiều lần, giãn dần theo thời gian.**

---

## 3. Chọn nguồn từ vựng

Không cần tự nghĩ ra danh sách từ. Có các bộ chuẩn, miễn phí hoặc bán chuẩn, hợp trình độ A1–A2:

| Nguồn | Quy mô | Phù hợp | Ghi chú |
|---|---|---|---|
| **NGSL** (New General Service List) | ~2.800 từ | A1–B1 | Phủ ~92% văn bản thông thường; chia sẵn theo tần suất, có block 50 từ. Bản quyền mở, dễ dùng làm data. |
| **Oxford 3000/5000** | 3.000 / 5.000 | A1–B2 | Có gắn nhãn CEFR (A1, A2...) cho từng từ — rất tiện để lọc đúng trình độ sơ cấp. |
| **4000 Essential English Words** | 6 quyển × ~600 từ | High-beginner → Advanced | Cấu trúc unit 20 từ + truyện, mô hình bài tập rất đáng học theo. |
| **English Vocabulary in Use (Elementary)** | theo chủ đề | A1–A2 | Mô hình "trang trái giải thích – trang phải luyện tập". |

**Đề xuất cho A1–A2:** lấy **Oxford 3000 lọc theo nhãn A1+A2** làm xương sống (đúng trình độ, có sẵn nhãn CEFR), rồi *tự nhóm theo chủ đề*. Mỗi chủ đề 15–25 từ, đúng nhịp một cuốn sách thật.

> Lưu ý bản quyền: nội dung *sách* có bản quyền, đừng chép nguyên. Nhưng *danh sách từ* và *ví dụ do LLM tự sinh* thì tự do dùng. Harness nên sinh ví dụ riêng thay vì copy từ sách.

---

## 4. Kiến trúc project đề xuất

```
english-learning/
├── data/
│   ├── topics/                 # mỗi chủ đề 1 file — nguồn chân lý về nội dung
│   │   ├── 01-family.json
│   │   ├── 02-food.json
│   │   └── ...
│   └── wordlists/              # nguồn thô (Oxford 3000 A1/A2, NGSL)
│
├── progress/                   # trạng thái học của bạn (git-ignored hoặc private)
│   ├── srs.json                # lịch ôn từng từ: ease, interval, due date
│   └── sessions.log            # nhật ký buổi học
│
├── harness/
│   ├── scheduler.py            # engine spaced repetition (SM-2)
│   ├── exercises/              # mỗi loại bài tập 1 module
│   │   ├── flashcard.py
│   │   ├── cloze.py            # điền chỗ trống
│   │   ├── translate.py        # Việt→Anh (chấm bằng LLM)
│   │   └── writing.py          # viết câu (chấm bằng LLM)
│   ├── session.py              # ghép: chọn từ đến hạn → chọn bài tập → chấm → cập nhật SRS
│   └── report.py               # thống kê tiến độ
│
├── skills/  hoặc  commands/    # nếu sau này đóng gói thành Cowork plugin
│   ├── learn-today.md          # "học buổi hôm nay"
│   ├── add-topic.md            # "thêm chủ đề mới X"
│   └── review-writing.md       # "chấm đoạn văn này"
│
└── README.md
```

**Nguyên tắc phân tách:** `data/` (nội dung) và `progress/` (tiến độ cá nhân) tách khỏi `harness/` (logic). Nhờ vậy bạn cập nhật thuật toán mà không đụng dữ liệu, và có thể share bộ chủ đề cho người khác mà không lộ tiến độ cá nhân.

---

## 5. Định dạng data một chủ đề (mẫu)

```json
{
  "topic": "family",
  "title_vi": "Gia đình",
  "cefr": "A1",
  "words": [
    {
      "word": "mother",
      "pos": "noun",
      "ipa": "/ˈmʌð.ər/",
      "meaning_vi": "mẹ",
      "example": "My mother cooks dinner every evening.",
      "example_vi": "Mẹ tôi nấu bữa tối mỗi buổi chiều."
    },
    {
      "word": "brother",
      "pos": "noun",
      "ipa": "/ˈbrʌð.ər/",
      "meaning_vi": "anh/em trai",
      "example": "I have one older brother.",
      "example_vi": "Tôi có một người anh trai."
    }
  ]
}
```

Trường `meaning_vi` và `example_vi` rất quan trọng ở trình độ A1–A2 — người mới cần tiếng Việt làm điểm tựa. (Xem file mẫu thật: `data/topics/01-family.sample.json`.)

---

## 6. Các loại bài tập (xếp theo độ khó nhớ)

Thiết kế theo bậc thang "nhận diện → sản sinh". Càng xuống dưới càng ép não nhiều, nhớ càng lâu:

1. **Flashcard 2 chiều** — xem `mother` → nhớ nghĩa; và ngược lại xem "mẹ" → nhớ `mother`. (Nhận diện, dễ nhất, dùng cho từ mới.)
2. **Multiple choice** — chọn nghĩa đúng trong 4 lựa chọn. (Nhận diện có nhiễu.)
3. **Cloze / điền chỗ trống** — "My ___ cooks dinner." → điền `mother`. (Bắt đầu sản sinh, có ngữ cảnh gợi ý.)
4. **Dịch Việt→Anh** — cho câu tiếng Việt, viết lại bằng tiếng Anh dùng từ mục tiêu. (Sản sinh mạnh — **LLM chấm**.)
5. **Viết câu tự do** — tự đặt một câu dùng từ mục tiêu. (Sản sinh cao nhất — **LLM chấm & sửa**.)
6. **Đọc đoạn cuối unit** — Claude sinh một đoạn ngắn A1–A2 chứa toàn bộ từ trong chủ đề + vài câu hỏi hiểu. (Củng cố trong ngữ cảnh dài, giống phần "story" của 4000 EEW.)

Engine chọn loại bài tập theo "độ chín" của từ: từ mới → flashcard/MCQ; từ đã ôn vài lần → cloze/dịch; từ đã thuộc → viết câu. Đây chính là chỗ retrieval practice phát huy tác dụng.

---

## 7. Engine ôn tập: bắt đầu với SM-2

**Vì sao SM-2 trước, FSRS sau:** SM-2 (SuperMemo, 1987) là công thức ~30 dòng, dễ implement, dễ hiểu, đủ tốt để khởi động. FSRS mới hơn, cần ~20–30% ít lần ôn hơn cho cùng mức nhớ, nhưng phức tạp hơn và cho kết quả tốt nhất khi đã có nhiều dữ liệu ôn tập của chính bạn. → Làm SM-2 cho MVP, thiết kế `scheduler.py` như một interface để sau này thay bằng FSRS mà không đụng phần còn lại.

Mỗi từ lưu 3 con số: `ease` (độ dễ), `interval` (số ngày đến lần ôn kế), `due` (ngày đến hạn). Sau mỗi lần trả lời, bạn tự chấm 0–5 (hoặc harness suy ra từ đúng/sai), engine tính lại `interval` — đúng thì giãn ra, sai thì kéo về gần.

---

## 8. Luồng một buổi học ("learn-today")

```
1. scheduler đọc progress/srs.json → lấy các từ "đến hạn hôm nay"
   + thêm N từ mới từ chủ đề đang học (mặc định 5 từ mới/ngày).
2. Với mỗi từ, session chọn loại bài tập theo độ chín.
3. Người học trả lời:
      - bài trắc nghiệm/cloze: harness tự chấm.
      - bài dịch/viết: gửi cho Claude chấm, trả về sửa lỗi + giải thích tiếng Việt.
4. Cập nhật SRS cho từng từ; ghi sessions.log.
5. Cuối buổi: đoạn đọc ngắn chứa các từ hôm nay + 3 câu hỏi.
6. report tóm tắt: học bao nhiêu từ mới, tỉ lệ đúng, chuỗi ngày liên tục.
```

Có thể gắn **scheduled task** để mỗi sáng tự nhắc "buổi học hôm nay có 12 từ đến hạn".

---

## 9. Vai trò của LLM (điểm khác biệt so với Anki thuần)

Một app flashcard tĩnh không làm được những việc này, nhưng harness dùng Claude thì có:

- **Chấm bài viết/dịch** và giải thích lỗi bằng tiếng Việt, gợi ý cách nói tự nhiên hơn.
- **Sinh ví dụ mới vô hạn** cho một từ theo nhiều ngữ cảnh (chống học vẹt đúng một câu).
- **Tạo chủ đề mới theo yêu cầu:** "thêm chủ đề Sân bay 20 từ A2" → tự sinh file data.
- **Sinh đoạn đọc cuối unit** vừa trình độ, chứa đúng các từ mục tiêu.
- **Trả lời thắc mắc** kiểu "khác nhau giữa `make` và `do`?" ngay trong lúc học.

---

## 10. Roadmap đề xuất

**MVP (tuần 1) — chứng minh vòng lặp học chạy được:**
- `scheduler.py` với SM-2.
- 3 loại bài tập: flashcard, cloze, dịch Việt→Anh (Claude chấm).
- 5 chủ đề đầu (family, food, house, daily routine, numbers/time), mỗi cái ~15 từ lấy từ Oxford 3000 A1.
- Lệnh `learn-today` chạy một buổi hoàn chỉnh + lưu tiến độ.

**V2 — làm dày trải nghiệm:**
- Thêm bài viết tự do + đoạn đọc cuối unit.
- `report` thống kê + chuỗi ngày (streak).
- 15–20 chủ đề.

**V3 — tối ưu & đóng gói:**
- Nâng scheduler lên FSRS.
- Scheduled task nhắc học mỗi sáng.
- Đóng gói thành Cowork plugin (skills/commands) để gọi bằng lệnh tự nhiên.
- Tuỳ chọn: thêm phát âm (TTS) và luyện nghe.

---

## 11. Rủi ro & lưu ý

- **Bản quyền:** dùng *danh sách từ* (tự do) chứ không chép *nội dung sách*; để Claude sinh ví dụ riêng.
- **Đừng over-engineer:** cám dỗ lớn nhất là xây UI đẹp/thuật toán phức tạp trước khi vòng lặp học chạy. Ưu tiên MVP chữ (CLI) chạy được, đẹp tính sau.
- **Chất lượng data:** ví dụ và nghĩa tiếng Việt cần được kiểm tra — sai một từ vựng gốc là học sai theo. Nên có bước rà lại data mới sinh.
- **Động lực học:** streak + báo cáo tiến độ + mục tiêu nhỏ (5 từ/ngày) quan trọng ngang thuật toán. Nhớ được từ hay không, phần lớn là học đều mỗi ngày.

---

## Nguồn tham khảo

- [4000 Essential English Words (Paul Nation, Compass)](https://www.essentialenglish.review/4000-essential-english-words-1)
- [The 11 Best English Vocabulary Books — StoryLearning](https://storylearning.com/learn/english/english-tips/best-english-vocabulary-books)
- [FSRS vs SM-2: Which Spaced Repetition Algorithm Wins (2026)](https://flica.app/article/fsrs-vs-sm2)
- [Spaced Repetition Algorithm: SM-2 vs FSRS Explained — Kachika](https://kachika.app/en/blog/spaced-repetition-algorithms/)
- [The Effect of Exercise Types on EFL Learners' Vocabulary Retention](https://www.academypublication.com/issues/past/tpls/vol02/08/24.pdf)
- [Oxford 3000 Vocabulary — Quizlet Study Guide](https://quizlet.com/study-guides/oxford-3000-vocabulary-essential-words-for-english-learners-f600fbb7-ace7-47f3-b6cf-42bd6a98fe06)
- [Vocabulary Learning in a Second Language — TESL-EJ](https://tesl-ej.org/ej26wp/a4.html)
