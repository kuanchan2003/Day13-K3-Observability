# Personal task — Thành viên A: API & Middleware

## Mục tiêu

Hoàn thiện phần API để mọi request có thể được theo dõi xuyên suốt bằng một
correlation ID, log API có đủ ngữ cảnh phục vụ điều tra, và lỗi chưa được xử lý
được trả về/ghi nhận nhất quán. Đây là phần đóng góp chính cho Checkpoint 1
(0:30–1:30); exception handler là phần mở rộng hỗ trợ CP2/CP3.

## Phạm vi công việc

### 1. Hoàn thiện `CorrelationIdMiddleware` (CP1)

Thực hiện trong `app/middleware.py`:

- Xóa `structlog` contextvars ở đầu mỗi request bằng `clear_contextvars()` để
  không rò rỉ context giữa các request.
- Đọc header `x-request-id` nếu client đã gửi; nếu không có thì sinh ID theo
  định dạng `req-<8 ký tự hex>`.
- Lưu ID vào `request.state.correlation_id` và bind vào contextvars bằng
  `bind_contextvars(correlation_id=...)`, để tất cả log phát sinh trong request
  tự động có cùng ID.
- Đo thời gian xử lý request bằng `time.perf_counter()`.
- Luôn gắn hai response header:
  - `x-request-id`: correlation ID của request;
  - `x-response-time-ms`: thời gian xử lý, tính theo milliseconds.
- Bảo đảm correlation ID vẫn được trả về/gắn header khi downstream ném lỗi
  (phối hợp với exception handler ở mục 3).

### 2. Bổ sung request context cho log `/chat` (CP1)

Thực hiện trong `app/main.py`, trước event `request_received`:

- Bind các trường ngữ cảnh vào `structlog`: `user_id_hash`, `session_id`,
  `feature`, `model`, `env`.
- `user_id_hash` phải được tạo bằng `hash_user_id(body.user_id)`, tuyệt đối
  không bind/log `user_id` gốc.
- Dùng model thực tế của `agent` và `APP_ENV` (mặc định `dev`) cho `model` và
  `env`.
- Giữ các event hiện có (`request_received`, `response_sent`,
  `request_failed`) để dữ liệu tiếp tục tương thích với dashboard và validator.
- Phối hợp với Thành viên B: chỉ log preview/tóm tắt nội dung; không vô hiệu hóa
  processor PII scrubbing mà B bổ sung trong `app/logging_config.py`.

### 3. Bổ sung global exception handler (phần mở rộng)

- Đăng ký handler cho exception không mong muốn ở cấp FastAPI.
- Handler cần:
  - ghi event `request_failed` có `service="api"`, `error_type` và correlation
    ID từ context/request state;
  - gọi `record_error(error_type)` đúng một lần cho mỗi lỗi;
  - trả JSON lỗi HTTP 500 an toàn, không đưa exception detail hoặc dữ liệu đầu
    vào nhạy cảm ra client;
  - giữ/gắn `x-request-id` trên response lỗi để client, log và trace đối chiếu
    được nhau.
- Rà soát `try/except` cục bộ của `/chat` để tránh ghi log hoặc tăng metric lỗi
  hai lần khi dùng handler toàn cục.

## Tiêu chí hoàn thành / bàn giao

- Mỗi request `/chat` có correlation ID hợp lệ, không còn giá trị `"MISSING"`.
- Gửi `x-request-id` từ client phải được giữ nguyên; request không có header
  phải nhận ID mới đúng format `req-xxxxxxxx`.
- Response thành công và response lỗi đều có `x-request-id` và
  `x-response-time-ms`.
- Mọi log `service="api"` có các trường: `correlation_id`, `user_id_hash`,
  `session_id`, `feature`, `model`, `env`; `user_id` thô không xuất hiện.
- Event lỗi chứa `error_type`, metric lỗi được tăng một lần, và response 500
  không rò rỉ chi tiết nội bộ/PII.
- Chạy load test tạo ít nhất hai correlation ID khác nhau, sau đó chạy:

```powershell
python scripts/load_test.py
python scripts/validate_logs.py
python -m pytest -q
```

- Mục tiêu CP1 chung: `validate_logs.py` đạt tối thiểu 80/100. Thành viên B
  chịu trách nhiệm chính về regex/PII scrubbing, nhưng phần A cần không làm mất
  request context hoặc đưa PII thô vào log.

## Phối hợp

- Với B: thống nhất `user_id_hash` và bảo đảm log lỗi/payload đi qua cơ chế
  scrubber.
- Với C/D: giữ nguyên tên event và các trường `request_received`,
  `request_failed`, `error_type`, correlation ID để tính `error_rate_pct`, SLO
  và alert.
- Với E: cung cấp correlation ID từ response/log để nối load-test, trace và log
  trong điều tra CP3.
