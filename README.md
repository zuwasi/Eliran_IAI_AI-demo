# SATCOM Requirements Transformation Agent — Demo

A working demo of an air-gapped, deterministic 5-stage pipeline that turns raw customer requirements into engineered specifications, features, and dev-ready backlog items — with full traceability and conflict detection.

> **Project AURORA-SATCOM** • Prepared by **Engineering Software Lab** ([eswlab.com](https://eswlab.com/contact-us/))

---

## 🌐 Live presentations (no install needed)

View the customer-facing decks directly in your browser:

- **Landing page:** https://zuwasi.github.io/Eliran_IAI_AI-demo/
- **How to run the demo (15-slide guide):** https://zuwasi.github.io/Eliran_IAI_AI-demo/how_to_run_the_demo.html
- **Technical overview (17-slide deck):** https://zuwasi.github.io/Eliran_IAI_AI-demo/satcom_requirements_presentation.html
- **Workflow diagram (draw.io):** [satcom_requirements_workflow.drawio](satcom_requirements_workflow.drawio) — open in [app.diagrams.net](https://app.diagrams.net/) or any draw.io / diagrams.net client

---

## What you get

```
.
├── README.md                                ← you are here
├── STEP_BY_STEP_GUIDE.md                    ← detailed written walkthrough
├── how_to_run_the_demo.html                 ← 15-slide HOW-TO deck (start here)
├── satcom_requirements_presentation.html    ← 17-slide TECHNICAL OVERVIEW deck
├── install.bat   / install.ps1   / install.sh         ← one-click installer
├── run_demo.bat  / run_demo.sh                        ← re-run the pipeline
├── open_presentation.bat / open_presentation.sh       ← open both decks in browser
├── esl_logo.png
└── satcom_requirements_agent_harness/       ← runnable Python project
    ├── config.json
    ├── requirements.txt
    ├── input/                               ← sample customer requirements + system context
    ├── prompts/                             ← per-stage prompt templates
    ├── src/                                 ← pipeline, validators, scoring
    └── tests/
```

---

## Watch the overview first

Two HTML decks (open in any modern browser — Chrome, Edge, Firefox, Safari). Navigate with **arrow keys**, **spacebar**, **swipe**, or the **‹ ›** buttons.

- **`how_to_run_the_demo.html`** — start here. A 15-slide hands-on guide with the exact commands for Windows / macOS / Linux, expected output, troubleshooting tips, and a TL;DR.
- **`satcom_requirements_presentation.html`** — a 17-slide technical overview of the architecture, the 5 pipeline stages, validation, scoring, and a 4-minute live-demo script.

---

## One-click install (recommended)

### Windows
Double-click **`install.bat`** in the project folder.
After it finishes, double-click **`run_demo.bat`** to re-run the pipeline any time.

### Linux / macOS
```bash
chmod +x install.sh run_demo.sh open_presentation.sh
./install.sh
./run_demo.sh
```

The installer:
1. Verifies Python 3.10+ is on your PATH.
2. Creates a clean virtual environment under `satcom_requirements_agent_harness/.venv/`.
3. Installs the only dependency (`jsonschema`).
4. Runs a smoke test to confirm the pipeline produces a passing score.

No admin rights, no registry changes, no system files modified — everything lives in this folder.

---

## Manual run (if you'd rather not use the installer)

### Windows
```powershell
cd satcom_requirements_agent_harness
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py --config config.json
```

### Linux / macOS
```bash
cd satcom_requirements_agent_harness
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py --config config.json
```

The runner prints `score_report.json` to the terminal and writes 8 JSON artifacts to `satcom_requirements_agent_harness/outputs/`.

**Expected result:** final score **100 / 100, passed**, 0 errors, 0 warnings, 1 conflict surfaced.

---

## What the pipeline does

| Stage | Output | Purpose |
|---|---|---|
| 1 — Ingestion | `stage1_ingested_requirements.json` | Deterministic regex extraction of raw customer requirements |
| 2 — SRD | `stage2_srd.json` | Engineering "shall" requirements with subsystem assignment |
| 3 — SSS | `stage3_sss.json` | Unified system spec — merge, dedup, **conflict detection** |
| 4 — Features | `stage4_features.json` | Capability groupings for product planning |
| 5 — PBIs | `stage5_pbis.json` | Backlog items with **Given / When / Then** acceptance criteria |
| Validate | `validation_report.json` | Schema + traceability cross-checks |
| Score | `score_report.json` | Weighted benchmark across 6 categories |

For the full step-by-step walkthrough with explanations, see **[STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md)**.

---

## Key design principles

- **Air-gapped** — no internet, no external SaaS APIs.
- **Deterministic** — mock mode produces byte-identical output every run; CI can diff against a golden reference.
- **Approved-model policy** — `config.json` declares disallowed origins/families for the production LLM swap-in.
- **Strict validation** — every artifact is JSON-schema validated; every requirement traces back to a customer ID; every PBI acceptance criterion contains Given/When/Then.

---

## Going to production (later)

Swap mock mode for a real on-prem LLM (NVIDIA NIM, vLLM, TensorRT-LLM, Llama / Mistral local wrapper):

1. In `satcom_requirements_agent_harness/config.json`, set `"mode": "local"`.
2. Implement `LocalLLMClient.generate_json()` in `src/llm_client.py` — POST prompt + payload to your on-prem endpoint, parse JSON, return.
3. Re-run the same command. The runner picks up the new client automatically. Schemas, validators, scoring stay untouched.

---

## Support

For deployment guidance, customizations, or production integration with **Polarion** / **Azure DevOps**, contact us at **[eswlab.com/contact-us](https://eswlab.com/contact-us/)**.
