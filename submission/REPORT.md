# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: C2
- Repository URL: https://github.com/gnuthnaht14/Day13-K3-Observability-Nhom-C2
- Commit SHA cuối tại thời điểm lập report: `1db56eebdd305877582627ec7d6fb983eb4ccda4`
- Thành viên và vai trò: Lê Thị Linh - Thiết lập SLO, viết alert rules và alert runbook

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: `100/100`.
- Tổng số traces: `25 traces` theo thông tin nhóm đã ghi; danh sách/link Langfuse
- Số PII leak còn lại: `0` theo `submission/validation_logs.txt`.
- Link/đường dẫn dashboard: chạy `python -m streamlit run dashboard.py`; evidence hiện có: `submission/evidence/dashboard.html`, `1.jpg`, `2.jpg`; URL runtime: http://localhost:8000/dashboard.

## 3. Logging và tracing

- Evidence correlation ID: `submission/validation_logs.txt`; 10 unique correlation IDs.
- Evidence PII redaction: `submission/validation_logs.txt`; Potential PII leaks detected: 0.
- Evidence trace waterfall: Langfuse trace `req-0f5e02e1` theo `submission/PITCH_DECK.md`;
- Giải thích một span đáng chú ý: span `RAG Document Retrieval/Vector Search` bị chậm thêm khoảng 2.5 giây khi incident `rag_slow` bật, khiến tổng latency của request `req-0f5e02e1` là 3357 ms.

## 4. Prompt versioning

- Prompt name: `day13-chat` theo `.env.example`.
- Version/label baseline: prompt name `day13-chat`, label cấu hình `production`; số version không có trong repo.
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: `dashboard.py`, `submission/evidence/dashboard.html`, `submission/evidence/1.jpg`, `submission/evidence/2.jpg`; runtime URL theo Pitch Deck: `http://localhost:8000/dashboard`.
- SLO đã chọn và lý do:
  - Latency P95 `<= 3000 ms`, target `99.5%`: giới hạn thời gian chờ của người dùng.
  - Error rate `<= 2%`, target `99.0%`: giới hạn số request thất bại.
  - Daily cost `<= 2.5 USD`: kiểm soát chi phí vận hành AI.
  - Average quality score `>= 0.75`, target `95.0%`: duy trì chất lượng câu trả lời ở mức tối thiểu.
- Alert rules và runbook:
  - `high_latency_p95` — warning, `latency_p95 > 3000ms for 5 minutes` — `config/alert_rules.yaml`, `docs/alerts.md#alert-1`.
  - `elevated_error_rate` — critical, `error_rate_pct > 5 for 3 minutes` — `config/alert_rules.yaml`, `docs/alerts.md#alert-2`.
  - `cost_budget_exceeded` — warning, `daily_cost_usd > 2.5` — `config/alert_rules.yaml`, `docs/alerts.md#alert-3`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1` (Seed: 1303, Cohort: K3, Feature: `refund`).
- Triệu chứng từ metrics: P95/P99 tăng từ baseline khoảng 890 ms lên khoảng 3383–3458 ms; vi phạm SLO P95 `<= 3000 ms` và vượt `latency_threshold_ms: 2000 ms`. Error rate giữ ở 0.0%.
- Trace ID liên quan: `req-0f5e02e1`, `req-9e0f33dd`, `req-a387bd6e`, `req-19d40269`, `req-8f6c149`.
- Log line/correlation ID liên quan: `correlation_id: req-0f5e02e1`; `request_received` lúc `04:14:26Z`, `response_sent` lúc `04:14:29Z`, `latency_ms: 3357`, `feature: refund`.
- Root cause: Incident `rag_slow` làm chậm bước RAG Document Retrieval/Vector Search của feature `refund`, thêm khoảng 2.5 giây vào truy vấn.
- Fix action: chạy `python scripts/inject_incident.py --scenario rag_slow --disable`; production nên tối ưu HNSW index, cache truy vấn RAG và đặt timeout 1.5 giây cho Retrieval.
- Preventive measure: dùng alert `high_latency_p95`, phân tách dashboard theo `feature` và bổ sung Circuit Breaker khi Retrieval vượt 1500 ms.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên  | Phần việc                                        | Commit/PR | Điều đã học                                                                           |
| ----------- | ------------------------------------------------ | --------- | ------------------------------------------------------------------------------------- |
| Lê Thị Linh | Thiết lập SLO, viết alert rules và alert runbook | `6eeb3f2` | Chuyển SLI/SLO thành threshold, condition, owner và quy trình Metrics → Traces → Logs |
