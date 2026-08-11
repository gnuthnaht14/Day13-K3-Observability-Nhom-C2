# Yêu cầu & Thiết kế Dashboard (Dashboard Spec)

Dashboard này được thiết kế để giám sát toàn diện **6 nhóm chỉ số chính** cho hệ thống Day 13 AI Observability.
Contract kiểm tra tự động nằm tại file [config/dashboard.yaml](file:///d:/workSpace/VinAI/Day13-K3-Observability-Nhom-C2/config/dashboard.yaml).

---

## 1. Cấu hình chung

- **Khoảng thời gian mặc định (Time Range)**: `60 phút` (1 giờ).
- **Tần suất tự động làm mới (Auto Refresh)**: `30 giây` (nằm trong khoảng 15–30s).
- **Công cụ giám sát**: Langfuse / Grafana / Specs dựa trên Endpoint `/metrics` & File log `data/logs.jsonl`.
- **Nguồn dữ liệu**: Endpoint `/metrics` & File log dạng JSON Lines `data/logs.jsonl`.

---

## 2. Bảng quy chuẩn 6 Nhóm Panel Chỉ Số

| # | Nhóm Panel | Tên Panel (Title) | Nguồn dữ liệu & Nguồn Metric | Đơn vị (Unit) | Khoảng thời gian | Threshold / SLO Line | Mô tả & Loại biểu đồ |
|---|---|---|---|---|---|---|---|
| 1 | **Latency** | `Latency percentiles` | `/metrics` $\rightarrow$ `latency_p50`, `latency_p95`, `latency_p99`<br>*(Log: `response_sent`)* | `ms` | 60 phút | `p95 <= 3000 ms` (SLO Line: 3000ms) | Biểu đồ Line Chart hiển thị độ trễ P50, P95, P99 theo thời gian. |
| 2 | **Traffic** | `Request traffic` | `/metrics` $\rightarrow$ `traffic`<br>*(Log: `request_received`)* | `requests_per_minute` / `count` | 60 phút | `rate_per_minute >= 1` | Counter tổng số request hoặc Gauge hiển thị lưu lượng request vào ứng dụng. |
| 3 | **Error** | `Error rate and breakdown` | `/metrics` $\rightarrow$ `error_rate_pct`, `error_breakdown`<br>*(Log: `request_failed`)* | `%` (percent) | 60 phút | `error_rate_pct <= 2.0%` (SLO Line: 2%) | Stat Panel (%) hiển thị tỷ lệ lỗi kèm Bar Chart/Table chi tiết theo loại lỗi (`error_type`). |
| 4 | **Cost** | `Cost over time` | `/metrics` $\rightarrow$ `total_cost_usd`, `avg_cost_usd`<br>*(Log: `response_sent`)* | `usd` ($) | 60 phút | `total_cost_usd <= 2.50 USD` | Line/Bar Chart theo dõi tổng chi phí gọi LLM so với ngưỡng ngân sách. |
| 5 | **Tokens** | `Input and output tokens` | `/metrics` $\rightarrow$ `tokens_in_total`, `tokens_out_total`<br>*(Log: `response_sent`)* | `tokens` | 60 phút | `tokens_total <= 50,000` | Stacked Bar Chart hiển thị số lượng token đầu vào (input) và đầu ra (output). |
| 6 | **Quality** | `Quality proxy` | `/metrics` $\rightarrow$ `quality_avg`<br>*(Log: `response_sent`)* | `score_0_to_1` | 60 phút | `quality_avg >= 0.75` | Gauge / Single Stat Chart hiển thị điểm số chất lượng phản hồi trung bình (0.0 - 1.0). |

---

## 3. Dữ liệu thực tế từ Endpoint `/metrics`

Khi gọi endpoint `/metrics` bằng lệnh `curl http://localhost:8000/metrics`, hệ thống trả về JSON mẫu như sau:

```json
{
  "traffic": 10,
  "latency_p50": 866.0,
  "latency_p95": 892.0,
  "latency_p99": 892.0,
  "avg_cost_usd": 0.0021,
  "total_cost_usd": 0.0206,
  "tokens_in_total": 330,
  "tokens_out_total": 1307,
  "error_rate_pct": 0.0,
  "error_breakdown": {},
  "quality_avg": 0.88
}
```

---

## 4. Kiểm tra Validator Contract

Chạy lệnh tự động để kiểm tra tính hợp lệ của Dashboard Contract:

```bash
uv run python scripts/validate_dashboard.py
```

Kết quả mong đợi:
```text
HỢP LỆ: 6/6 panel có trong dashboard contract.
```
