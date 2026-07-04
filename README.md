# English Learning — Học từ vựng theo chủ đề

Website tĩnh + harness để học tiếng Anh theo chủ đề (kiểu sách từ vựng), đủ **nghe – đọc – viết – ngữ pháp**, tự kiểm tra đáp án, và tải **worksheet PDF** để in. Dùng được ở nhiều nơi qua **GitHub Pages**.

Bài tập do bạn tạo bằng harness + Claude → lưu thành `data/topics/<unit>.json` → website tự render.

## Chạy thử ở máy
Website dùng `fetch()` nên **cần một web server** (mở trực tiếp bằng `file://` sẽ không tải được dữ liệu):
```bash
cd english-learning
python3 -m http.server 8000
# mở http://localhost:8000
```

## Đăng lên web (GitHub Pages)
1. Tạo repo trên GitHub và push toàn bộ thư mục này.
2. Vào **Settings → Pages → Build and deployment → Source: Deploy from a branch**.
3. Chọn branch `main`, thư mục **/ (root)** → Save.
4. Sau ~1 phút, site chạy tại `https://<username>.github.io/<repo>/` — mở được ở mọi thiết bị.

> Sau khi có domain Pages, sửa `audio_placeholder_url` trong `harness/build_unit_family.py`
> (thay `<user>`/repo cho đúng) rồi chạy lại để QR trên worksheet trỏ đúng audio.

## Cấu trúc
```
index.html            # trang web (trang chủ + trang unit)
assets/               # app.js, style.css
data/
  units.json          # danh sách unit (website đọc file này)
  topics/*.json       # nội dung từng unit (nguồn chân lý)
harness/
  build_unit_family.py  # sinh JSON + worksheet/answer PDF
  build_audio.py        # sinh audio mp3 (edge-tts)
dist/                 # PDF + audio đã sinh (website & QR dùng)
```

## Thêm một unit mới
1. Tạo `data/topics/<id>.json` (bằng harness + Claude), theo đúng cấu trúc unit hiện có.
2. Sinh audio: `python3 harness/build_audio.py` (chỉnh trỏ tới unit mới).
3. Sinh PDF worksheet + answer key.
4. Thêm một mục vào `data/units.json` → xong, website tự hiện thẻ unit mới.

## Giấy phép
- Danh sách từ: **NGSL** (CC BY-SA 4.0) — xem `SOURCING-AND-LICENSING.md`.
- Ví dụ, bài tập, audio, code: nội dung tự sinh cho dự án.
