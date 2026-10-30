# AI Security Labs

A collection of self-contained labs for practicing AI security defense against LLM vulnerabilities.

## Projects

### [nuguard-medical/](./nuguard-medical)
Mock hospital LLM red-teaming lab. Demonstrates that prompt-only defenses fail and database-layer enforcement is necessary.

**Key learning:** All seven OWASP LLM Top 10 vulnerabilities (V1–V7) seeded, attacked, and blocked with code-level access control.

- `hospital_core.py` — app logic, defenses, chat loop
- `medical_redteam_lab.ipynb` — builds synthetic hospital database
- `medical_redteam_attacks.ipynb` — attack harness with multi-run scoring
- `README.md` — quick start and architecture

### nuguard/
NuGuard practice lab (original Practical DevSecOps course recreation).

## Getting Started

Each project has its own README with setup instructions. Start with `nuguard-medical/` for the hospital red-teaming lab.

---

More labs coming soon.
