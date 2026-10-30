# NuGuard Lab: Red-Teaming a Local AI Support Agent

A practice lab that points [NuGuard](https://github.com/NuGuardAI/nuguard), an open-source AI red-team and AI-SBOM scanner, at a small customer-support agent running Mistral 7B locally through Ollama. I ran five scans, changing the app or the judge model each time, to see which fixes held up and which results could be trusted.

> **This is a practice lab on a deliberately small app, not a benchmark.** One toy app, one 7B target, one scan per run, and local models as attacker and judge. The app hard-codes a customer (`CURRENT_CUSTOMER`) and sample orders. Do not reuse it as a production pattern.


## Results

| Run | What changed | Judge | Scenarios | Findings | Risk |
| --- | --- | --- | --- | --- | --- |
| 1 | Basic agent, no defenses | Mistral | 66 | 11 | 49.5 |
| 2 | Regex input filter, API docs off, HTML escaping | Mistral | 92 | 24 | 48.3 |
| 3 | Allow-list gate, ownership check, output cleaning, policy file | Mistral | 86 | 0 | 0.0 |
| 4 | Same app as run 3 | Qwen 2.5 14B | 86 | 0 | 0.0 |
| 5 | Gate switched off, cleaning and ownership kept | Qwen 2.5 14B | 87 | 16 | 42.0 |

What I took from it:

1. A scan with zero scenarios is not a pass. My first attempt ran 0 scenarios because NuGuard found no agent in the SBOM.
2. Controls in code held (allow-list gate, server-side ownership check, output cleaning). Prompt-only rules did not hold against a 7B model.
3. Read the evidence behind each finding. The judge is a model too, and it is sometimes wrong. By my reading, run 2 had about 13 real findings and 11 false positives, and run 5 had 6 real and 10 that caused no harm.
4. A gate that hides the model produces a clean scan. Runs 3 and 4 hit 0 findings partly because the gate likely refused many attacks before they reached the model.
5. Run 5 changed the app and the judge together, so it cannot isolate the judge. Run 6 (same app as run 5, Mistral as judge) would.

## Layout

```
app/app.py                 final app (run 5): FastAPI + OpenAI Agents SDK agent, one lookup_order tool
nuguard.yaml               final config (runs 4 and 5)
cognitive-policy.md        policy file NuGuard uses to add scenarios
app.sbom.json              AI-SBOM of the app (1 AGENT, 1 TOOL, 1 API endpoint)
reports/                   scan reports for runs 1 to 5, plus remediation plans
variants/                  run 3 app (allow-list gate on) and run 3 config
docs/nuguard-lab-guide.md  step-by-step guide to recreate the lab
```

`reports/redteam.md` is run 1. The others are `redteam-run2.md` to `redteam-run5.md`.

## Reproduce

The full steps are in [docs/nuguard-lab-guide.md](docs/nuguard-lab-guide.md). In short:

- Python 3.12 with two conda environments, because the dependencies conflict: `nuguard` (NuGuard and LiteLLM) and `acme-app` (the app and the OpenAI Agents SDK).
- Ollama with `mistral` and `qwen2.5:14b` pulled. Tested on a Mac mini M4 with 24 GB of RAM.
- Environment variables: `OLLAMA_API_BASE=http://localhost:11434` and `NUGUARD_REDTEAM_LLM_MODEL=ollama_chat/mistral`.
- Start the app on port 8000, then generate the SBOM and run the scan:

```bash
nuguard sbom generate --source ./app --output app.sbom.json
nuguard redteam --config nuguard.yaml --profile standard --scenarios non-destructive --format markdown --output reports/redteam-run5.md
```

The guide names some backup files from each run. This repo keeps only the final files, so those backups are in `variants/` or were removed.

## Known limits

- Tool-abuse coverage was 0%, because Mistral 7B writes tool calls as plain text instead of running them.
- The judge's `VERIFIED` labels come from the same weak model, so they are not independent proof.
- Summed scenario time is not wall-clock time, because scenarios run in parallel.
