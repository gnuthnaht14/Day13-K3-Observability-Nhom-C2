# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: [CẦN BẠN BỔ SUNG]
- Repository URL: [CẦN BẠN BỔ SUNG]
- Commit SHA cuối: `e4decfd` tại thời điểm lập báo cáo; cập nhật lại sau khi commit báo cáo.
- Thành viên và vai trò: [CẦN BẠN BỔ SUNG]

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: `100/100`.
- Tổng số traces: [CẦN BẠN BỔ SUNG — repo không có danh sách trace Langfuse].
- Số PII leak còn lại: `0` theo `submission/validation_logs.txt`.
- Link/đường dẫn dashboard: chạy `python -m streamlit run dashboard.py`; link runtime/screenshot: [CẦN BẠN BỔ SUNG].

## 3. Logging và tracing

- Evidence correlation ID: `submission/validation_logs.txt`; 10 unique correlation IDs.
- Evidence PII redaction: `submission/validation_logs.txt`; Potential PII leaks detected: 0.
- Evidence trace waterfall: [CẦN BẠN BỔ SUNG — chưa có file hoặc trace ID trong repo].
- Giải thích một span đáng chú ý: [CẦN BẠN BỔ SUNG sau khi chọn một trace thực tế].

## 4. Prompt versioning

- Prompt name: [CẦN BẠN BỔ SUNG từ Langfuse].
- Version/label baseline: [CẦN BẠN BỔ SUNG từ Langfuse].
- Version/label candidate: [CẦN BẠN BỔ SUNG từ Langfuse].
- Trace ID của mỗi version: [CẦN BẠN BỔ SUNG].
- Bằng chứng đổi label hoặc rollback: [CẦN BẠN BỔ SUNG — chưa có evidence trong repo].

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: `dashboard.py`; screenshot/runtime URL: [CẦN BẠN BỔ SUNG].
- SLO đã chọn và lý do:
  - Latency P95 `<= 3000 ms`, target `99.5%`: giới hạn thời gian chờ của người dùng.
  - Error rate `<= 2%`, target `99.0%`: giới hạn số request thất bại.
  - Daily cost `<= 2.5 USD`: kiểm soát chi phí vận hành AI.
  - Average quality score `>= 0.75`, target `95.0%`: duy trì chất lượng câu trả lời ở mức tối thiểu.
- Alert rules và runbook:
  - `ChatLatencyP95High` — `config/alert_rules.yaml`, `docs/alerts.md#alert-1`.
  - `ChatErrorRateHigh` — `config/alert_rules.yaml`, `docs/alerts.md#alert-2`.
  - `ChatQualityDegraded` — `config/alert_rules.yaml`, `docs/alerts.md#alert-3`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`.
- Triệu chứng từ metrics: [CẦN BẠN BỔ SUNG từ lần chạy challenge chính thức].
- Trace ID liên quan: [CẦN BẠN BỔ SUNG].
- Log line/correlation ID liên quan: [CẦN BẠN BỔ SUNG].
- Root cause: [CẦN BẠN BỔ SUNG — không tự suy đoán khi chưa có evidence].
- Fix action: [CẦN BẠN BỔ SUNG].
- Preventive measure: [CẦN BẠN BỔ SUNG].

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên        | Phần việc                                                      | Commit/PR         | Điều đã học                                                                          |
| ----------------- | -------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------ |
| [CẦN BẠN BỔ SUNG] | Thiết lập SLO, viết symptom-based alert rules và alert runbook | `6eeb3f2`         | Chuyển SLI/SLO thành threshold, condition, owner và quy trình Metrics → Trace → Logs |
| [CẦN BẠN BỔ SUNG] | [CẦN BẠN BỔ SUNG]                                              | [CẦN BẠN BỔ SUNG] | [CẦN BẠN BỔ SUNG]                                                                    |
