# PII Redaction Evidence — Member B (Security Engineer)

Scope: `app/pii.py` (regex patterns) + `app/logging_config.py` (`scrub_event` processor
wired into the structlog pipeline). First generated 2026-08-11 on the PII-only branch;
updated 2026-08-11 after merging `origin/dev` (Member A's `CorrelationID` commit
`f043f4f`, branch `Manh`) into `Van`, to show the combined result of both roles.

## 1. Test inputs sent to `/chat` (raw, contain real-looking PII)

| # | PII type | Raw input sent |
|---|---|---|
| 1 | email | `What is your refund policy? My email is student@vinuni.edu.vn` |
| 2 | phone_vn | `Here is my phone 0987654321, what should be logged?` |
| 3 | credit_card | `What is the policy for PII and credit card 4111 1111 1111 1111?` |
| 4 | cccd | `CCCD cua toi la 012345678901, xin dung luu lai` |
| 5 | passport_vn | `Ho chieu cua toi la B1234567, can ho tro` |
| 6 | address_vn | `Giao hang toi so nha 12 Nguyen Trai giup minh` |

## 2. Resulting log lines in `data/logs.jsonl` (after merge — redaction + correlation ID + enrichment together)

```json
{"service": "api", "payload": {"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-c0634a79", "user_id_hash": "2055254ee30a", "session_id": "s01", "env": "dev", "level": "info", "ts": "2026-08-11T03:23:03.940251Z"}
{"service": "api", "payload": {"message_preview": "Here is my phone [REDACTED_PHONE_VN], what should be logged?"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-f996668e", "user_id_hash": "64f6ec689229", "session_id": "s05", "env": "dev", "level": "info", "ts": "2026-08-11T03:23:09.062045Z"}
{"service": "api", "payload": {"message_preview": "What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-8c711566", "user_id_hash": "4d14d5d4f719", "session_id": "s09", "env": "dev", "level": "info", "ts": "2026-08-11T03:23:13.559611Z"}
{"service": "api", "payload": {"message_preview": "CCCD cua toi la [REDACTED_CCCD], xin dung luu lai"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-6fe4c48f", "user_id_hash": "92ec86fa8892", "session_id": "s11", "env": "dev", "level": "info", "ts": "2026-08-11T03:23:16.019263Z"}
{"service": "api", "payload": {"message_preview": "Ho chieu cua toi la [REDACTED_PASSPORT_VN], can ho tro"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-3b61bf05", "user_id_hash": "a50656c6edf2", "session_id": "s12", "env": "dev", "level": "info", "ts": "2026-08-11T03:23:17.254519Z"}
{"service": "api", "payload": {"message_preview": "Giao hang toi [REDACTED_ADDRESS_VN]"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-8010e845", "user_id_hash": "9607720f9f1c", "session_id": "s13", "env": "dev", "level": "info", "ts": "2026-08-11T03:23:18.488211Z"}
```

No raw email address, phone number, card number, CCCD number, passport number, or house
number from the inputs above appears anywhere in `data/logs.jsonl`. `user_id_hash` is a
SHA-256-derived hash (`hash_user_id`), never the raw `user_id` — scrubbing and the
correlation-ID/enrichment work (Member A) do not interfere with each other.

## 3. `python scripts/validate_logs.py` output (after merging Member A's `CorrelationID` commit)

```text
--- Lab Verification Results ---
Total log records analyzed: 27
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 13
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
+ [PASSED] Basic JSON schema
+ [PASSED] Correlation ID propagation
+ [PASSED] Log enrichment
+ [PASSED] PII scrubbing

Estimated Score: 100/100
```

Before the merge (PII scrubbing alone, on top of the un-merged `middleware.py` TODOs),
the same test run scored 30/100 with only `+ [PASSED] PII scrubbing` passing — see git
history of this file. `Potential PII leaks detected: 0` held in both runs, confirming the
scrubbing logic itself does not depend on correlation ID/enrichment being present.

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
