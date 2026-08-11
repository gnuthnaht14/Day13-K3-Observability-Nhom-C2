# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm C2 — VinAI K3 Cohort
- Repository URL: `https://github.com/gnuthnaht14/Day13-K3-Observability-Nhom-C2`
- Commit SHA cuối: `a472d37`
- Thành viên và vai trò:
  - Mai Hồng Sơn (2A202601921): CP1 Middleware, gán Correlation ID, và bổ sung exception handler (phần mở rộng).
  - Lê Thị Linh (2A202601441): CP2 Thiết lập SLO, viết Alerts rules và Alert Runbook xử lý sự cố.
  - Vũ Thu Huyền (2A202601583): CP1/CP2 đo đếm error_rate_pct và thiết kế spec Dashboard 6 nhóm chỉ số.
  - Lường Thị Hảo (2A202601637): CP1 PII Scrubbing, regex patterns và kiểm chứng log không lộ PII.
  - Nhữ Trọng Thành (2A202601977): Leader / Chạy load test, bọc trace cho sub-component RAG/LLM (phần mở rộng), dẫn dắt điều tra Challenge (CP3) và hoàn thiện báo cáo nhóm.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** (Đạt chuẩn JSON schema, Propagation, Enrichment & 0 PII Leak)
- Tổng số traces: **25+ traces** từ Langfuse
- Số PII leak còn lại: **0**
- Link/đường dẫn dashboard: `http://localhost:8000/dashboard` (Tệp bằng chứng: `submission/evidence/dashboard.html`)

## 3. Logging và tracing

- Evidence correlation ID: Tự động sinh bởi `CorrelationIdMiddleware` ở header `X-Correlation-ID` (định dạng `req-<8hex>`) và lan truyền đồng bộ vào mọi bản ghi log (`request_received`, `response_sent`). Bằng chứng lưu tại `submission/evidence/1.jpg`.
- Evidence PII redaction: Processor `scrub_event` đệ quy tự động lọc và che 6 loại thông tin cá nhân nhạy cảm thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`, `[REDACTED_NATIONAL_ID]`, `[REDACTED_PASSPORT]`, `[REDACTED_ADDRESS_VN]`. Bằng chứng lưu tại `submission/evidence/2.jpg`.
- Evidence trace waterfall: Langfuse Tracing thể hiện chi tiết cây span cha `run` (Trace) và span con `generation` (LLM Call), hiển thị đầy đủ `doc_count`, `query_preview`, `prompt_tokens`, `completion_tokens`, `cost_details`.
- Giải thích một span đáng chú ý: Span `run` của request `req-0f5e02e1` (`feature: refund`): Do sự cố `rag_slow` bị kích hoạt, thời gian xử lý của bước RAG Retrieval bị chậm thêm **2.500 ms**, khiến tổng thời gian thực thi của span `run` tăng từ baseline **890 ms** lên **3.357 ms**, lập tức kích hoạt cảnh báo SLO `high_latency_p95`.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: `v1` (label: `baseline`, `production`)
- Version/label candidate: `v2` (label: `candidate`)
- Trace ID của mỗi version:
  - Baseline Trace: `req-0f5e02e1` (`prompt_version: v1`, `prompt_label: production`)
  - Candidate Trace: `req-602e8e55` (`prompt_version: v2`, `prompt_label: candidate`)
- Bằng chứng đổi label hoặc rollback: Thay đổi nhãn `LANGFUSE_PROMPT_LABEL` trong `.env` từ `production` sang `candidate`, SDK `client.get_prompt()` tự động tải phiên bản prompt tương ứng từ Langfuse mà không cần thay đổi mã nguồn.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: **HỢP LỆ: 6/6 panel có trong dashboard contract**
- Evidence dashboard: Đã lưu bản giao diện web thời gian thực tại `submission/evidence/dashboard.html` và truy cập trực tiếp tại `http://localhost:8000/dashboard`.
- SLO đã chọn và lý do:
  1. `latency_p95_ms` ($\le 3000\text{ms}$, target 99.5%): Đảm bảo người dùng nhận phản hồi nhanh chóng khi tương tác với Chatbot.
  2. `error_rate_pct` ($\le 2.0\%$, target 99.0%): Giữ hệ thống ổn định, tránh gián đoạn dịch vụ.
  3. `daily_cost_usd` ($\le \$2.50$, target 100.0%): Kiểm soát ngân sách gọi LLM API không bị bùng nổ.
  4. `quality_score_avg` ($\ge 0.75$, target 95.0%): Đảm bảo chất lượng câu trả lời AI luôn đạt tiêu chuẩn khá trở lên.
- Alert rules và runbook:
  - Cấu hình 3 quy tắc cảnh báo triệu chứng (Symptom-based) trong `config/alert_rules.yaml` (`high_latency_p95`, `elevated_error_rate`, `cost_budget_exceeded`).
  - Xây dựng tài liệu chi tiết quy trình ứng cứu sự cố 3 bước (Metrics $\rightarrow$ Traces $\rightarrow$ Logs) tại `docs/alerts.md`.

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

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Mai Hồng Sơn (2A202601921) | CP1 Middleware, gán Correlation ID và bổ sung exception handler (phần mở rộng) | `2A202601921` | Cách tạo ContextVar middleware để gán Correlation ID và bổ sung exception handler tập trung cho FastAPI. |
| Lê Thị Linh (2A202601441) | CP2 Thiết lập SLO, viết Alerts rules và Alert Runbook xử lý sự cố | `2A202601441` | Quy trình ứng cứu sự cố 3 bước (Metrics -> Traces -> Logs) và cách định nghĩa Alert Rules & Runbook. |
| Vũ Thu Huyền (2A202601583) | CP1/CP2 đo đếm error_rate_pct và thiết kế spec Dashboard 6 nhóm chỉ số | `2A202601583` | Phương pháp thiết kế Dashboard Observability chuẩn 6 nhóm chỉ số và theo dõi tỷ lệ lỗi dịch vụ. |
| Lường Thị Hảo (2A202601637) | CP1 PII Scrubbing, regex patterns và kiểm chứng log không lộ PII | `2A202601637` | Kỹ thuật PII scrubbing với regex patterns đệ quy trong structlog, đảm bảo an toàn dữ liệu 0 PII leak. |
| Nhữ Trọng Thành (2A202601977) | Leader — Chạy load test, bọc trace cho sub-component RAG/LLM (phần mở rộng), dẫn dắt điều tra Challenge (CP3) và hoàn thiện báo cáo nhóm | `2A202601977` | Quản lý dự án, tracing chi tiết sub-component RAG/LLM với Langfuse, phân tích RCA sự cố RAG latency và tổng hợp báo cáo nhóm. |

