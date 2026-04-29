# SATCOM Requirements Agent Harness — Step-by-Step Guide

This guide walks you through running the harness end-to-end, what every step does, and how to read the outputs.

> **Project AURORA-SATCOM** · Prepared by **[Engineering Software Lab](https://eswlab.com/contact-us/)**

---

## What this harness is

A 5-stage pipeline that takes raw **customer requirements** (Markdown / text from defense, commercial, and emergency-response stakeholders) and transforms them into:

1. Structured customer requirements (ingested)
2. Engineering-style **SRD** (System Requirements Document)
3. Unified **SSS** (System / Subsystem Specification) — with conflict detection
4. **Features** (capability groupings)
5. **PBIs** (Product Backlog Items) with Given / When / Then acceptance criteria

It then **validates** everything (traceability, schemas) and **scores** the result.

The whole pipeline runs offline in `mock` mode (deterministic, no LLM calls) and is designed to swap in a local on-prem LLM (NVIDIA NIM / vLLM / TensorRT-LLM) for production — never an external internet API.

---

## Step 0 — Prerequisites

- **Python 3.10+** installed and on your PATH. Verify:
  ```powershell
  python --version
  ```
- A terminal: PowerShell on Windows, bash/zsh on Linux/macOS.
- About **5 MB** of free disk space.

No internet access is required to run the demo — only `pip install` (one-time) needs network access to fetch the single dependency. After that the pipeline is fully offline.

---

## Step 1 — Open the project

Open a terminal in the folder you cloned/extracted, and change into the harness directory:

```powershell
cd satcom_requirements_agent_harness
```

You should see:

```
config.json
requirements.txt
README.md
input/
prompts/
src/
tests/
```

---

## Step 2 — Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Why:** isolates this project's single Python dependency (`jsonschema`) from your global environment.

---

## Step 3 — Install dependencies

**Windows:**
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Linux / macOS:**
```bash
pip install -r requirements.txt
```

The only runtime dependency is **`jsonschema`** — used by `src/validators.py` to enforce strict per-stage JSON schemas.

**Why:** every stage output (SRD, SSS, Features, PBIs) is validated against a strict schema in `src/schemas.py` before scoring. The schemas are deliberately strict — required fields, array minimum lengths, type constraints.

---

## Step 4 — Inspect `config.json`

```json
{
  "project_name": "AURORA-SATCOM",
  "mode": "mock",
  "input_customer_requirements_dir": "input/customer_requirements",
  "input_context_dir": "input/context",
  "output_dir": "outputs",
  "llm": {
    "provider": "local",
    "endpoint": "http://localhost:8000/v1/chat/completions",
    "model": "approved-local-model",
    "temperature": 0,
    "top_p": 1,
    "timeout_seconds": 120
  },
  "approved_model_policy": {
    "disallowed_origins": ["China"],
    "disallowed_model_families": [
      "Qwen", "DeepSeek", "Baichuan", "Yi",
      "InternLM", "GLM", "Zhipu", "Moonshot", "Kimi"
    ]
  }
}
```

**What each field does:**

- `mode: mock` — picks `MockLLMClient` (deterministic outputs). Switch to `local` to call a real on-prem endpoint.
- `input_customer_requirements_dir` — where customer `.md` files live (Customer A defense / B commercial / C emergency response).
- `input_context_dir` — system context (subsystem catalog) included in every LLM prompt.
- `output_dir` — where all stage results land.
- `llm.endpoint / model / temperature` — config for the eventual `LocalLLMClient`.
- `approved_model_policy` — guardrail blocking models from disallowed origins/families. Production deployments must enforce this list.

---

## Step 5 — Run the pipeline

**Windows:**
```powershell
.\.venv\Scripts\python.exe src\main.py --config config.json
```

**Linux / macOS:**
```bash
python src/main.py --config config.json
```

The runner is `src/main.py`. Internally it:

1. Loads `config.json`.
2. Picks `MockLLMClient` (mode=`mock`) or `LocalLLMClient` (real LLM).
3. Calls `run_pipeline(config, llm)` in `src/pipeline.py`.
4. Prints `score_report.json` to stdout.
5. Exits `0` if score passed, else `1`.

You'll see the final score block printed in the terminal.

---

## Step 6 — Understand each stage

### Stage 1 — Ingestion (deterministic, no LLM)

- **Input:** every `.md` file in `input/customer_requirements/`.
- **Logic:** `utils.extract_requirement_blocks()` runs a regex `^([A-Z]-REQ-\d{3})` to peel out individual requirements.
- **Output:** `outputs/stage1_ingested_requirements.json` — list of `{id, text, source_document, keywords, domain}`.
- **Why deterministic:** ingestion must be reproducible — no LLM creativity allowed for source-of-truth extraction.

### Stage 2 — SRD generation (LLM)

- **Prompt:** `prompts/stage2_srd.md` + ingested requirements + system context.
- **Logic:** every customer requirement becomes one **SRD entry** with: subsystem assignment, normalized "shall" wording, verification method, traceability back to its customer ID via `source_ids`.
- **Output:** `outputs/stage2_srd.json`.
- **Why:** SRDs are engineering-grade — each one ties back to exactly one customer requirement.

### Stage 3 — SSS generation (LLM, the most important stage)

- **Prompt:** `prompts/stage3_sss.md` + SRDs + context.
- **Logic:** consolidates **multiple** related SRDs into unified system/subsystem requirements (deduplication & merge), and **detects conflicts** between customers.
- **Conflict example:** A-REQ-013 says "retain operational logs ≥7 years" while B-REQ-009 says "retain billing usage records ≥24 months" → SSS-DATA-001 captures both via `conflict_notes`.
- **Output:** `outputs/stage3_sss.json` — each item has `source_srd_ids` AND `source_customer_ids` (mandatory full traceability).

### Stage 4 — Features (LLM)

- **Prompt:** `prompts/stage4_features.md` + SSS.
- **Logic:** groups SSS items into PM-level **features** by subsystem prefix (e.g. all `SSS-SEC-*` → "Secure Communications and Key Management").
- **Output:** `outputs/stage4_features.json`.
- **Why:** features are the unit a product manager / scrum master plans against.

### Stage 5 — PBIs (LLM)

- **Prompt:** `prompts/stage5_pbis.md` + features + SSS.
- **Logic:** explodes each feature into 2 backlog items with **Given / When / Then** acceptance criteria, dependencies, and links back to SSS.
- **Output:** `outputs/stage5_pbis.json` — dev-ready user stories.

### Validation

- File: `src/validators.py`.
- Checks: JSON-schema conformance, every traceability link resolves, every SSS has both `source_srd_ids` and `source_customer_ids`, every PBI AC contains "Given"/"When"/"Then", duplicate-text warnings.
- **Output:** `outputs/validation_report.json` (errors must be empty to pass).

### Scoring

- File: `src/scoring.py`.
- Weighted categories:
  - Traceability accuracy (25%)
  - Deduplication quality (20%)
  - Conflict detection (15%)
  - Feature quality (15%)
  - PBI quality (15%)
  - JSON validity (10%)
- Pass condition: `validation passed` AND `final_score ≥ 80`.
- **Output:** `outputs/score_report.json`.

---

## Step 7 — Verify outputs

The following files must exist under `outputs/`:

```
stage1_ingested_requirements.json
stage2_srd.json
stage3_sss.json
stage4_features.json
stage5_pbis.json
validation_report.json
score_report.json
run_log.json
```

Then check:

- `validation_report.json` → `"passed": true`, `errors: []`
- Every SSS item has non-empty `source_srd_ids` AND `source_customer_ids`
- Every PBI acceptance criterion contains the words **Given**, **When**, **Then**
- `score_report.json` → `final_score ≥ 80` and `"passed": true`

---

## Step 8 — Expected results

```
ingested:  14
srd:       14
sss:        9
features:   6
pbis:      12

errors:    0
warnings:  0
final_score: 100.0  (passed: true)

Detected conflict:
  SSS-DATA-001 — "operational logs require 7 years;
                  billing usage records require 24 months"
```

---

## Step 9 — Try modifications

Want to see how the pipeline reacts to changes? Try:

1. **Edit a customer requirement** in `input/customer_requirements/01_Customer_A_Defense_Requirements.md` — add or change a requirement, re-run, watch traceability propagate.
2. **Add a fourth customer file** (e.g. `04_Customer_D_Maritime_Requirements.md`) using the same `D-REQ-001` format — re-run, watch new SRDs and SSS items appear.
3. **Introduce a conflict** between two customers (e.g. different SLA or retention numbers) — watch `conflict_notes` get populated in `stage3_sss.json`.
4. **Break traceability** intentionally — e.g. modify the regex in `src/utils.py` to drop a requirement — watch the validator catch the dangling reference and the score drop.

---

## Step 10 — Going to production

When ready to use a real local LLM:

1. Set `"mode": "local"` in `config.json`.
2. Implement `LocalLLMClient.generate_json()` in `src/llm_client.py` (POST to your on-prem endpoint, parse JSON, return).
3. Keep all schemas, validators, scoring, and traceability logic untouched.
4. Re-run the same command — the runner picks up the new client automatically.

**Strict constraints honored:** no internet, no external APIs, no removal of validation, no schema simplification, no pipeline replacement.

---

## Need help?

For deployment guidance, customizations, or production integration with **Polarion** / **Azure DevOps**, contact **[Engineering Software Lab](https://eswlab.com/contact-us/)**.
