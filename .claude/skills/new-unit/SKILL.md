---
name: new-unit
description: Tạo bài học từ vựng end-to-end cho dự án english-learning. Kích hoạt khi người dùng nói "tạo unit mới", "tạo bài học mới", "new unit", "new lesson", "làm bài kế tiếp", "/new-unit", hoặc nêu tên chủ đề (vd "tạo unit Food"). CŨNG kích hoạt cho chế độ ÔN TẬP unit cũ: "luyện tập <chủ đề>", "ôn tập <chủ đề>", "thêm bài cho unit <chủ đề>", "bài mới cho unit cũ" — sinh biến thể (variant) cùng bộ từ nhưng bài tập mới. Skill tự chọn bài, sinh JSON đúng schema, rồi build PDF/audio/manifest bằng một lệnh.
---

# Tạo unit mới (english-learning)

Mục tiêu: từ một lời gọi ngắn, tạo ra một unit hoàn chỉnh chạy được trên website. Người dùng KHÔNG phải mô tả nhiều — bạn tự soi lộ trình + lịch sử để quyết định.

## Bối cảnh bắt buộc đọc trước
- `CLAUDE.md` §2 (nguyên tắc) và §4 (data contract — nguồn chân lý về schema).
- `data/topics/01-family.json` — **mẫu vàng**: unit mới phải cùng cấu trúc & độ chi tiết.
- `data/curriculum.json` — lộ trình A1→A2 (kế hoạch chủ đề + trọng tâm ngữ pháp).

## Quy trình 4 bước

### Bước 1 — Chọn unit kế tiếp (soi lịch sử)
Chạy để biết đã có unit nào:
```bash
ls data/topics/*.json          # lịch sử: unit đã tạo
cat data/curriculum.json       # kế hoạch: chủ đề + level + grammar
```
- Nếu người dùng **nêu tên chủ đề cụ thể** → làm chủ đề đó (khớp `id` trong curriculum nếu có).
- Nếu **không nêu** → chọn unit có `unit` **nhỏ nhất trong curriculum mà CHƯA có file** `data/topics/<id>.json`.
- **Báo người dùng lựa chọn** trước khi sinh: "Sẽ tạo Unit N — <title_en> (<cefr>), trọng tâm ngữ pháp: …". Chỉ hỏi lại nếu thật sự mơ hồ.

### Bước 2 — Sinh nội dung `data/topics/<id>.json`
Viết file JSON **đúng data contract §4**, bám sát `01-family.json` về hình thức. Số lượng chuẩn (để bài đủ dày và validator qua):

| Phần | Yêu cầu |
|---|---|
| `grammar` | `title_vi`, `intro_vi`, và **4 points** `[mô_tả_vi, ví_dụ_en]` — đúng trọng tâm ngữ pháp của unit trong curriculum |
| `words` | **~15 từ**, mỗi từ ĐÚNG 7 phần tử: `[word, ipa, pos, meaning_vi, example_en, example_vi, collocations]`; `collocations` = **2 cụm** `[phrase_en, phrase_vi]` |
| `mcq` | **5 câu** `[câu, [4 lựa chọn], index_đúng]` |
| `matching` | **6 cặp** `[en, vi]` |
| `cloze` | `bank` **~10 từ** + **10 items** `[câu_có "______", đáp_án]`; đáp án phải nằm trong `bank` |
| `word_order` | **10 câu** `[[tokens xáo trộn], câu_đúng, giải_thích_ngữ_pháp_vi]`; tokens phải ghép đúng ra câu_đúng |
| `listening` | `dictation` **3 câu**, `choose` **2 mục** `[từ_đúng, [3 lựa chọn]]` (từ_đúng ∈ lựa chọn), và `audio_placeholder_url` = `https://github.com/luatnq/english-learning/raw/main/dist/audio/<id>/` (vd `.../dist/audio/02-numbers-time/`) |
| `reading` | `text` (đoạn ngắn đúng level) + **5 câu** T/F `[câu, true/false]` |
| `writing` | `prompt`, `prompt_vi`, **5 câu hỏi gợi ý** `[en, vi]`, `grammar_reminder_vi`, `model` (bài mẫu 3–5 câu) |

