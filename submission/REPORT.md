# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: C2
- Repository URL: https://github.com/gnuthnaht14/Day13-K3-Observability-Nhom-C2.git
- Commit SHA cuối: a472d37d5d66841c6a905b58772fe81e3c9147b4
- Thành viên và vai trò: Vũ Thu Huyền -(Metrics & Dashboard): CP1/CP2 đo đếm error_rate_pct và thiết kế spec Dashboard 6 nhóm chỉ số.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (baseline)
- Tổng số traces: 25 traces từ langfuse
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: chưa có

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1` (Seed: 1303, Cohort: K3, Feature: `refund`)
- Triệu chứng từ metrics: Độ trễ P95/P99 tăng đột biến từ baseline ~890ms lên **3383ms - 3458ms** (vi phạm SLO P95 <= 3000ms và vượt ngưỡng `latency_threshold_ms: 2000ms`). Tỷ lệ lỗi giữ ở 0.0%.
- Trace ID liên quan: `req-0f5e02e1`, `req-9e0f33dd`, `req-a387bd6e`, `req-19d40269`, `req-8f6c1492`
- Log line/correlation ID liên quan: `correlation_id: req-0f5e02e1` (Ghi nhận `request_received` lúc `04:14:26Z` và `response_sent` lúc `04:14:29Z` với `latency_ms: 3357`, `feature: refund`).
- Root cause: Incident `rag_slow` được bật làm nghẽn bước RAG Document Retrieval (Vector Search) của tính năng `refund`, thêm khoảng delay 2.5s vào mọi truy vấn liên quan.
- Fix action: 
  1. Tắt công tắc sự cố: `python scripts/inject_incident.py --scenario rag_slow --disable`.
  2. Trên Production: Tối ưu hóa chỉ mục HNSW trong Vector DB, bật Caching cho các truy vấn RAG phổ biến và đặt timeout 1.5s cho bước Retrieval.
- Preventive measure: Cấu hình Alert `high_latency_p95` (`latency_p95 > 3000ms for 5m`), cài đặt Circuit Breaker tự động ngắt RAG khi vượt quá 1500ms, và thiết lập bảng Dashboard giám sát P95 Latency phân tách theo từng `feature`.
