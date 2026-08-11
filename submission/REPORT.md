# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 sau khi merge `origin/dev` (correlation ID + enrichment của Thành viên A, commit `f043f4f`) vào nhánh `Van` — xem [pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) mục 3 (trước merge: 30/100, chỉ PII scrubbing PASSED).
- Tổng số traces: 12 trace CP2 đã xác minh qua Langfuse API trong session `cp2-prompt-versioning`; xem [cp2_verification.md](evidence/cp2_verification.md).
- Số PII leak còn lại: 0 (`Potential PII leaks detected: 0`, xác nhận qua 6 loại PII: email, phone_vn, cccd, credit_card, passport, address_vn)
- Link/đường dẫn dashboard: `http://localhost:8000/dashboard`; ảnh runtime [cp2_dashboard_runtime.png](evidence/cp2_dashboard_runtime.png).

## 3. Logging và tracing

- Evidence correlation ID: [pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) mục 2 (log có `correlation_id` dạng `req-xxxxxxxx`, không còn `MISSING`) — triển khai bởi Thành viên A (`app/middleware.py`, commit `f043f4f`); Thành viên B xác nhận không xung đột với PII scrubbing.
- Evidence PII redaction: [submission/evidence/pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) — 6 loại PII (email, phone_vn, cccd, credit_card, passport, address_vn) test qua `/chat`, đối chiếu raw input vs log đã redact trong `data/logs.jsonl`, cộng kết quả `validate_logs.py` (`+ [PASSED] PII scrubbing`, `Potential PII leaks detected: 0`) và các lệnh `grep` thủ công theo đúng checklist checkpoint chính thức.
- Evidence trace waterfall: trace baseline `59d45158a862f335a8cc85b1ffeb1f69` và candidate `6df1c593f2908e65c370427ab69648c2`; danh sách đủ 12 trace tại [cp2_verification.md](evidence/cp2_verification.md).
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label baseline: v1, labels `baseline` và `production` (trạng thái cuối).
- Version/label candidate: v2, label `candidate`.
- Trace ID của mỗi version: baseline `59d45158a862f335a8cc85b1ffeb1f69`; candidate `6df1c593f2908e65c370427ab69648c2`.
- Bằng chứng đổi label hoặc rollback: promotion xác nhận `production=v2`, sau đó rollback xác nhận `production=v1`, `rollback_status=PASSED`; xem [cp2_verification.md](evidence/cp2_verification.md).

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: [cp2_dashboard_runtime.png](evidence/cp2_dashboard_runtime.png), hiển thị 6 panel, time range 60 phút, refresh 30 giây, đơn vị và threshold.
- SLO đã chọn và lý do: P95 ≤ 3.000 ms và error rate ≤ 2% để phản ánh trực tiếp độ chậm/lỗi người dùng; budget ≤ 2,50 USD và quality ≥ 0,75 làm guardrail vận hành.
- Alert rules và runbook: ba alert symptom-based cho latency, error rate và quality trong [`config/alert_rules.yaml`](../config/alert_rules.yaml), quy trình xử lý tại [`docs/alerts.md`](../docs/alerts.md).

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
