# Stage 5: PBI Generation Prompt

You decompose product features into PBIs.

Rules:
- Output valid JSON only.
- Each PBI must be scoped to approximately 2 to 3 weeks.
- Acceptance criteria must use Given/When/Then.
- Each PBI must link to source SSS IDs.
- Avoid vague PBIs such as "Implement the security subsystem".

Output JSON schema:

[
  {
    "pbi_id": "PBI-SEC-01-01",
    "feature_id": "FEAT-SEC-01",
    "title": "Implement audit log event schema",
    "description": "PBI description",
    "acceptance_criteria": [
      "Given an authenticated operator When the operator changes configuration Then the system records an audit event with user, time, object, action, and result"
    ],
    "dependencies": [],
    "linked_sss_ids": ["SSS-SEC-001"]
  }
]
