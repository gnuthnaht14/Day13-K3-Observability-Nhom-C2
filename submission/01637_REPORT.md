# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm C2
- Repository URL: https://github.com/gnuthnaht14/Day13-K3-Observability-Nhom-C2.git
- Thành viên và vai trò: Lường Thị Hảo | Security Engineer: CP1 PII Scrubbing, regex patterns và kiểm chứng log không lộ PII.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (đã xác nhận sau khi hoàn thiện PII scrubbing)
- Tổng số traces:
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard:

## 3. Logging và tracing
- Evidence PII redaction: xem `app/pii.py` — bổ sung 6 pattern regex trong `PII_PATTERNS`: `email`, `phone_vn` (số điện thoại VN dạng `0` hoặc `+84`), `cccd` (12 chữ số), `credit_card` (16 chữ số, có/không dấu cách hoặc gạch ngang), `passport` (1 chữ hoa + 7–8 số), `address_vn` (từ khóa địa chỉ: số nhà/đường/phường/quận/huyện/tỉnh/thành phố, không phân biệt hoa thường). Hàm `scrub_text()` áp dụng lần lượt từng pattern, thay bằng nhãn `[REDACTED_<LOẠI>]` trước khi log được ghi. `hash_user_id()` băm SHA-256 (rút gọn 12 ký tự) để ẩn danh user ID, và `summarize_text()` đảm bảo bản tóm tắt log cũng được scrub trước khi cắt độ dài. Kết quả: `validate_logs.py` đạt 100/100, không phát hiện PII leak.
  - Ảnh/log minh chứng: trong data/log.jsonl (cần 1 dòng log thể hiện dữ liệu PII giả đã được thay bằng `[REDACTED_...]`, lưu vào `submission/evidence/`)

## 4. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Lường Thị Hảo | B (Security Engineer) | CP1 — PII Scrubbing: thiết kế và triển khai 6 regex pattern (email, phone_vn, cccd, credit_card, passport, address_vn) trong `app/pii.py`; áp dụng scrub cho log text và bản tóm tắt; ẩn danh user ID bằng SHA-256 hash. Kiểm chứng qua `validate_logs.py` (100/100), xác nhận không còn PII leak trong log. | 