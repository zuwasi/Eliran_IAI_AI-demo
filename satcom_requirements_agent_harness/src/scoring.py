"""Benchmark scoring model."""

from __future__ import annotations

from typing import Any


WEIGHTS = {
    "traceability_accuracy": 0.25,
    "deduplication_quality": 0.20,
    "conflict_detection": 0.15,
    "feature_quality": 0.15,
    "pbi_quality": 0.15,
    "json_validity": 0.10,
}


def score_run(validation_report: dict[str, Any], sss: list[dict[str, Any]], features: list[dict[str, Any]], pbis: list[dict[str, Any]]) -> dict[str, Any]:
    errors = validation_report.get("errors", [])
    warnings = validation_report.get("warnings", [])

    json_validity = 100 if not errors else max(0, 100 - 20 * len(errors))

    traceability_errors = [e for e in errors if "traceability" in e.lower() or "unknown" in e.lower()]
    traceability_accuracy = max(0, 100 - 25 * len(traceability_errors))

    duplicate_warnings = [w for w in warnings if "duplicate" in w.lower()]
    deduplication_quality = max(0, 100 - 20 * len(duplicate_warnings))

    conflict_detection = 100
    if any("retain" in item.get("text", "").lower() or "retention" in item.get("text", "").lower() for item in sss):
        if not any(item.get("conflict_notes") for item in sss):
            conflict_detection = 60

    feature_quality = 100 if features else 0
    if any(not f.get("linked_sss_ids") for f in features):
        feature_quality -= 30

    pbi_quality = 100 if pbis else 0
    weak_pbi_terms = ["implement complete", "implement subsystem", "do everything"]
    for pbi in pbis:
        joined = (pbi.get("title", "") + " " + pbi.get("description", "")).lower()
        if any(term in joined for term in weak_pbi_terms):
            pbi_quality -= 20
        if not pbi.get("acceptance_criteria"):
            pbi_quality -= 20
    pbi_quality = max(0, pbi_quality)

    category_scores = {
        "traceability_accuracy": traceability_accuracy,
        "deduplication_quality": deduplication_quality,
        "conflict_detection": conflict_detection,
        "feature_quality": feature_quality,
        "pbi_quality": pbi_quality,
        "json_validity": json_validity,
    }

    final_score = sum(category_scores[k] * WEIGHTS[k] for k in WEIGHTS)

    return {
        "weights": WEIGHTS,
        "category_scores": category_scores,
        "final_score": round(final_score, 2),
        "passed": validation_report.get("passed", False) and final_score >= 80
    }
