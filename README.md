# AI Agent Eval & Red-Team Harness

A small, dependency-free harness for measuring agent safety and answer quality.
It ships with adversarial prompt probes and a dry-run mode that works offline.

## What it checks
- Prompt-injection attempts (override, system-role hijack, jailbreak, data-exfiltration prompts)
- Citation/grounding presence in answers (basic checks)
- Cost and latency per task (reported when run against a live endpoint)

## Usage
    # Offline demo (no keys, no network): generates a sample report
    python run_probes.py --dry-run

    # Against any OpenAI-compatible endpoint
    export OPENAI_BASE_URL=http://localhost:4000/v1   # e.g. LiteLLM gateway
    export OPENAI_API_KEY=sk-...
    python run_probes.py --model gpt-5-mini

Output: report.json (per-probe status, latency, notes).

## Files
- run_probes.py - runner (stdlib only)
- data/probes.json - adversarial probe set (extend freely)
- docs/METHODOLOGY.md - how probes are scored

## Honest status
This is a working scaffold with an offline demo path. Live results depend on the endpoint you point it at. It does not claim to be a full compliance suite.
