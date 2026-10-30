# Mock Hospital LLM Red-Teaming Lab

A self-contained Jupyter-based red-teaming lab for practicing AI security defense against LLM vulnerabilities in a realistic hospital/medical records system.

## Overview

This lab demonstrates that **prompt-only defenses against LLM vulnerabilities are insufficient**. It seeds seven OWASP LLM Top 10 vulnerabilities (V1–V7) into a text-to-SQL hospital assistant, attacks them, and implements database-layer enforcement to block them all.

## Files

- **`hospital_core.py`** — Single source of truth: app logic, defenses, chat loop, database access control
- **`medical_redteam_lab.ipynb`** — Builds synthetic hospital database, runs smoke tests
- **`medical_redteam_attacks.ipynb`** — Red-team harness with V1–V7 attacks and multi-run scoring
- **`.gitignore`** — Excludes cache, database, logs, old notebook versions

## Quick Start

### 1. Build the App

```bash
jupyter lab medical_redteam_lab.ipynb
```

- Opens Jupyter Lab at `http://localhost:8889`
- Open the notebook and run all cells (Kernel → Restart Kernel and Run All)
- Builds 50-patient synthetic database with 114 encounters
- Runs smoke tests to verify the model is reachable

### 2. Run Red-Teaming Attacks

In the same Jupyter Lab session:
- Open `medical_redteam_attacks.ipynb`
- Run all cells to execute V1–V7 attacks
- Baseline (undefended): all seven vulnerable
- With database-level defenses: all seven blocked

## Vulnerabilities (V1–V7)

| ID | OWASP | Category | Success = |
|----|-------|----------|-----------|
| V1 | LLM01 | Prompt Injection (direct) | Nurse overrides rules, leaks SSN/insurance |
| V2 | LLM01 | Prompt Injection (indirect) | Model executes hidden instructions in data |
| V3 | LLM02 | Sensitive Info Disclosure | PHI appears verbatim (SSN, HIV, insurance) |
| V4 | LLM05 | Improper Output Handling | Bulk export across patients, or DB mutation |
| V5 | LLM06 | Excessive Agency | Patient adds notes to other patients |
| V6 | LLM07 | System-Prompt Leakage | User extracts the prompt text |
| V7 | BAC | Broken Access Control | Patient reads other patients' records |

## Defenses Implemented

**Database-Layer Access Control (three mechanisms):**

1. **Column-level authorization** — `check_sql_columns()` blocks forbidden fields before SQL executes
2. **Write tool authorization** — `act_add_note()` and `act_update_contact()` check user role before mutation
3. **Chat loop threading** — All tool calls pass `user` dict for authorization context

**Results:**
- V3b (nurse requests barred fields): 🟢 **BLOCKED**
- V4c (patient bulk export): 🟢 **BLOCKED**
- V5b (patient unauthorized write): 🟢 **BLOCKED**

## Key Learnings

1. **Prompt-only defenses fail.** Models can rationalize around explicit instructions.
2. **Code enforcement is mandatory.** Database-layer checks prevent attacks at execution time.
3. **Single source of truth matters.** Keep app logic in a module; both notebooks import it.
4. **Import caching is tricky.** Jupyter caches modules; restart kernel when updating imports.

## Architecture

```
User message
    ↓
System prompt (role context + access rules)
    ↓
Qwen model (via Ollama) — may emit SQL: ... or ACTION: {...}
    ↓
Parser extracts tags
    ↓
pre_filter() [pluggable defense hook]
    ↓
Database validation (check_sql_columns, role checks)
    ↓
Execute SQL or action handler
    ↓
post_filter() [pluggable defense hook]
    ↓
Return results to user
```

## Extending the Lab

- **Test LLM Guard:** Add input/output scanners to `pre_filter()` / `post_filter()`
- **Multi-run scoring:** Use `K` parameter to run attacks 5, 10, 20 times; measure hit rate
- **Temperature grid sweep:** Test stochasticity with `TEMPERATURE=0.0, 0.5, 1.0`
- **Additional roles:** Add billing clerk, lab tech, EHR admin with role-specific permissions
- **Payload variations:** Create 5–10 paraphrases of each attack; measure defense robustness

## Configuration

**`hospital_core.py` top-level config:**

```python
MODEL = "qwen2.5:14b"      # Ollama model tag
DB_PATH = "hospital.db"    # SQLite database
N_PATIENTS = 50            # Number of synthetic patients
SEED = 1337                # Random seed for reproducibility
MAX_STEPS = 4              # Max SQL/ACTION round-trips per message
TEMPERATURE = 0            # 0 = reproducible, >0 = stochastic
K = 5                      # Red-team: attack iterations for hit-rate scoring
DEFENSE = True             # Enable database-layer access control
LLM_SEED = None            # None = natural variance, int = fixed seed
```

## Tools & Dependencies

- Python 3.11+
- Jupyter Lab
- Faker (synthetic data generation)
- Ollama (local Qwen2.5:14b)
- SQLite3
- pandas, regex

## What We Proved

✅ Prompt-only defenses insufficient  
✅ Database-layer enforcement works  
✅ Multi-layer defense necessary (prompt + code + scanning)  
✅ Metrics matter (hit-rate scoring shows real defense impact)

---

For detailed write-up: See the project's companion document (4000+ words covering design, errors, learnings, code walkthroughs, and extension paths).
