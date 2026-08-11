# CP3 — Challenge Investigation Evidence

## Challenge và protocol

- Thời điểm chạy: 2026-08-11, log timestamp theo UTC.
- Challenge ID: `day13-k3-observability-v1`.
- Cohort: `K3`.
- Incident do Lab Coach cung cấp: `rag_slow`.
- Feature bị ảnh hưởng: `refund`.
- Ngưỡng latency: `2000 ms`.
- File `config/challenge.json` chỉ được đọc và validate, không bị sửa.
- Validator: `Hợp lệ: day13-k3-observability-v1`.

## Kết quả load test chính thức

Lệnh đã chạy:

```text
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
```

Kết quả 5 request chính thức:

| Session | Correlation ID | HTTP | Client latency |
|---|---|---:|---:|
| `k3-challenge-s01` | `req-c72d81b1` | 200 | 13283.8 ms |
| `k3-challenge-s02` | `req-aea71952` | 200 | 13282.2 ms |
| `k3-challenge-s03` | `req-7eb026c8` | 200 | 13279.6 ms |
| `k3-challenge-s04` | `req-9ade2039` | 200 | 10627.0 ms |
| `k3-challenge-s05` | `req-8452e3b8` | 200 | 13279.4 ms |

## Metrics

Snapshot trước challenge đã chứa traffic practice cũ:

```json
{"traffic":20,"latency_p50":864.0,"latency_p95":2656.0,"latency_p99":2656.0,"error_rate_pct":0.0}
```

Snapshot sau 5 request challenge:

```json
{"traffic":25,"latency_p50":2651.0,"latency_p95":2652.0,"latency_p99":2656.0,"error_rate_pct":0.0}
```

Do metrics endpoint là số liệu tích lũy và baseline đã có dữ liệu `rag_slow` cũ,
p95 tổng không dùng để so sánh trước/sau. Khi cô lập đúng 5 log challenge, latency
nội bộ là `2651, 2651, 2651, 2651, 2652 ms`; vì vậy p50 challenge là `2651 ms`
và p95 challenge là `2652 ms`. Cả 5/5 request đều vượt ngưỡng `2000 ms` nhưng
không phát sinh lỗi HTTP (`error_rate_pct=0.0`).

## Langfuse traces và waterfall

Langfuse API trả về đúng một trace cho mỗi session chính thức. `correlation_id`
trong metadata khớp với response và log JSONL.

| Session | Trace ID | Correlation ID | `run` | `retrieve` | `generate` |
|---|---|---|---:|---:|---:|
| `k3-challenge-s01` | `c29dac4916f8336ee16121caad0d1b0a` | `req-c72d81b1` | 2654 ms | 2503 ms | 151 ms |
| `k3-challenge-s02` | `3941fc168ec04f727cdfdc28cf6e6cd8` | `req-aea71952` | 2651 ms | 2500 ms | 151 ms |
| `k3-challenge-s03` | `b8704a8e9c1e29d7a123f28605d8f859` | `req-7eb026c8` | 2652 ms | 2502 ms | 150 ms |
| `k3-challenge-s04` | `04b01c48f1f9ffc01b5d0ff16072344e` | `req-9ade2039` | 2653 ms | 2502 ms | 151 ms |
| `k3-challenge-s05` | `71aa65f306c6a3d7ccd478cca78ca126` | `req-8452e3b8` | 2654 ms | 2503 ms | 151 ms |

Trace đại diện `c29dac4916f8336ee16121caad0d1b0a` cho thấy span `retrieve`
mất `2503/2654 ms` (khoảng 94% thời gian của `run`), trong khi `generate` chỉ
mất `151 ms`. Đây là bằng chứng khoanh vùng độ chậm ở RAG, không phải LLM.

## Log thô liên quan

Hai record sau nằm trong `data/logs.jsonl` và có cùng correlation ID với trace
đại diện:

```json
{"service":"api","payload":{"message_preview":"What is your refund policy?"},"event":"request_received","model":"claude-sonnet-4-5","feature":"refund","env":"dev","user_id_hash":"026c7a407135","session_id":"k3-challenge-s01","correlation_id":"req-c72d81b1","level":"info","ts":"2026-08-11T05:08:57.930556Z"}
{"service":"api","latency_ms":2652,"tokens_in":29,"tokens_out":87,"cost_usd":0.001392,"quality_score":0.9,"payload":{"answer_preview":"Starter answer. Teams should improve this output logic and add better quality ch..."},"event":"response_sent","model":"claude-sonnet-4-5","feature":"refund","env":"dev","user_id_hash":"026c7a407135","session_id":"k3-challenge-s01","correlation_id":"req-c72d81b1","level":"info","ts":"2026-08-11T05:09:00.584662Z"}
```

Control log xác nhận incident chính thức được bật lúc
`2026-08-11T05:08:51.830888Z`. Sau điều tra, incident đã được tắt và `/health`
xác nhận `rag_slow=false`, `tool_fail=false`, `cost_spike=false`.

## Kết luận và khắc phục

- Root cause trực tiếp: scenario `rag_slow` thêm khoảng 2,5 giây vào RAG retrieval.
- Yếu tố khuếch đại: retrieval đồng bộ/blocking được gọi trong FastAPI async
  handler, nên 5 request concurrent bị xếp hàng; client latency tăng tới khoảng
  10,6–13,3 giây dù latency nội bộ từng request là khoảng 2,65 giây.
- Fix action: kiểm tra và tối ưu vector-store/index/network; đặt timeout dưới SLO,
  fallback khi RAG chậm; chuyển I/O retrieval sang async hoặc offload khỏi event loop.
- Preventive measure: cảnh báo theo latency riêng của span `retrieve`, theo dõi event-loop
  lag và queue time, chạy load test concurrent trong CI/staging, thêm timeout/circuit
  breaker và regression test cho p95.

## Câu hỏi phản biện

**Bằng chứng nào khẳng định root cause?** Metrics và 5 log challenge xác nhận triệu
chứng latency vượt ngưỡng; trace waterfall độc lập cho cả 5 request đều chỉ ra
`retrieve` mất khoảng 2,5 giây trong khi `generate` chỉ khoảng 0,15 giây; metadata
`correlation_id` nối từng trace với đúng log. Sự lặp lại nhất quán ở ba lớp loại trừ
LLM và lỗi ngẫu nhiên, đồng thời khớp với incident `rag_slow` trong challenge chính thức.

**Nếu chỉ có metrics thì khó khăn gì?** Metrics chỉ cho biết hệ thống chậm trong khoảng
thời gian nào, không cho biết request, feature hay sub-component gây chậm. Không có
trace và log, nhóm không thể phân biệt RAG chậm, LLM chậm, queueing hay lỗi mạng; root
cause khi đó chỉ là phỏng đoán và không có correlation ID để tái dựng hành trình request.

## Evidence UI

- Dashboard CP3: [cp3_dashboard_metrics.png](cp3_dashboard_metrics.png), thể hiện
  traffic 25, P50 2651 ms và P95 2652 ms.
- Log CP3: [cp3_log_correlation.png](cp3_log_correlation.png), thể hiện cặp event
  của `req-c72d81b1`, session `k3-challenge-s01` và `latency_ms=2652`.
- Waterfall UI: [trace_waterfall.png](trace_waterfall.png), thể hiện cấu trúc
  `run → retrieve/generate`. Bảng Langfuse API ở trên cung cấp trace ID, duration
  và correlation ID cụ thể của năm request challenge.

Không để API key hoặc thông tin đăng nhập xuất hiện trong ảnh.
