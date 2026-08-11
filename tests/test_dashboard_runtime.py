from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_exposes_six_metric_groups_and_runtime_settings() -> None:
    with TestClient(app) as client:
        response = client.get("/dashboard")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    for title in (
        "Latency percentiles",
        "Request traffic",
        "Error rate &amp; breakdown",
        "Cost over time",
        "Input &amp; output tokens",
        "Quality proxy",
    ):
        assert title in response.text
    assert "Last 60 minutes" in response.text
    assert "Refresh 30s" in response.text
    assert "fetch('/metrics'" in response.text


def test_metrics_contract_contains_all_dashboard_values() -> None:
    with TestClient(app) as client:
        payload = client.get("/metrics").json()

    assert {
        "traffic",
        "latency_p50",
        "latency_p95",
        "latency_p99",
        "avg_cost_usd",
        "total_cost_usd",
        "tokens_in_total",
        "tokens_out_total",
        "error_rate_pct",
        "error_breakdown",
        "quality_avg",
    } <= payload.keys()
