"""Pipeline orchestration."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from llm_client import BaseLLMClient
from utils import extract_requirement_blocks, read_text_files, write_json
from validators import validate_all
from scoring import score_run


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_pipeline(config: dict[str, Any], llm: BaseLLMClient) -> dict[str, Any]:
    started = time.time()
    root = Path.cwd()
    output_dir = root / config["output_dir"]
    prompt_dir = root / "prompts"

    customer_dir = root / config["input_customer_requirements_dir"]
    context_dir = root / config["input_context_dir"]

    customer_docs = read_text_files(customer_dir)
    context_docs = read_text_files(context_dir)
    context_text = "\n\n".join(context_docs.values())

    run_log = {
        "project": config["project_name"],
        "stages": [],
        "mode": config["mode"]
    }

    # Stage 1 is deterministic extraction for this demo harness.
    t0 = time.time()
    ingested = []
    for doc_name, text in customer_docs.items():
        ingested.extend(extract_requirement_blocks(doc_name, text))
    write_json(output_dir / "stage1_ingested_requirements.json", ingested)
    run_log["stages"].append({"stage": "stage1_ingestion", "count": len(ingested), "seconds": round(time.time() - t0, 3)})

    # Stage 2
    t0 = time.time()
    srd = llm.generate_json(
        "stage2_srd",
        load_prompt(prompt_dir / "stage2_srd.md"),
        {"requirements": ingested, "context": context_text}
    )
    write_json(output_dir / "stage2_srd.json", srd)
    run_log["stages"].append({"stage": "stage2_srd", "count": len(srd), "seconds": round(time.time() - t0, 3)})

    # Stage 3
    t0 = time.time()
    sss = llm.generate_json(
        "stage3_sss",
        load_prompt(prompt_dir / "stage3_sss.md"),
        {"srd": srd, "context": context_text}
    )
    write_json(output_dir / "stage3_sss.json", sss)
    run_log["stages"].append({"stage": "stage3_sss", "count": len(sss), "seconds": round(time.time() - t0, 3)})

    # Stage 4
    t0 = time.time()
    features = llm.generate_json(
        "stage4_features",
        load_prompt(prompt_dir / "stage4_features.md"),
        {"sss": sss, "context": context_text}
    )
    write_json(output_dir / "stage4_features.json", features)
    run_log["stages"].append({"stage": "stage4_features", "count": len(features), "seconds": round(time.time() - t0, 3)})

    # Stage 5
    t0 = time.time()
    pbis = llm.generate_json(
        "stage5_pbis",
        load_prompt(prompt_dir / "stage5_pbis.md"),
        {"features": features, "sss": sss, "context": context_text}
    )
    write_json(output_dir / "stage5_pbis.json", pbis)
    run_log["stages"].append({"stage": "stage5_pbis", "count": len(pbis), "seconds": round(time.time() - t0, 3)})

    validation_report = validate_all(ingested, srd, sss, features, pbis)
    score_report = score_run(validation_report, sss, features, pbis)

    run_log["total_seconds"] = round(time.time() - started, 3)
    run_log["validation_passed"] = validation_report["passed"]
    run_log["final_score"] = score_report["final_score"]

    write_json(output_dir / "validation_report.json", validation_report)
    write_json(output_dir / "score_report.json", score_report)
    write_json(output_dir / "run_log.json", run_log)

    return {
        "validation_report": validation_report,
        "score_report": score_report,
        "run_log": run_log
    }
