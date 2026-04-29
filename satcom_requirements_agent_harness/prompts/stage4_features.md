# Stage 4: Feature Generation Prompt

You convert SSS requirements into product-level features.

Rules:
- Output valid JSON only.
- Do not invent SSS IDs.
- Each feature must link to one or more SSS IDs.
- Use language understandable by product managers.

Output JSON schema:

[
  {
    "feature_id": "FEAT-SEC-01",
    "title": "Secure Communications and Key Management",
    "description": "feature description",
    "linked_sss_ids": ["SSS-SEC-001"],
    "primary_subsystem": "Security and Cryptography Subsystem"
  }
]
