# Alerts và runbook

Các alert dưới đây dựa trên triệu chứng người dùng hoặc nguy cơ vi phạm SLO. Tên incident hay chi tiết implementation chỉ được dùng sau khi metrics, traces và logs cung cấp bằng chứng.

`objective` trong `config/slo.yaml` là ngưỡng kỹ thuật phân loại một phép đo là tốt. `target` là tỷ lệ request hoặc cửa sổ đo phải đạt ngưỡng đó trong cửa sổ SLO 28 ngày.

## HighLatencyP95

- **Severity:** `warning`
- **Owner:** `sre-oncall`; escalation tới application/agent owner nếu trace xác định span ứng dụng gây chậm.
- **SLI/SLO liên quan:** P95 của `response_sent.latency_ms` phải không vượt quá 3000 ms; 99.5% cửa sổ đo phải đạt objective trong 28 ngày.
- **Điều kiện:** `latency_p95_ms > 3000` liên tục 5 phút.
- **Ảnh hưởng người dùng:** câu trả lời chậm, timeout phía client và trải nghiệm không ổn định ở nhóm request đuôi dài.

### Ba bước kiểm tra đầu tiên

1. **Metrics:** xác nhận P95 vượt 3000 ms trong ít nhất 5 phút; so sánh P50/P99, traffic và error rate trong cùng khoảng thời gian.
2. **Traces:** mở các trace chậm trong khoảng cảnh báo, so sánh duration của retrieval, generation và các dependency span để khoanh vùng bước bất thường.
3. **Logs:** dùng correlation ID của trace/request để tìm `request_received`, `response_sent` hoặc `request_failed`; kiểm tra `feature`, `model`, `latency_ms` và `error_type` thay vì suy luận từ tên incident.

- **Mitigation tạm thời:** giảm tải hoặc giới hạn concurrency, rollback thay đổi vừa triển khai, chuyển sang dependency/prompt đã ổn định hoặc tạm vô hiệu hóa đường xử lý chậm nếu có fallback an toàn.
- **Escalation:** page application/agent owner khi P95 vượt 6000 ms, error rate đồng thời vượt 2%, hoặc cảnh báo không hồi phục sau 15 phút mitigation.
- **Điều kiện đóng incident:** P95 không vượt 3000 ms trong ít nhất 15 phút, traffic đã trở lại mức đại diện, không có error spike liên quan và trace/log xác nhận nguyên nhân đã được loại bỏ.

## HighErrorRate

- **Severity:** `critical`
- **Owner:** `sre-oncall`; escalation tới owner của dependency hoặc application component được trace xác định.
- **SLI/SLO liên quan:** tỷ lệ `request_failed / request_received` không vượt quá 2%; 99% cửa sổ đo phải đạt objective trong 28 ngày.
- **Điều kiện:** `error_rate_pct > 2` liên tục 5 phút.
- **Ảnh hưởng người dùng:** request thất bại, không nhận được câu trả lời hoặc phải thử lại, có thể làm tăng latency và chi phí do retry.

### Ba bước kiểm tra đầu tiên

1. **Metrics:** xác nhận error rate vượt 2%, kiểm tra request volume và breakdown theo `error_type` để loại trừ tỷ lệ méo do traffic quá thấp.
2. **Traces:** mở trace lỗi đại diện và trace thành công gần đó; tìm span có error status, timeout hoặc retry tăng bất thường.
3. **Logs:** tra correlation ID trong `request_failed`, xác nhận `error_type`, feature/model bị ảnh hưởng và chuỗi event của cùng request; không dùng exception chứa dữ liệu nhạy cảm làm bằng chứng công khai.

- **Mitigation tạm thời:** rollback release gần nhất, chuyển sang dependency/fallback khỏe, tắt feature gây lỗi hoặc áp dụng rate limit/circuit breaker để ngăn retry storm.
- **Escalation:** page ngay application owner; page dependency owner nếu nhiều trace cùng thất bại tại một dependency. Incident commander được gọi khi lỗi kéo dài 10 phút hoặc ảnh hưởng nhiều feature.
- **Điều kiện đóng incident:** error rate không vượt 2% trong ít nhất 15 phút với traffic đại diện, không còn loại lỗi chi phối và trace/log của request kiểm chứng cho thấy đường xử lý đã phục hồi.

## DailyCostBudgetRisk

- **Severity:** `warning`
- **Owner:** `sre-oncall`; escalation tới AI platform/finops owner khi nguyên nhân nằm ở model price, token usage hoặc traffic policy.
- **SLI/SLO liên quan:** tổng `response_sent.cost_usd` trong rolling 24 giờ không vượt quá 2.50 USD; 100% cửa sổ ngày trong kỳ SLO phải nằm trong ngân sách.
- **Điều kiện:** `daily_cost_usd > 2.5` trong rolling 24 giờ và duy trì 15 phút. Dashboard 60 phút dùng cùng ngưỡng 2.50 USD như một cảnh báo sớm, còn quyết định SLO dùng tổng rolling 24 giờ.
- **Ảnh hưởng người dùng:** chưa chắc gây lỗi tức thời, nhưng có thể buộc throttling, hạ model hoặc dừng dịch vụ khi ngân sách cạn; token/retry bất thường cũng thường đi kèm latency tăng.

### Ba bước kiểm tra đầu tiên

1. **Metrics:** xác nhận tổng cost rolling 24 giờ, sau đó so sánh traffic, tokens input/output và cost trên mỗi request với baseline; kiểm tra tăng giá trị thay vì chỉ tăng volume.
2. **Traces:** mở trace có cost/token cao, so sánh model, prompt/generation usage, retry và số span với trace bình thường.
3. **Logs:** dùng correlation ID để kiểm tra `tokens_in`, `tokens_out`, `cost_usd`, `feature` và `model` của các request đóng góp nhiều nhất; kiểm tra spike có tập trung ở một feature/session hay không.

- **Mitigation tạm thời:** giới hạn output tokens/concurrency, dừng retry không cần thiết, chuyển sang model rẻ hơn đã được phê duyệt, cache kết quả an toàn hoặc rate-limit workload không ưu tiên.
- **Escalation:** thông báo AI platform/finops owner khi chi phí tiếp tục tăng sau 30 phút, forecast vượt 120% ngân sách hoặc mitigation có nguy cơ làm quality thấp hơn 0.75.
- **Điều kiện đóng incident:** rolling-24-hour cost hoặc forecast đã dưới 2.50 USD, cost/request và token/request ổn định ít nhất 30 phút, đồng thời quality và error SLO vẫn đạt sau mitigation.
