# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: B6
- Repository URL: https://github.com/kuanchan2003/Day13-K3-Observability
- Commit SHA cuối: `01a5902d09701f4f5fe57df9ef62bbb548eb2eea` (HEAD trước commit hoàn thiện báo cáo; cập nhật lại sau commit nộp bài nếu có).
- Thành viên và vai trò:
  - Nguyễn Trần Nguyên Mạnh — `2A2026` — Thành viên A, API & Middleware.
  - Lê Hà Hải Vân — `2A202601587` — Thành viên B, Security Engineer.
  - Tạ Minh Đức — `2A202601497` — Thành viên C, Metrics & Dashboard.
  - Phạm Thành Long — `2A202601259` — Thành viên D, SRE & Alerts Engineer.
  - Trần Anh Quân — `2A202601997` — Thành viên E, QA & Chief Investigator, Leader.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 — 105 records, 0 record thiếu required fields/enrichment, 49 correlation IDs, 0 PII leak; xem [final_validation.txt](evidence/final_validation.txt).
- Tổng số traces: 17 trace có evidence đã xác minh qua Langfuse API (12 trace CP2 trong [cp2_verification.md](evidence/cp2_verification.md) và 5 trace CP3 trong [cp3_challenge_investigation.md](evidence/cp3_challenge_investigation.md)).
- Số PII leak còn lại: 0 (`Potential PII leaks detected: 0`, xác nhận qua 6 loại PII: email, phone_vn, cccd, credit_card, passport, address_vn)
- Link/đường dẫn dashboard: `http://localhost:8000/dashboard`; ảnh runtime [cp2_dashboard_runtime.png](evidence/cp2_dashboard_runtime.png).

## 3. Logging và tracing

