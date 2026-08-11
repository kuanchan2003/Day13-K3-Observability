from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from structlog.contextvars import bind_contextvars, clear_contextvars

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.agent import LabAgent
from app.prompt_management import DEFAULT_PROMPT_TEMPLATE
from app.tracing import get_langfuse_client


CANDIDATE_PROMPT_TEMPLATE = (
    "Feature={{feature}}\n"
    "Docs={{docs}}\n"
    "Question={{message}}\n"
    "Answer concisely and cite only the supplied docs."
)
DEMO_MESSAGE = "What is the refund policy?"


def _get_prompt_by_label(client, name: str, label: str):
    try:
        return client.get_prompt(
            name,
            label=label,
            type="text",
            cache_ttl_seconds=0,
            max_retries=0,
            fetch_timeout_seconds=5,
        )
    except Exception:
        return None


def _ensure_versions(client, name: str):
    baseline = _get_prompt_by_label(client, name, "baseline")
    if baseline is None:
        baseline = client.create_prompt(
            name=name,
            prompt=DEFAULT_PROMPT_TEMPLATE,
            labels=["baseline", "production"],
            tags=["day13", "checkpoint-2"],
            commit_message="CP2 baseline prompt",
        )

    candidate = _get_prompt_by_label(client, name, "candidate")
    if candidate is None:
        candidate = client.create_prompt(
            name=name,
            prompt=CANDIDATE_PROMPT_TEMPLATE,
            labels=["candidate"],
            tags=["day13", "checkpoint-2"],
            commit_message="CP2 candidate prompt",
        )

    return baseline, candidate


def _run_trace(client, label: str) -> tuple[str, str]:
    os.environ["LANGFUSE_PROMPT_LABEL"] = label
    correlation_id = f"req-{uuid4().hex[:8]}"
    clear_contextvars()
    bind_contextvars(correlation_id=correlation_id)
    agent = LabAgent()

    with client.start_as_current_generation(
        name="LabAgent.run",
        metadata={"checkpoint": 2, "evidence": True},
    ):
        trace_id = client.get_current_trace_id()
        LabAgent.run.__wrapped__(
            agent,
            user_id="cp2-evidence-user",
            feature="qa",
            session_id="cp2-prompt-versioning",
            message=DEMO_MESSAGE,
        )

    if trace_id is None:
        raise RuntimeError("Langfuse did not create a trace ID")
    return trace_id, correlation_id


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    client = get_langfuse_client()
    name = os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat")
    original_label = os.getenv("LANGFUSE_PROMPT_LABEL", "production")

    baseline, candidate = _ensure_versions(client, name)
    baseline_trace, baseline_correlation = _run_trace(client, "baseline")
    candidate_trace, candidate_correlation = _run_trace(client, "candidate")

    client.update_prompt(
        name=name,
        version=candidate.version,
        new_labels=["candidate", "production"],
    )
    promoted = client.get_prompt(name, label="production", cache_ttl_seconds=0)

    client.update_prompt(
        name=name,
        version=baseline.version,
        new_labels=["baseline", "production"],
    )
    rolled_back = client.get_prompt(name, label="production", cache_ttl_seconds=0)
    client.flush()
    os.environ["LANGFUSE_PROMPT_LABEL"] = original_label

    print(f"prompt_name={name}")
    print(f"baseline_version={baseline.version}; labels=baseline,production")
    print(f"candidate_version={candidate.version}; labels=candidate")
    print(f"baseline_trace_id={baseline_trace}; correlation_id={baseline_correlation}")
    print(f"candidate_trace_id={candidate_trace}; correlation_id={candidate_correlation}")
    print(f"promotion_production_version={promoted.version}")
    print(f"rollback_production_version={rolled_back.version}")
    print("rollback_status=PASSED" if rolled_back.version == baseline.version else "rollback_status=FAILED")
    return 0 if rolled_back.version == baseline.version else 1


if __name__ == "__main__":
    raise SystemExit(main())