Đặt `"unit": N`, `"topic"`, `"title_en"`, `"title_vi"`, `"cefr"`, `"minutes"`, `"source": "wordlist: NGSL (CC BY-SA 4.0); examples/exercises: original"`.

**Quality bar (bám nguyên tắc §2):**
- Từ vựng lấy nền **NGSL** (từ phổ biến, hợp chủ đề & level). KHÔNG chép cấu trúc/nội dung sách có bản quyền.
- Ví dụ, câu bài tập, đoạn đọc, bài mẫu: **tự sinh (original)**, câu ĐƠN GIẢN đúng A1/A2, dùng đúng ngữ pháp trọng tâm của unit.
- Mọi nghĩa/giải thích có **tiếng Việt** (người học là người Việt sơ cấp).
- IPA chuẩn; `pos` gọn (n/v/adj/adv…).

### Bước 3 — Build (một lệnh)
```bash
python3 harness/build_unit.py data/topics/<id>.json
```
Lệnh này: **validate → manifest → PDF → audio**. Trong đó validate + manifest luôn chạy (web cập nhật ngay); PDF cần `.venv` (reportlab), audio cần `edge-tts` + mạng (không cần ffmpeg) — nếu thiếu sẽ tự bỏ qua và in hướng dẫn, KHÔNG lỗi.
- Nếu validate báo lỗi → **sửa file JSON** rồi chạy lại (đừng bỏ qua lỗi).
- Chỉ web (bỏ PDF/audio nhanh): thêm `--no-audio` / `--no-pdf`.

### Bước 4 — Báo cáo
Tóm tắt cho người dùng: unit nào đã tạo, file JSON + PDF + (audio nếu có), số từ, và:
```bash
python3 -m http.server 8000   # xem tại http://localhost:8000  (đừng mở file:// — web dùng fetch)
```
Nhắc: unit tự hiện trên trang chủ vì đã vào `data/units.json`; site live tự deploy khi push `main`.

## Chế độ ÔN TẬP — biến thể unit cũ (variant)
Khi người dùng muốn **học lại một chủ đề đã có** với bài tập mới ("luyện tập Family", "ôn tập <chủ đề>", "thêm bài cho unit <chủ đề>"):

1. **Tìm unit gốc**: `data/topics/<NN>-<topic>.json` (khớp `id` trong curriculum, vd `01-family`).
2. **Đặt id biến thể**: `<NN>-<topic>-p<k>` với `k` = (số biến thể đã có) + 2. Ví dụ biến thể đầu của Family → `01-family-p2`, tiếp theo → `01-family-p3`. (Kiểm tra: `ls data/topics/<NN>-<topic>-p*.json`.)
3. **Dùng lại nguyên `words` và `grammar`** của unit gốc (cùng bộ từ, cùng trọng tâm ngữ pháp — mục tiêu là ôn tập).
4. **Sinh MỚI toàn bộ bài tập** chỉ từ bộ từ đó, KHÁC bản gốc để không lộ đáp án cũ: `mcq`, `matching`, `cloze`, `word_order`, `listening` (dictation + choose), `reading`, `writing`. Cùng độ khó/level.
5. Đặt `title_en` = "<gốc> — Practice k", `title_vi` = "<gốc> — Luyện tập k"; giữ `unit`, `cefr`, `minutes` như gốc; `audio_placeholder_url` trỏ `.../dist/audio/<NN>-<topic>-p<k>/`.
6. Build như thường: `python3 harness/build_unit.py data/topics/<NN>-<topic>-p<k>.json`.

Biến thể hiện như một thẻ riêng trên web (ngay sau unit gốc do sắp xếp theo id). Không sửa code web.

## Nguyên tắc bất biến (KHÔNG vi phạm)
- **KHÔNG có AI chấm bài** — mọi phần phải tự chấm bằng so đáp án. Phần viết chỉ có câu gợi ý + bài mẫu.
- **Nội dung nằm hoàn toàn trong JSON** — không hard-code nội dung vào code/harness. Thêm unit KHÔNG sửa code web.
- Nguồn mở (NGSL CC BY-SA), giữ đơn giản.
