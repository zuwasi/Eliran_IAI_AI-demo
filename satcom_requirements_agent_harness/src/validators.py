"""Validation logic for generated artifacts."""

from __future__ import annotations

from typing import Any
from jsonschema import validate, ValidationError

from schemas import INGESTED_REQUIREMENT_SCHEMA, SRD_SCHEMA, SSS_SCHEMA, FEATURE_SCHEMA, PBI_SCHEMA


def validate_list_schema(items: list[dict[str, Any]], schema: dict[str, Any], name: str) -> list[str]:
    errors = []
    for i, item in enumerate(items):
        try:
            validate(item, schema)
        except ValidationError as exc:
            errors.append(f"{name}[{i}] schema error: {exc.message}")
    return errors


def validate_all(ingested, srd, sss, features, pbis) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    errors += validate_list_schema(ingested, INGESTED_REQUIREMENT_SCHEMA, "ingested")
    errors += validate_list_schema(srd, SRD_SCHEMA, "srd")
    errors += validate_list_schema(sss, SSS_SCHEMA, "sss")
    errors += validate_list_schema(features, FEATURE_SCHEMA, "features")
    errors += validate_list_schema(pbis, PBI_SCHEMA, "pbis")

    customer_ids = {x["id"] for x in ingested}
    srd_ids = {x["srd_id"] for x in srd}
    sss_ids = {x["sss_id"] for x in sss}
    feature_ids = {x["feature_id"] for x in features}

    for item in srd:
        for src in item.get("source_ids", []):
            if src not in customer_ids:
                errors.append(f"SRD {item.get('srd_id')} references unknown customer ID {src}")

    for item in sss:
        if not item.get("source_srd_ids"):
            errors.append(f"SSS {item.get('sss_id')} has no SRD traceability")
        if not item.get("source_customer_ids"):
            errors.append(f"SSS {item.get('sss_id')} has no customer traceability")
        for src in item.get("source_srd_ids", []):
            if src not in srd_ids:
                errors.append(f"SSS {item.get('sss_id')} references unknown SRD ID {src}")
        for src in item.get("source_customer_ids", []):
            if src not in customer_ids:
                errors.append(f"SSS {item.get('sss_id')} references unknown customer ID {src}")

    for feature in features:
        for sss_id in feature.get("linked_sss_ids", []):
            if sss_id not in sss_ids:
                errors.append(f"Feature {feature.get('feature_id')} references unknown SSS ID {sss_id}")

    for pbi in pbis:
        if pbi.get("feature_id") not in feature_ids:
            errors.append(f"PBI {pbi.get('pbi_id')} references unknown feature ID {pbi.get('feature_id')}")
        for ac in pbi.get("acceptance_criteria", []):
            if not ("Given" in ac and "When" in ac and "Then" in ac):
                warnings.append(f"PBI {pbi.get('pbi_id')} has weak acceptance criterion: {ac}")
        for sss_id in pbi.get("linked_sss_ids", []):
            if sss_id not in sss_ids:
                errors.append(f"PBI {pbi.get('pbi_id')} references unknown SSS ID {sss_id}")

    duplicate_texts = {}
    for item in sss:
        key = " ".join(item.get("text", "").lower().split())
        duplicate_texts.setdefault(key, []).append(item.get("sss_id"))
    for text, ids in duplicate_texts.items():
        if len(ids) > 1:
            warnings.append(f"Potential duplicate SSS requirements: {ids}")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "ingested": len(ingested),
            "srd": len(srd),
            "sss": len(sss),
            "features": len(features),
            "pbis": len(pbis)
        }
    }