- Evidence correlation ID: [cp1_correlation_id_redacted_log.png](evidence/cp1_correlation_id_redacted_log.png) và [pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) cho thấy `correlation_id` dạng `req-xxxxxxxx` đi cùng `user_id_hash`, `session_id`, `feature`, `model`, `env`; validator cuối không còn `MISSING`.
- Evidence PII redaction: [pii_redaction_evidence.md](evidence/pii_redaction_evidence.md) và [cp1_correlation_id_redacted_log.png](evidence/cp1_correlation_id_redacted_log.png) kiểm chứng email, phone_vn, cccd, credit_card, passport và address_vn được che; validator cuối xác nhận 0 PII leak.
- Evidence trace waterfall: [trace_waterfall.png](evidence/trace_waterfall.png) thể hiện cấu trúc sub-span `run → retrieve/generate`; dữ liệu Langfuse API của trace CP3 `c29dac4916f8336ee16121caad0d1b0a` và duration từng span tại [cp3_challenge_investigation.md](evidence/cp3_challenge_investigation.md); danh sách trace CP2 tại [cp2_verification.md](evidence/cp2_verification.md).
- Giải thích một span đáng chú ý: trong trace challenge `c29dac4916f8336ee16121caad0d1b0a`, span `retrieve` mất 2503 ms trên tổng 2654 ms của `run` (khoảng 94%), còn `generate` chỉ mất 151 ms; xem [cp3_challenge_investigation.md](evidence/cp3_challenge_investigation.md).

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label baseline: v1, labels `baseline` và `production` (trạng thái cuối).
- Version/label candidate: v2, label `candidate`.
- Trace ID của mỗi version: baseline `59d45158a862f335a8cc85b1ffeb1f69`; candidate `6df1c593f2908e65c370427ab69648c2`.
- Bằng chứng đổi label hoặc rollback: promotion xác nhận `production=v2`, sau đó rollback xác nhận `production=v1`, `rollback_status=PASSED`; xem [cp2_verification.md](evidence/cp2_verification.md).

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`; xem [final_validation.txt](evidence/final_validation.txt).
- Evidence dashboard: [cp2_dashboard_runtime.png](evidence/cp2_dashboard_runtime.png) và [cp3_dashboard_metrics.png](evidence/cp3_dashboard_metrics.png), hiển thị đủ 6 panel, time range 60 phút, refresh 30 giây, đơn vị/threshold; ảnh CP3 ghi nhận traffic 25, P50 2651 ms và P95 2652 ms.
- SLO đã chọn và lý do: P95 ≤ 3.000 ms và error rate ≤ 2% để phản ánh trực tiếp độ chậm/lỗi người dùng; budget ≤ 2,50 USD và quality ≥ 0,75 làm guardrail vận hành.
- Alert rules và runbook: ba alert symptom-based cho latency, error rate và quality trong [`config/alert_rules.yaml`](../config/alert_rules.yaml), quy trình xử lý tại [`docs/alerts.md`](../docs/alerts.md).

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1` (`rag_slow`, feature `refund`, ngưỡng 2000 ms).
- Triệu chứng từ metrics: traffic tăng từ 20 lên 25; p50 tích lũy tăng từ 864 ms lên 2651 ms. Khi cô lập 5 request challenge từ log, p50 = 2651 ms, p95 = 2652 ms và 5/5 request vượt ngưỡng 2000 ms; error rate vẫn 0%. Client latency dưới concurrency 5 tăng tới 10,6–13,3 giây.
- Trace ID liên quan: `c29dac4916f8336ee16121caad0d1b0a` (session `k3-challenge-s01`); waterfall: `run=2654 ms`, `retrieve=2503 ms`, `generate=151 ms`.
- Log line/correlation ID liên quan: `req-c72d81b1`; cặp event `request_received` lúc `2026-08-11T05:08:57.930556Z` và `response_sent` lúc `2026-08-11T05:09:00.584662Z`, trong đó `latency_ms=2652`. Evidence: [cp3_log_correlation.png](evidence/cp3_log_correlation.png) và [cp3_challenge_investigation.md](evidence/cp3_challenge_investigation.md).
- Root cause: RAG retrieval bị scenario `rag_slow` thêm khoảng 2,5 giây; Langfuse cho thấy `retrieve` chiếm khoảng 94% thời gian `run`, loại trừ LLM (`generate` chỉ khoảng 151 ms). Lời gọi blocking trong async request handler còn làm các request concurrent xếp hàng, khuếch đại latency end-to-end.
- Fix action: kiểm tra/tối ưu vector store, index và network; đặt timeout dưới SLO và fallback khi retrieval chậm; chuyển retrieval sang async hoặc offload blocking I/O khỏi event loop.
- Preventive measure: cảnh báo latency riêng cho span `retrieve`, theo dõi event-loop lag/queue time, thêm timeout và circuit breaker, đồng thời chạy regression/load test concurrency trong CI hoặc staging.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Trần Nguyên Mạnh (`2A2026`) — A | CP1 API & Middleware: tạo/propagate Correlation ID, bind request context, bổ sung exception handler và chuyển startup sang lifespan. | [`f043f4f`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/f043f4f3f8ebeca035c4e773bf3c27fa4470bbe2), [`b6d2904`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/b6d2904413a71aca5364919865ffed9318a957c3), [`7f4e5cf`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/7f4e5cf4bfc2f0f5f0e27ab46f8d8fc6fb55675b) | Context request cần được bind một lần ở middleware và vẫn phải truy xuất được trong đường lỗi; lifespan thay thế API startup đã deprecated. |
| Lê Hà Hải Vân (`2A202601587`) — B | CP1 PII Scrubbing: hoàn thiện regex, processor `scrub_event`, test và evidence xác nhận log không lộ PII. | [`9554a15`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/9554a1559fac81c5853c8037350ec14ea786b4e7), [`14f9204`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/14f9204c6830df85f7c16a17acfc53addfc82da4), [`531333f`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/531333f11b6c410fe78e8f2dcf51b019d8eeef4f) | Redaction phải nằm trước JSON rendering và áp dụng cho mọi field string; từng loại PII cần test dương/âm để tránh cả leak lẫn che nhầm. |
| Tạ Minh Đức (`2A202601497`) — C | CP1/CP2 Metrics & Dashboard: bổ sung error metrics/tests, dựng dashboard 6 panel, workflow prompt versioning và evidence CP2. | [`ae824b6`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/ae824b6dd067abab5fc1e0177082895469e0ec64), [`cc1240e`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/cc1240ebab3170223700c7078c82ef95e5749a78), [`93e9691`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/93e96914c252ebf541a703b19369e9f9c208f079), [`6f4e9a9`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/6f4e9a9af3dc31b698e80d31fe18b320ff4a40f0) | Dashboard hữu ích phải gắn đúng nguồn event/field, đơn vị và threshold; prompt version cần trace metadata và rollback kiểm chứng được. |
| Phạm Thành Long (`2A202601259`) — D | CP2 SRE & Alerts: thiết lập SLO 28 ngày, ba alert symptom-based, runbook Metrics → Traces → Logs và test cấu hình. | [`abf8e9f`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/abf8e9fc90e5a3bc7eda177c9b83c900ac21f941) | Alert cần duration, severity, owner, escalation và điều kiện đóng; `objective` kỹ thuật khác với tỷ lệ `target` trong cửa sổ SLO. |
| Trần Anh Quân (`2A202601997`) — E, Leader | QA & Chief Investigator: liên kết correlation ID vào Langfuse, thêm sub-span RAG/LLM không capture PII, chạy load test/challenge, phân tích Metrics → Traces → Logs và hoàn thiện report. | [`2ff0b14`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/2ff0b14774ae4d1e81176f0022c20fefc298f4e3), [`35a4410`](https://github.com/kuanchan2003/Day13-K3-Observability/commit/35a44103a526f6b656acf4697f70472b71b9fa7e); phần CP3/report đang ở working tree, cần commit trước khi nộp | Correlation ID nối trace với log; sub-span khoanh vùng `retrieve` là nút thắt, nhưng phải tắt capture input/output để tránh gửi PII sang Langfuse. |

Checklist evidence trước khi nộp: [submission_checklist.md](evidence/submission_checklist.md).
