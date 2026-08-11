# PII Redaction Evidence — Member B (Security Engineer)

Scope: `app/pii.py` (regex patterns) + `app/logging_config.py` (`scrub_event` processor
wired into the structlog pipeline). Generated on 2026-08-11 against `data/logs.jsonl`.

## 1. Test inputs sent to `/chat` (raw, contain real-looking PII)

| # | PII type | Raw input sent |
|---|---|---|
| 1 | email | `What is your refund policy? My email is student@vinuni.edu.vn` |
| 2 | phone_vn | `Here is my phone 0987654321, what should be logged?` |
| 3 | credit_card | `What is the policy for PII and credit card 4111 1111 1111 1111?` |
| 4 | cccd | `CCCD cua toi la 012345678901, xin dung luu lai` |
| 5 | passport_vn | `Ho chieu cua toi la B1234567, can ho tro` |
| 6 | address_vn | `Giao hang toi so nha 12 Nguyen Trai giup minh` |

## 2. Resulting log lines in `data/logs.jsonl` (after redaction)

```json
{"service": "api", "payload": {"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"}, "event": "request_received", "level": "info", "ts": "2026-08-11T03:09:12.567789Z"}
{"service": "api", "payload": {"message_preview": "Here is my phone [REDACTED_PHONE_VN], what should be logged?"}, "event": "request_received", "level": "info", "ts": "2026-08-11T03:09:17.458205Z"}
{"service": "api", "payload": {"message_preview": "What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"}, "event": "request_received", "level": "info", "ts": "2026-08-11T03:09:21.916211Z"}
{"service": "api", "payload": {"message_preview": "CCCD cua toi la [REDACTED_CCCD], xin dung luu lai"}, "event": "request_received", "level": "info", "ts": "2026-08-11T03:09:24.302657Z"}
{"service": "api", "payload": {"message_preview": "Ho chieu cua toi la [REDACTED_PASSPORT_VN], can ho tro"}, "event": "request_received", "level": "info", "ts": "2026-08-11T03:09:25.440676Z"}
{"service": "api", "payload": {"message_preview": "Giao hang toi [REDACTED_ADDRESS_VN]"}, "event": "request_received", "level": "info", "ts": "2026-08-11T03:09:26.640601Z"}
```

No raw email address, phone number, card number, CCCD number, passport number, or house
number from the inputs above appears anywhere in `data/logs.jsonl`.

## 3. `python scripts/validate_logs.py` output

```text
--- Lab Verification Results ---
Total log records analyzed: 26
Records with missing required fields: 26
Records with missing enrichment (context): 26
Unique correlation IDs found: 0
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
- [FAILED] Missing required fields (ts, level, etc.)
- [FAILED] Correlation ID propagation (less than 2 unique IDs)
- [FAILED] Log enrichment (missing user_id_hash, etc.)
+ [PASSED] PII scrubbing

Estimated Score: 30/100
```

`+ [PASSED] PII scrubbing` and `Potential PII leaks detected: 0` are the evidence for this
role. The other three FAILED lines (correlation ID, enrichment, required fields) are
Member A's scope (`app/middleware.py`, request context binding) — not part of CP1 PII
scrubbing.

## 4. What was implemented (commit `9554a15`, "Member B done CP1")

- `app/pii.py`: added `passport_vn` (1 letter + 7 digits) and `address_vn` (Vietnamese
  address keyword + house number) patterns, on top of the pre-existing `email`,
  `phone_vn`, `cccd`, `credit_card`.
- `app/logging_config.py`: registered the previously-unused `scrub_event` processor into
  the structlog pipeline, right before the JSONL file write. This closes a real gap:
  `app/main.py:88` logs `payload={"detail": str(exc), ...}` on the error path, and
  `str(exc)` was never passed through `summarize_text()` — so any exception message that
  happened to echo user input would have written raw PII to disk. `scrub_event` scrubs
  every string field in `payload` and in `event`, independent of whether the call site
  remembered to sanitize manually.
- `tests/test_pii.py`: added unit tests for `passport_vn`, `address_vn`, `credit_card`,
  `cccd`, and a direct test of `scrub_event` proving the `detail` field gets redacted.

## 5. Automated test coverage

`python -m pytest -q` → 27 passed, including 6 PII-specific tests in `tests/test_pii.py`.
