# Template Alert và Runbook

Tất cả alert trong hệ thống đều tuân thủ nguyên tắc **Symptom-based Alerting** (cảnh báo dựa trên triệu chứng ảnh hưởng trực tiếp tới trải nghiệm người dùng hoặc vi phạm SLO), không phụ thuộc vào tên triển khai nội bộ.

---

## Alert 1: High Latency P95

- **Tên alert**: `high_latency_p95`
- **Severity**: `warning`
- **SLI/SLO liên quan**: SLI Latency P95 (SLO: P95 <= 3000ms cho 99.5% requests)
- **Điều kiện và thời gian duy trì**: `latency_p95 > 3000ms for 5 minutes`
- **Ảnh hưởng tới người dùng**: Người dùng gặp hiện tượng phản hồi chậm khi gửi câu hỏi qua API `/chat`, trải nghiệm trò chuyện bị gián đoạn, thời gian chờ đợi phản hồi kéo dài bất thường.
- **Ba bước kiểm tra đầu tiên**:
  1. **Bước 1 (Metrics)**: Mở Dashboard kiểm tra panel *Latency Percentiles* để xác định độ trễ tăng đột biến ở P95/P99 hay toàn bộ P50. Kiểm tra đồng thời panel *Traffic* xem có dấu hiệu spike traffic bất thường hay không.
  2. **Bước 2 (Traces)**: Mở Langfuse Tracing, lọc các trace có độ trễ > 3000ms. Kiểm tra waterfall span để xác định xem thời gian bị nghẽn ở bước RAG retrieval (Retrieval span) hay ở thời gian phản hồi của LLM generation (Generation span).
  3. **Bước 3 (Logs)**: Trích xuất `correlation_id` từ trace bị chậm, tra cứu log tương ứng trong `data/logs.jsonl` để kiểm tra thông tin chi tiết (`feature`, `model`, `payload.message_preview`).
- **Mitigation tạm thời**: 
  - Nếu do RAG/retrieval bị chậm: Bật incident toggle hoặc tạm thời fallback sử dụng Mock RAG fast mode / cache kết quả retrieval.
  - Nếu do LLM generation bị nghẽn: Chuyển đổi model LLM sang model có tốc độ phản hồi nhanh hơn hoặc giảm `max_tokens` đầu ra.
- **Owner**: `on-call-engineer`

---

## Alert 2: Elevated Error Rate

- **Tên alert**: `elevated_error_rate`
- **Severity**: `critical`
- **SLI/SLO liên quan**: SLI Error Rate (SLO: Error Rate <= 2.0% cho 99.0% cửa sổ thời gian)
- **Điều kiện và thời gian duy trì**: `error_rate_pct > 5 for 3 minutes`
- **Ảnh hưởng tới người dùng**: Người dùng nhận được phản hồi lỗi HTTP 500 khi gọi API `/chat`, không thể hoàn thành truy vấn và nhận được câu trả lời từ hệ thống AI.
- **Ba bước kiểm tra đầu tiên**:
  1. **Bước 1 (Metrics)**: Mở Dashboard kiểm tra panel *Error Rate and Breakdown* để xem tỷ lệ lỗi hiện tại và phân loại lỗi trong `error_breakdown` (ví dụ: `RateLimitError`, `TimeoutError`, `APIConnectionError`).
  2. **Bước 2 (Logs)**: Tìm các dòng log có `level == "error"` và `event == "request_failed"` trong `data/logs.jsonl`, đọc chi tiết `error_type` và `payload.detail` cùng `correlation_id`.
  3. **Bước 3 (Traces & Health)**: Mở Langfuse kiểm tra các trace có status `ERROR`, xác định xem lỗi phát sinh từ kết nối mạng API bên ngoài (Provider API limit) hay do lỗi nội bộ ứng dụng. Đồng thời kiểm tra `/health` endpoint.
- **Mitigation tạm thời**:
  - Nếu do dính Rate Limit / Quota API bên ngoài: Chuyển hướng traffic sang API Key dự phòng (Failover API Key) hoặc giảm nhịp request từ phía client.
  - Nếu do lỗi ứng dụng: Khởi động lại service API worker hoặc rollback về commit/version ổn định gần nhất.
- **Owner**: `on-call-engineer`

---

## Alert 3: Cost Budget Exceeded

- **Tên alert**: `cost_budget_exceeded`
- **Severity**: `warning`
- **SLI/SLO liên quan**: SLI Daily Cost (SLO: Chi phí LLM dưới $2.50 USD / ngày)
- **Điều kiện và thời gian duy trì**: `daily_cost_usd > 2.5`
- **Ảnh hưởng tới người dùng**: Không ảnh hưởng trực tiếp đến tốc độ phản hồi của người dùng ngay lập tức, nhưng có nguy cơ khiến hệ thống bị tạm dừng (service suspension) do cạn kiệt ngân sách vận hành.
- **Ba bước kiểm tra đầu tiên**:
  1. **Bước 1 (Metrics & Dashboard)**: Kiểm tra panel *Cost Over Time* và *Input and Output Tokens* trên Dashboard để xem tổng `total_cost_usd` và đếm tổng số token input/output consumed.
  2. **Bước 2 (Traces Audit)**: Mở Langfuse Audit, sắp xếp các trace theo chi phí (`cost_usd` giảm dần) để phát hiện các request tiêu tốn chi phí bất thường (ví dụ: prompt dài quá mức hoặc output token vượt ngưỡng).
  3. **Bước 3 (Logs Analysis)**: Tìm các dòng log `response_sent` có `cost_usd` cao, phân tích `user_id_hash`, `feature` và `session_id` để kiểm tra xem có dấu hiệu lạm dụng (Abuse / Bot Spam) từ một tài khoản cụ thể hay không.
- **Mitigation tạm thời**:
  - Thắt chặt giới hạn độ dài Prompt / Document Retrieval (`max_docs` giảm bớt).
  - Cấu hình bổ sung Rate Limiting theo `user_id` để chặn các tài khoản có hành vi spam / lạm dụng API.
- **Owner**: `team-lead`
