"""JSON schemas for the SATCOM requirements pipeline."""

INGESTED_REQUIREMENT_SCHEMA = {
    "type": "object",
    "required": ["id", "text", "source_document", "keywords", "domain"],
    "properties": {
        "id": {"type": "string"},
        "text": {"type": "string"},
        "source_document": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "domain": {"type": "string"}
    },
    "additionalProperties": True
}

SRD_SCHEMA = {
    "type": "object",
    "required": ["srd_id", "text", "source_ids", "subsystem", "type", "verification", "assumptions", "uncertainty"],
    "properties": {
        "srd_id": {"type": "string"},
        "text": {"type": "string"},
        "source_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "subsystem": {"type": "string"},
        "type": {"type": "string"},
        "verification": {"type": "string"},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "uncertainty": {"type": "boolean"}
    },
    "additionalProperties": True
}

SSS_SCHEMA = {
    "type": "object",
    "required": ["sss_id", "text", "subsystem", "source_srd_ids", "source_customer_ids", "conflict_notes", "verification", "uncertainty"],
    "properties": {
        "sss_id": {"type": "string"},
        "text": {"type": "string"},
        "subsystem": {"type": "string"},
        "source_srd_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "source_customer_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "conflict_notes": {"type": "string"},
        "verification": {"type": "string"},
        "uncertainty": {"type": "boolean"}
    },
    "additionalProperties": True
}

FEATURE_SCHEMA = {
    "type": "object",
    "required": ["feature_id", "title", "description", "linked_sss_ids", "primary_subsystem"],
    "properties": {
        "feature_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "linked_sss_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "primary_subsystem": {"type": "string"}
    },
    "additionalProperties": True
}

PBI_SCHEMA = {
    "type": "object",
    "required": ["pbi_id", "feature_id", "title", "description", "acceptance_criteria", "dependencies", "linked_sss_ids"],
    "properties": {
        "pbi_id": {"type": "string"},
        "feature_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "dependencies": {"type": "array", "items": {"type": "string"}},
        "linked_sss_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1}
    },
    "additionalProperties": True
}
