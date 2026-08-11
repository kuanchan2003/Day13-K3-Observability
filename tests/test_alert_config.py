from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ALERT_PATH = REPO_ROOT / "config" / "alert_rules.yaml"
SLO_PATH = REPO_ROOT / "config" / "slo.yaml"
ALLOWED_SEVERITIES = {"warning", "critical"}
EXPECTED_ALERTS = {
    "HighLatencyP95": ("latency_p95_ms", ">", "latency_p95_ms"),
    "HighErrorRate": ("error_rate_pct", ">", "error_rate_pct"),
    "DailyCostBudgetRisk": ("daily_cost_usd", ">", "daily_cost_usd"),
}
CONDITION_PATTERN = re.compile(
    r"^(?P<metric>[a-z][a-z0-9_]*)\s*(?P<operator>>=|<=|>|<)\s*(?P<value>\d+(?:\.\d+)?)$"
)
DURATION_PATTERN = re.compile(r"^[1-9]\d*[mhd]$")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_alert_config_is_complete() -> None:
    raw = ALERT_PATH.read_text(encoding="utf-8")
    alerts = load_yaml(ALERT_PATH)["alerts"]

    assert "todo" not in raw.lower()
    assert len(alerts) == 3
    assert {alert["name"] for alert in alerts} == set(EXPECTED_ALERTS)

    for alert in alerts:
        assert alert["severity"] in ALLOWED_SEVERITIES
        assert alert["type"] == "symptom-based"
        assert alert["owner"].strip()
        assert DURATION_PATTERN.fullmatch(alert["for"])
        assert CONDITION_PATTERN.fullmatch(alert["condition"])
        assert alert["runbook"].startswith("docs/alerts.md#")


def test_alert_thresholds_match_slo_objectives() -> None:
    alerts = {alert["name"]: alert for alert in load_yaml(ALERT_PATH)["alerts"]}
    slis = load_yaml(SLO_PATH)["slis"]

    for alert_name, (metric, operator, sli_name) in EXPECTED_ALERTS.items():
        match = CONDITION_PATTERN.fullmatch(alerts[alert_name]["condition"])
        assert match is not None
        assert match.group("metric") == metric
        assert match.group("operator") == operator
        assert float(match.group("value")) == float(slis[sli_name]["objective"])


def test_every_runbook_link_targets_an_existing_heading() -> None:
    alerts = load_yaml(ALERT_PATH)["alerts"]

    for alert in alerts:
        relative_path, anchor = alert["runbook"].split("#", maxsplit=1)
        document = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        expected_heading = f"## {alert['name']}"

        assert anchor == alert["name"].lower()
        assert expected_heading in document
