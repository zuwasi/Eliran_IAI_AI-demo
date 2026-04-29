"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llm_client import MockLLMClient, LocalLLMClient
from pipeline import run_pipeline


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="SATCOM Requirements Agent Harness")
    parser.add_argument("--config", default="config.json", help="Path to config JSON")
    args = parser.parse_args()

    config = load_config(Path(args.config))

    if config.get("mode") == "mock":
        llm = MockLLMClient()
    else:
        llm_cfg = config["llm"]
        llm = LocalLLMClient(
            endpoint=llm_cfg["endpoint"],
            model=llm_cfg["model"],
            temperature=llm_cfg.get("temperature", 0),
            top_p=llm_cfg.get("top_p", 1),
            timeout_seconds=llm_cfg.get("timeout_seconds", 120),
        )

    result = run_pipeline(config, llm)
    print(json.dumps(result["score_report"], indent=2))
    return 0 if result["score_report"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
