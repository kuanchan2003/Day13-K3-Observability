# Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `HighLatencyP95`
- Severity: warning
- SLI/SLO liên quan: P95 latency ≤ 3.000 ms.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000` liên tục 5 phút.
- Ảnh hưởng tới người dùng: câu trả lời chậm, client có thể timeout.
- Ba bước kiểm tra đầu tiên: xác nhận traffic/error cùng cửa sổ; mở trace chậm nhất và tìm span chiếm thời gian; nối `correlation_id` sang log để kiểm tra RAG/LLM.
- Mitigation tạm thời: tắt incident nếu đang bật, giảm concurrency hoặc chuyển prompt label về baseline ổn định.
- Owner: `ai-platform-oncall`.

## Alert 2

- Tên: `ElevatedErrorRate`
- Severity: critical
- SLI/SLO liên quan: error rate ≤ 2%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 2` liên tục 5 phút, chỉ đánh giá khi có ít nhất 20 request để tránh nhiễu mẫu nhỏ.
- Ảnh hưởng tới người dùng: request trả lỗi hoặc không có câu trả lời.
- Ba bước kiểm tra đầu tiên: xem breakdown theo `error_type`; mở trace thất bại gần nhất; tìm log `request_failed` bằng `correlation_id` và kiểm tra thay đổi/dependency gần đây.
- Mitigation tạm thời: rollback deployment/prompt label gần nhất hoặc cô lập dependency gây lỗi; xác nhận error rate hồi phục.
- Owner: `ai-platform-oncall`.

## Alert 3

- Tên: `QualityRegression`
- Severity: warning
- SLI/SLO liên quan: quality proxy trung bình ≥ 0,75.
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` liên tục 15 phút, với ít nhất 20 request.
- Ảnh hưởng tới người dùng: câu trả lời thiếu ngữ cảnh hoặc kém hữu ích dù API vẫn thành công.
- Ba bước kiểm tra đầu tiên: phân đoạn theo feature/prompt version; so trace baseline và candidate; kiểm tra retrieval docs và prompt metadata trong generation.
- Mitigation tạm thời: rollback label `production` về prompt baseline đã xác minh và chạy lại cùng tập input.
- Owner: `ai-quality-oncall`.
