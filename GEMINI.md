# GEMINI.md — globalst Research Pipeline Rules

## Purpose
Ship a reproducible, OA-first Spatio-Temporal Network Meta-Analysis (ST-NMA) of Cardiovascular Disease (CVD) as an **E156 micro-paper + GitHub repo + interactive HTML dashboard**.

## Session Workflow
Before you use any tool or make changes, briefly say what you're about to do, then do it. After each tool call, summarize what you found and what's next.

## Statistical Framework: ST-NMA
- **Methods:** Use Bayesian hierarchical models (e.g., via `Stan` or `rjags`) to synthesize direct (RCT) and indirect (observational) evidence.
- **Data Integration:** ClinicalTrials.gov (RCTs), IHME (Burden), World Bank (Covariates), WHO (Regional data).
- **Spatio-Temporal:** Borrow strength across adjacent regions and years.

## Non-negotiables (from Global Rules)
1. **OA-only**: no paywalls.
2. **No secrets**: redact before logs.
3. **Memory ≠ evidence**: certified claims must cite evidence locators + hashes.
4. **Fail-closed**: if validation incomplete, REJECT + reasons.
5. **Determinism**: fixed seeds, stable sorting, pinned versions.

## TruthCert (proof-carrying numbers)
- Every number must come from certified claims or be labeled UNCERTIFIED.
- Evidence locator + hash + transformation steps + validator outcomes.

## E156 Workbook Protection
- `C:\E156\rewrite-workbook.txt`: Always keep `CURRENT BODY` up to date.
- **NEVER** modify or delete `YOUR REWRITE` sections.

## Quality Loop
- **Fix ALL issues in one pass.**
- **Test after EACH change.** Run full suite and report pass/fail count.
- **Search before declaring missing.**

## SHIP Ritual
When ready to **SHIP**:
1. Run full test suite.
2. Demo on fixtures.
3. Perform TruthCert validation.
4. Generate E156 micro-paper (156 words max).
5. Deploy HTML dashboard to GitHub Pages.
6. Update master `INDEX.md` and workbook.

## Platform Defaults
- Python-first pipelines; browser-first for interactive apps.
- `python` not `python3`.
- Offline-first tests + fixtures.
