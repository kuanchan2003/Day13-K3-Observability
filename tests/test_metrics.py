from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_calculates_dynamic_error_rate(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 3)
    monkeypatch.setattr(metrics, "ERRORS", metrics.Counter({"TimeoutError": 1}))

    assert metrics.snapshot()["error_rate_pct"] == 25.0

    metrics.ERRORS["ValueError"] += 1

    assert metrics.snapshot()["error_rate_pct"] == 40.0


def test_snapshot_error_rate_is_zero_without_requests(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    monkeypatch.setattr(metrics, "ERRORS", metrics.Counter())

    assert metrics.snapshot()["error_rate_pct"] == 0.0
