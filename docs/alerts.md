# Alert và Runbook xử lý sự cố

Các alert dưới đây dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

Quy trình chung: xác nhận alert trên dashboard, khoanh vùng theo feature/model, mở trace bất thường, dùng correlation ID để tìm log, áp dụng mitigation, sau đó xác nhận metric hồi phục.

## Alert 1

- Tên: ChatLatencyP95High
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms <= 3000 ms`, target 99.5% trong cửa sổ 28 ngày.
- Điều kiện và thời gian duy trì: P95 của `response_sent.latency_ms` lớn hơn 3000 ms liên tục trong 10 phút.
- Ảnh hưởng tới người dùng: Câu trả lời chậm, có thể gây timeout hoặc người dùng phải thử lại.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel Latency và lọc theo feature/model để xác định phạm vi ảnh hưởng.
  2. Mở một trace chậm và so sánh thời gian các span retrieval, prompt và generation.
  3. Dùng correlation ID của trace để tìm các event `request_received` và `response_sent` tương ứng trong log.
- Mitigation tạm thời: giảm concurrency/traffic nếu cần; tắt dependency hoặc incident practice đang gây chậm; rollback prompt nếu latency bắt đầu sau khi đổi prompt.
- Owner: dashboard-slo

## Alert 2

- Tên: ChatErrorRateHigh
- Severity: critical
- SLI/SLO liên quan: error rate `<= 2%`, target 99.0% trong cửa sổ 28 ngày.
- Điều kiện và thời gian duy trì: `request_failed / request_received * 100` lớn hơn 2% liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: Request thất bại, người dùng nhận lỗi 500 hoặc không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra error rate và breakdown theo `error_type` trên dashboard.
  2. Mở một trace của request lỗi để xác định span thất bại.
  3. Dùng correlation ID để đối chiếu log `request_failed`, exception type và feature bị ảnh hưởng.
- Mitigation tạm thời: giảm traffic; tắt feature/incident gây lỗi nếu đã xác định; rollback thay đổi gần nhất và theo dõi error rate sau mitigation.
- Owner: api-oncall

## Alert 3

- Tên: ChatQualityDegraded
- Severity: warning
- SLI/SLO liên quan: `quality_score_avg >= 0.75`, target 95.0% trong cửa sổ 28 ngày.
- Điều kiện và thời gian duy trì: trung bình `response_sent.quality_score` nhỏ hơn 0.75 liên tục trong 15 phút.
- Ảnh hưởng tới người dùng: Câu trả lời có thể thiếu thông tin, không liên quan hoặc không đáp ứng câu hỏi.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel Quality và phân nhóm theo feature, prompt label và model.
  2. Mở các trace có quality score thấp, kiểm tra prompt version, số tài liệu retrieval và generation metadata.
  3. Đối chiếu correlation ID với log để xác định nhóm request và input bị ảnh hưởng.
- Mitigation tạm thời: rollback prompt label về phiên bản ổn định; giảm traffic ở feature bị ảnh hưởng; kiểm tra lại retrieval context trước khi mở lại.
- Owner: ai-quality

## Sau sự cố

- Ghi lại thời gian bắt đầu/kết thúc, alert bị kích hoạt và phạm vi ảnh hưởng.
- Lưu metric, trace ID và correlation ID làm evidence.
- Ghi root cause, hành động khắc phục và preventive measure vào `submission/REPORT.md`.
