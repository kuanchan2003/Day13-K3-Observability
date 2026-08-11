# Kiểm kê evidence trước khi nộp

| Yêu cầu | Evidence | Trạng thái |
|---|---|---|
| `validate_logs.py` cuối cùng | [final_validation.txt](final_validation.txt), [cp1_validate_logs_score.png](cp1_validate_logs_score.png) | Đạt: 100/100; ảnh CP1 là lần chạy trước, file text là kết quả cuối 105 records |
| Danh sách tối thiểu 10 traces | [cp2_verification.md](cp2_verification.md), [cp3_challenge_investigation.md](cp3_challenge_investigation.md) | Đạt: 17 trace đã xác minh (12 CP2 + 5 CP3) |
| Trace waterfall đầy đủ | [trace_waterfall.png](trace_waterfall.png), [cp3_challenge_investigation.md](cp3_challenge_investigation.md) | Đạt: ảnh thể hiện `run → retrieve/generate`; dữ liệu API liên kết waterfall CP3 với trace/correlation ID cụ thể |
| Log có correlation ID và metadata | [cp1_correlation_id_redacted_log.png](cp1_correlation_id_redacted_log.png), [pii_redaction_evidence.md](pii_redaction_evidence.md) | Đạt |
| Log chứng minh PII đã redact | [cp1_correlation_id_redacted_log.png](cp1_correlation_id_redacted_log.png), [pii_redaction_evidence.md](pii_redaction_evidence.md) | Đạt: 0 leak |
| Hai prompt version + rollback | [cp2_verification.md](cp2_verification.md) | Đạt: v1/v2, promotion và rollback |
| Dashboard đủ 6 nhóm | [cp2_dashboard_runtime.png](cp2_dashboard_runtime.png), [final_validation.txt](final_validation.txt) | Đạt: 6/6 |
| Alert rules và runbook | [`config/alert_rules.yaml`](../../config/alert_rules.yaml), [`docs/alerts.md`](../../docs/alerts.md) | Đạt |
| Điều tra challenge | [cp3_dashboard_metrics.png](cp3_dashboard_metrics.png), [cp3_log_correlation.png](cp3_log_correlation.png), [trace_waterfall.png](trace_waterfall.png), [cp3_challenge_investigation.md](cp3_challenge_investigation.md) | Đạt: metrics, trace API/waterfall, log và kết luận root cause |
