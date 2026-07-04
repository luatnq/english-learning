# Nguồn từ vựng & Giấy phép — Hướng dẫn cho repo public

> Tài liệu này giúp dự án **public trên GitHub một cách sạch về bản quyền**, để có thể dùng làm nguồn tài liệu mở, truy cập được nhiều nơi.
>
> ⚠️ Đây là hướng dẫn thực hành, **không phải tư vấn pháp lý**. Với dự án phân phối rộng, nếu cần chắc chắn tuyệt đối hãy hỏi ý kiến luật sư.

---

## 1. Nguyên tắc bản quyền (tóm tắt)

| Thứ | Bản quyền? | Được đăng public? |
|---|---|---|
| Một **từ đơn lẻ** | Không | ✅ Được |
| **Cách chọn + nhóm từ theo unit** của một cuốn sách cụ thể | Có thể (compilation copyright) | ❌ Không chép nguyên si |
| **Định nghĩa, ví dụ, bài tập, đoạn đọc** trong sách | Có | ❌ Không |
| **Wordlist nguồn mở** (vd NGSL) | Có, nhưng giấy phép mở | ✅ Được, kèm ghi công |
| **Ví dụ / bài tập / audio do bạn hoặc LLM tự sinh** | Của bạn | ✅ Được |

**Kết luận:** dùng *từ* thì tự do, nhưng đừng sao chép *cấu trúc tuyển chọn* và *nội dung* của một cuốn sách có bản quyền. Tự sinh mới toàn bộ nội dung xung quanh.

---

## 2. Nguồn từ vựng nên dùng

### ✅ NGSL — nguồn nền khuyến nghị
- **New General Service List** (Browne, Culligan, Phillips).
- Giấy phép **CC BY-SA 4.0** → tự do dùng lại, chỉnh sửa, phân phối; chỉ cần **ghi công** và **chia sẻ lại cùng giấy phép**.
- ~2.800 từ tần suất cao, phủ ~92% văn bản thông thường → rất hợp A1–B1.
- Trang: https://www.newgeneralservicelist.com

### ⚠️ Oxford 3000/5000 — chỉ tham khảo
- Tài sản của Oxford University Press, có điều khoản riêng.
- Được **tham khảo** nhãn CEFR để tự phân loại, nhưng **không đăng lại nguyên bộ dữ liệu** lên repo public.

### ⚠️ Sách đang học (Work on Your Vocabulary...) — chỉ tham khảo cá nhân
- **Không** commit PDF sách, **không** chép danh sách từ theo đúng unit, **không** chép ví dụ/bài tập.
- Được phép: học nó offline, và lấy *cảm hứng* về chủ đề (vd "gia đình", "nhà cửa") — nhưng chủ đề và bộ từ trên repo phải do bạn tự dựng từ nguồn mở.

---

## 3. Cách tránh "compilation copyright" trong thực tế

1. **Lấy từ từ NGSL**, không phải từ mục lục sách.
2. **Tự đặt tên và ranh giới chủ đề.** Chủ đề đời sống (Family, Food, Travel...) là ý tưởng chung, không ai độc quyền — nhưng cách nhóm cụ thể thì tự làm.
3. **Ghi rõ nguồn** mỗi từ trong data (`"source": "NGSL"`), để minh bạch xuất xứ.
4. **Nội dung sinh mới:** ví dụ, câu nghe, đoạn đọc, bài word-order → luôn do LLM/bạn tạo, không lấy từ sách.

---

## 4. Giấy phép đề xuất cho repo (dual license)

Vì trộn **code** và **nội dung học**, nên tách giấy phép:

- **Code** (`harness/`, scripts): **MIT** — đơn giản, phổ biến, ai cũng dùng được.
- **Nội dung học** (`data/`, units, worksheets): **CC BY-SA 4.0**.
  - Chọn CC BY-SA để **tương thích với NGSL** (NGSL là BY-SA, nên bản phái sinh phải BY-SA).

Thêm vào repo:
```
LICENSE            → MIT (cho code)
LICENSE-CONTENT    → CC BY-SA 4.0 (cho data & bài tập)
NOTICE / CREDITS   → ghi công NGSL + các nguồn
README.md          → nói rõ phần nào theo giấy phép nào
```

Mẫu dòng ghi công (bỏ vào NOTICE/README):
> Vocabulary data derived from the **New General Service List** (Browne, C., Culligan, B., & Phillips, J.), licensed under CC BY-SA 4.0. Example sentences, exercises, and audio are original content generated for this project.

---

## 5. Cấu trúc repo gợi ý (bản public)

```
english-learning/
├── README.md                 # giới thiệu + hướng dẫn + giấy phép
├── LICENSE                   # MIT (code)
├── LICENSE-CONTENT           # CC BY-SA 4.0 (data)
├── NOTICE                    # ghi công NGSL
├── data/
│   ├── wordlists/ngsl.csv    # nguồn mở, kèm attribution
│   └── topics/*.json         # chủ đề tự nhóm từ NGSL
├── harness/                  # generator, scheduler, exercises
├── units/                    # bài tập đã sinh (có thể commit)
├── dist/                     # worksheet PDF + audio để tải về
└── docs/                     # (tuỳ chọn) GitHub Pages để duyệt online
```

**Để "truy cập được nhiều nơi":**
- Bật **GitHub Pages** (thư mục `docs/`) cho trang duyệt chủ đề + tải PDF.
- Dùng **GitHub Releases** đính kèm bộ PDF + audio theo từng bản.
- README có mục lục chủ đề + link tải nhanh.

---

## 6. Checklist trước khi push public

- [ ] Không có PDF/scan sách có bản quyền trong repo (kể cả trong lịch sử git).
- [ ] Bộ từ lấy từ NGSL (hoặc nguồn mở khác), có cột `source`.
- [ ] Không có định nghĩa/ví dụ/bài tập chép từ sách.
- [ ] Có `LICENSE`, `LICENSE-CONTENT`, `NOTICE` ghi công NGSL.
- [ ] README nói rõ đây là tài liệu bổ trợ độc lập, không liên kết/không được chứng thực bởi nhà xuất bản nào.
