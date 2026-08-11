# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 sau khi merge `origin/dev` (correlation ID + enrichment của Thành viên A, commit `f043f4f`) vào nhánh `Van` — xem [pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) mục 3 (trước merge: 30/100, chỉ PII scrubbing PASSED).
- Tổng số traces:
- Số PII leak còn lại: 0 (`Potential PII leaks detected: 0`, xác nhận qua 6 loại PII: email, phone_vn, cccd, credit_card, passport, address_vn)
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: [pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) mục 2 (log có `correlation_id` dạng `req-xxxxxxxx`, không còn `MISSING`) — triển khai bởi Thành viên A (`app/middleware.py`, commit `f043f4f`); Thành viên B xác nhận không xung đột với PII scrubbing.
- Evidence PII redaction: [submission/evidence/pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) — 6 loại PII (email, phone_vn, cccd, credit_card, passport, address_vn) test qua `/chat`, đối chiếu raw input vs log đã redact trong `data/logs.jsonl`, cộng kết quả `validate_logs.py` (`+ [PASSED] PII scrubbing`, `Potential PII leaks detected: 0`) và các lệnh `grep` thủ công theo đúng checklist checkpoint chính thức.
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

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| B (Security Engineer) | CP1 PII Scrubbing: thêm pattern `passport`/`address_vn` vào `app/pii.py`; đăng ký và sau đó mở rộng processor `scrub_event` trong `app/logging_config.py` để redact mọi field string/dict cấp cao nhất trong log (không chỉ `payload`/`event`), theo đúng Bước 3b của checkpoint chính thức; thêm/điều chỉnh unit test cho các pattern và cho `scrub_event`. | `9554a15`, evidence follow-up sau khi merge `origin/dev` | Redaction phải nằm ở tầng processor (áp dụng cho mọi log call) thay vì chỉ gọi `summarize_text` thủ công ở từng chỗ; khi có spec chính thức từ Lab Coach, nên đối chiếu tên pattern/regex chính xác thay vì tự đặt tên khác dù regex tự viết chặt hơn. |
