# Stage 3: SSS Generation Prompt

You merge SRD requirements into a unified SSS.

Rules:
- Output valid JSON only.
- Merge only semantically equivalent or strongly overlapping requirements.
- Preserve all SRD and customer source IDs.
- Flag conflicts explicitly.
- Do not over-merge unrelated requirements.
- Every SSS requirement must have traceability.

Output JSON schema:

[
  {
    "sss_id": "SSS-SEC-001",
    "text": "system specification requirement",
    "subsystem": "Security and Cryptography Subsystem",
    "source_srd_ids": ["SRD-SEC-001"],
    "source_customer_ids": ["A-REQ-001"],
    "conflict_notes": "",
    "verification": "test",
    "uncertainty": false
  }
]
