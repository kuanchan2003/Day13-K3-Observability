# Xác minh Checkpoint 2

Thời điểm xác minh: ngày 11/08/2026 (múi giờ Asia/Bangkok).

## Dashboard và log

```text
HỢP LỆ: 6/6 panel có trong dashboard contract.

Tổng số bản ghi log đã phân tích: 46
Số bản ghi thiếu trường bắt buộc: 0
Số bản ghi thiếu thông tin ngữ cảnh: 0
Số correlation ID duy nhất: 20
Số trường hợp có khả năng rò rỉ PII: 0
Điểm ước tính: 100/100
```

Bằng chứng dashboard runtime: [cp2_dashboard_runtime.png](cp2_dashboard_runtime.png).
Ảnh chụp hiển thị đủ sáu nhóm chỉ số, khoảng thời gian 60 phút gần nhất, chu kỳ
làm mới 30 giây, đơn vị đo và các ngưỡng SLO, ngân sách, chất lượng.

## Phiên bản prompt và rollback

Langfuse API trả về trạng thái label cuối cùng sau khi thực hiện chuyển
`production` sang candidate và rollback:

```text
prompt_name=day13-chat
baseline=v1
candidate=v2
production=v1
promotion_production_version=2
rollback_production_version=1
rollback_status=PASSED
```

Script `scripts/setup_prompt_versions.py` tạo các phiên bản nếu chưa tồn tại,
chạy cùng một input với cả hai label, tạm thời chuyển `production` sang v2 rồi
rollback về v1. Sau khi kết thúc minh họa, label `production` được chủ động giữ
ở phiên bản baseline.

## Bằng chứng trace

Truy vấn Langfuse API cho session `cp2-prompt-versioning` trả về 12 trace. Tất
cả trace đều có các trường `prompt_name`, `prompt_label`, `prompt_version` và
`correlation_id` trong metadata.

| Trace ID | Label | Phiên bản | Correlation ID |
|---|---|---:|---|
| `59d45158a862f335a8cc85b1ffeb1f69` | baseline | 1 | `req-3ac55d0d` |
| `6df1c593f2908e65c370427ab69648c2` | candidate | 2 | `req-9bc8db80` |
| `81fa52f59414b8f403a71e5cc27b2a80` | baseline | 1 | `req-cd8f7d7d` |
| `ec08bc379c0bdb34b8f7ef6047a514b5` | candidate | 2 | `req-433b486c` |
| `2d0ce01489b8f8df03ca4a6b8391c7cf` | baseline | 1 | `req-924cd85c` |
| `5a0718ff5505e08105f0d1aff2f848a0` | candidate | 2 | `req-edb13660` |
| `02aa904503e66d40609d2bc57bb9d373` | baseline | 1 | `req-609402e5` |
| `5e2853c22309fbbd95c459e56f3f416d` | candidate | 2 | `req-aae782a4` |
| `bb09b0ee11b6b990b2dbb2e29415b194` | baseline | 1 | `req-ba1b0e04` |
| `f0c866cde23a01eda9a7d8acd8389018` | candidate | 2 | `req-8d41245b` |
| `0125de649d46819efc514c9bd6a27ec3` | baseline | 1 | `req-600a49e5` |
| `ad69fa868f854c733e0386392737735a` | candidate | 2 | `req-23aea27d` |

## Ảnh chụp cần bổ sung thủ công

Bằng chứng API ở trên đã đầy đủ, tuy nhiên rubric còn yêu cầu ảnh chụp giao diện
Langfuse. Hãy đăng nhập Langfuse Cloud, mở một trace baseline và một trace
candidate trong bảng, sau đó chụp trang phiên bản prompt thể hiện `production`
đang trỏ tới v1. Không để thông tin đăng nhập hoặc API key xuất hiện trong ảnh.
