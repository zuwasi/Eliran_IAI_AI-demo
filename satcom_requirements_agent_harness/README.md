# SATCOM Requirements Agent Harness

This is a ready-to-run Python project skeleton for simulating an on-prem, air-gapped LLM workflow for systems engineering requirements.

Domain: complex satellite communication system.

The workflow supports:

1. Customer requirements to SRD
2. Multiple SRDs to unified SSS with traceability
3. SSS to product features
4. Features to PBIs with acceptance criteria
5. Validation and benchmark scoring

The project is designed for use with Ampcode or another coding agent. The agent should implement the LLM adapter in `src/llm_client.py` for the target local inference server.

## Key Constraints

- On-prem only
- Air-gapped compatible
- No external internet calls
- No Chinese-origin model requirement assumed
- Deterministic structured outputs
- Full traceability required
- Human review expected before Polarion or Azure DevOps ingestion

## Recommended Local Models

Use only models approved by the customer, for example:

- Mistral
- Cohere
- Meta Llama
- NVIDIA Nemotron

Do not use Qwen, DeepSeek, Baichuan, Yi, GLM/Zhipu, Moonshot/Kimi, Alibaba, Tencent, or Baidu models.

## Project Structure

```text
satcom_requirements_agent_harness/
  input/
    customer_requirements/
    context/
  outputs/
  prompts/
  src/
    main.py
    llm_client.py
    schemas.py
    validators.py
    scoring.py
    pipeline.py
    utils.py
  tests/
  config.json
  README.md
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate        # Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
python src/main.py --config config.json
```

The harness includes a mock LLM mode by default. This lets the workflow execute without a real model.

To connect a local model, edit:

```text
src/llm_client.py
```

and implement:

```python
LocalLLMClient.generate_json(...)
```

## Expected Outputs

The workflow writes:

```text
outputs/
  stage1_ingested_requirements.json
  stage2_srd.json
  stage3_sss.json
  stage4_features.json
  stage5_pbis.json
  validation_report.json
  score_report.json
  run_log.json
```

## Integration Targets

Polarion:
- Import SRD and SSS JSON as requirements/work items.
- Preserve upstream/downstream traceability links.

Azure DevOps:
- Import Features and PBIs.
- Store linked SSS IDs in custom fields or links.

## Important Design Principle

Do not rely on the LLM alone for traceability.

The LLM proposes normalized requirements and merge candidates. The system must validate:

- source IDs exist
- no hallucinated IDs
- every SSS requirement has source traceability
- PBIs link back to SSS requirements
- JSON schema is valid

## Demo Dataset

Place customer documents under:

```text
input/customer_requirements/
```

Place subsystem context under:

```text
input/context/
```

You can use the synthetic AURORA-SATCOM dataset previously generated for this purpose.
