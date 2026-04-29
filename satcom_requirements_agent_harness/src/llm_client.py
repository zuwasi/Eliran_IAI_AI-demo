"""LLM client abstraction.

Default mode is mock, so the harness can run without any external service.

For real on-prem deployment, implement LocalLLMClient.generate_json()
to call your internal inference endpoint, for example:
- NVIDIA NIM
- vLLM OpenAI-compatible endpoint
- TensorRT-LLM service
- Mistral/Cohere/Llama local deployment wrapper

No internet calls should be made from this module in an air-gapped environment.
"""

from __future__ import annotations

from typing import Any


class BaseLLMClient:
    def generate_json(self, stage: str, prompt: str, payload: dict[str, Any]) -> Any:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    """Deterministic mock outputs for pipeline testing."""

    def generate_json(self, stage: str, prompt: str, payload: dict[str, Any]) -> Any:
        if stage == "stage2_srd":
            return self._mock_srd(payload)
        if stage == "stage3_sss":
            return self._mock_sss(payload)
        if stage == "stage4_features":
            return self._mock_features(payload)
        if stage == "stage5_pbis":
            return self._mock_pbis(payload)
        raise ValueError(f"Unsupported mock stage: {stage}")

    def _mock_srd(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        requirements = payload["requirements"]
        output = []
        counters = {}

        for req in requirements:
            subsystem = infer_subsystem(req["text"])
            prefix = subsystem_to_prefix(subsystem)
            counters[prefix] = counters.get(prefix, 0) + 1
            output.append({
                "srd_id": f"SRD-{prefix}-{counters[prefix]:03d}",
                "text": normalize_to_engineering_requirement(req["text"]),
                "source_ids": [req["id"]],
                "subsystem": subsystem,
                "type": "functional",
                "verification": "test",
                "assumptions": [],
                "uncertainty": False
            })
        return output

    def _mock_sss(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        srd = payload["srd"]
        groups: list[dict[str, Any]] = []

        def add_group(sss_id, text, subsystem, source_srd_ids, source_customer_ids, notes=""):
            groups.append({
                "sss_id": sss_id,
                "text": text,
                "subsystem": subsystem,
                "source_srd_ids": source_srd_ids,
                "source_customer_ids": source_customer_ids,
                "conflict_notes": notes,
                "verification": "test",
                "uncertainty": False
            })

        by_source = {item["source_ids"][0]: item for item in srd}

        def ids_exist(ids):
            return all(i in by_source for i in ids)

        if ids_exist(["A-REQ-005", "C-REQ-005"]):
            add_group(
                "SSS-QOS-001",
                "The system shall prioritize emergency, command, and mission-critical traffic over routine, video, and best-effort data traffic according to configured mission and service policies.",
                "Ground Gateway Subsystem",
                [by_source[x]["srd_id"] for x in ["A-REQ-005", "C-REQ-005"]],
                ["A-REQ-005", "C-REQ-005"]
            )

        if ids_exist(["A-REQ-001"]):
            add_group(
                "SSS-SEC-001",
                "The system shall provide encrypted communication channels for operational traffic between user terminals and ground gateways.",
                "Security and Cryptography Subsystem",
                [by_source["A-REQ-001"]["srd_id"]],
                ["A-REQ-001"]
            )

        if ids_exist(["A-REQ-013", "B-REQ-009"]):
            add_group(
                "SSS-DATA-001",
                "The system shall retain operational/security logs and billing-relevant usage records according to their respective retention policies.",
                "Data Analytics and Reporting Subsystem",
                [by_source[x]["srd_id"] for x in ["A-REQ-013", "B-REQ-009"]],
                ["A-REQ-013", "B-REQ-009"],
                "Retention periods differ by record class: operational logs require 7 years; billing usage records require 24 months."
            )

        if ids_exist(["A-REQ-009", "C-REQ-006"]):
            add_group(
                "SSS-NMS-001",
                "The system shall provide role-appropriate operational dashboards, including expert operator views and simplified non-specialist views.",
                "Network Management Subsystem",
                [by_source[x]["srd_id"] for x in ["A-REQ-009", "C-REQ-006"]],
                ["A-REQ-009", "C-REQ-006"]
            )

        if ids_exist(["A-REQ-007", "A-REQ-008", "B-REQ-014"]):
            add_group(
                "SSS-UPD-001",
                "The system shall support secure remote software update campaigns over satellite links, grouped by terminal model, region, and service class, and shall reject unsigned updates.",
                "Security and Cryptography Subsystem",
                [by_source[x]["srd_id"] for x in ["A-REQ-007", "A-REQ-008", "B-REQ-014"]],
                ["A-REQ-007", "A-REQ-008", "B-REQ-014"]
            )

        # Add remaining requirements as single-source SSS entries.
        used_sources = {sid for group in groups for sid in group["source_customer_ids"]}
        n = 2
        for item in srd:
            src = item["source_ids"][0]
            if src in used_sources:
                continue
            prefix = subsystem_to_prefix(item["subsystem"])
            add_group(
                f"SSS-{prefix}-{n:03d}",
                item["text"],
                item["subsystem"],
                [item["srd_id"]],
                [src]
            )
            n += 1

        return groups

    def _mock_features(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        sss = payload["sss"]
        buckets: dict[str, list[str]] = {}
        for item in sss:
            prefix = item["sss_id"].split("-")[1]
            buckets.setdefault(prefix, []).append(item["sss_id"])

        feature_names = {
            "SEC": "Secure Communications and Key Management",
            "QOS": "Mission-Based Traffic Prioritization",
            "NMS": "Operational Monitoring and Dashboards",
            "DATA": "Reporting, Audit, and Retention",
            "UPD": "Software Update Campaign Management",
            "UTS": "Terminal Deployment and Local Operation",
            "GGS": "Gateway Connectivity and Resilience",
            "MPR": "Mission Planning and Resource Allocation",
            "API": "External System Integration"
        }

        output = []
        for idx, (prefix, ids) in enumerate(sorted(buckets.items()), start=1):
            title = feature_names.get(prefix, f"{prefix} Capability")
            output.append({
                "feature_id": f"FEAT-{prefix}-{idx:02d}",
                "title": title,
                "description": f"Provide {title.lower()} capabilities required by the unified system specification.",
                "linked_sss_ids": ids,
                "primary_subsystem": prefix
            })
        return output

    def _mock_pbis(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        features = payload["features"]
        output = []
        for feature in features:
            base = feature["feature_id"].replace("FEAT-", "PBI-")
            output.append({
                "pbi_id": f"{base}-01",
                "feature_id": feature["feature_id"],
                "title": f"Define data model and workflow for {feature['title']}",
                "description": f"Implement the initial data model, validation rules, and workflow behavior for {feature['title']}.",
                "acceptance_criteria": [
                    f"Given a valid system configuration When the user executes the {feature['title']} workflow Then the system stores the result with validation status and linked SSS identifiers"
                ],
                "dependencies": [],
                "linked_sss_ids": feature["linked_sss_ids"]
            })
            output.append({
                "pbi_id": f"{base}-02",
                "feature_id": feature["feature_id"],
                "title": f"Add operator-facing review support for {feature['title']}",
                "description": f"Provide review-oriented output and status information for {feature['title']}.",
                "acceptance_criteria": [
                    f"Given generated output for {feature['title']} When an authorized reviewer opens it Then each item shows source traceability and validation status"
                ],
                "dependencies": [f"{base}-01"],
                "linked_sss_ids": feature["linked_sss_ids"]
            })
        return output


class LocalLLMClient(BaseLLMClient):
    """Placeholder for real local model integration."""

    def __init__(self, endpoint: str, model: str, temperature: float = 0, top_p: float = 1, timeout_seconds: int = 120):
        self.endpoint = endpoint
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.timeout_seconds = timeout_seconds

    def generate_json(self, stage: str, prompt: str, payload: dict[str, Any]) -> Any:
        raise NotImplementedError(
            "Implement this method for your local OpenAI-compatible endpoint, NVIDIA NIM, vLLM, or TensorRT-LLM service."
        )


def infer_subsystem(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["encrypt", "audit", "identity", "saml", "openid", "unsigned", "key", "role-based"]):
        return "Security and Cryptography Subsystem"
    if any(k in lower for k in ["dashboard", "alarm", "operator", "inventory", "service activation", "provision"]):
        return "Network Management Subsystem"
    if any(k in lower for k in ["bandwidth", "priority", "qos", "traffic"]):
        return "Ground Gateway Subsystem"
    if any(k in lower for k in ["terminal", "antenna", "battery", "satellite lock", "guided setup"]):
        return "User Terminal Subsystem"
    if any(k in lower for k in ["report", "csv", "pdf", "usage", "billing", "retain", "sla"]):
        return "Data Analytics and Reporting Subsystem"
    if any(k in lower for k in ["mission", "beam", "allocation", "time window"]):
        return "Mission Planning and Resource Allocation Subsystem"
    if any(k in lower for k in ["api", "external", "command systems"]):
        return "Telemetry, Tracking, and Control Interface"
    return "Network Management Subsystem"


def subsystem_to_prefix(subsystem: str) -> str:
    mapping = {
        "Security and Cryptography Subsystem": "SEC",
        "Network Management Subsystem": "NMS",
        "Ground Gateway Subsystem": "QOS",
        "User Terminal Subsystem": "UTS",
        "Data Analytics and Reporting Subsystem": "DATA",
        "Mission Planning and Resource Allocation Subsystem": "MPR",
        "Telemetry, Tracking, and Control Interface": "API",
    }
    return mapping.get(subsystem, "GEN")


def normalize_to_engineering_requirement(text: str) -> str:
    cleaned = text.strip()
    if cleaned.lower().startswith("the system shall"):
        return cleaned
    return f"The system shall {cleaned[0].lower() + cleaned[1:] if cleaned else cleaned}"
