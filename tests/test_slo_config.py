from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SLO_PATH = REPO_ROOT / "config" / "slo.yaml"
DASHBOARD_PATH = REPO_ROOT / "config" / "dashboard.yaml"

EXPECTED_SLIS = {
    "latency_p95_ms": ("latency", "lte"),
    "error_rate_pct": ("errors", "lte"),
    "daily_cost_usd": ("cost", "lte"),
    "quality_score_avg": ("quality", "gte"),
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_slo_config_is_complete_and_has_no_placeholders() -> None:
    raw = SLO_PATH.read_text(encoding="utf-8")
    config = load_yaml(SLO_PATH)

    assert "todo" not in raw.lower()
    assert "replace with" not in raw.lower()
    assert config["service"] == "day13-observability-lab"
    assert config["window"] == "28d"
    assert set(config["slis"]) == set(EXPECTED_SLIS)
    assert config["semantics"]["objective"]
    assert config["semantics"]["target"]

    for sli in config["slis"].values():
        assert isinstance(sli["objective"], (int, float))
        assert isinstance(sli["target"], (int, float))
        assert 0 < sli["target"] <= 100
        assert sli["comparison"] in {"lte", "gte"}
        assert sli["unit"]
        assert sli["note"]


def test_slo_objectives_match_dashboard_thresholds() -> None:
    slis = load_yaml(SLO_PATH)["slis"]
    panels = {
        panel["id"]: panel
        for panel in load_yaml(DASHBOARD_PATH)["dashboard"]["panels"]
    }

    for sli_name, (panel_id, comparison) in EXPECTED_SLIS.items():
        threshold = panels[panel_id]["threshold"]
        assert slis[sli_name]["objective"] == threshold["value"]
        assert slis[sli_name]["comparison"] == comparison
        assert threshold["operator"] == comparison
