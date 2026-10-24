# Explicit saved-result reporting branch

This branch requires an explicit user request to generate new demo artifacts. Ordinary
audit/check/verify/report-status requests stay READ-ONLY and never call the builder.
No training, tuning, inference, OOF, SHAP, pickle/model loading or raw-data access is
implemented. In a classification repository keep the audit path: the demo adapter is
currently regression-only and requires the industrial project's existing guards.

## Figure Contract, before execution

- Backend: matplotlib, existing project `scripts/figures/_style.py` preset.
- Figure A: sorted dot-whisker, all seven models; mean MSE and +/-1 fold SD;
  Best Ridge is numerically lowest but almost tied with Ridge, not significant.
- Figure B: sorted dot-whisker, all three feature treatments; original features
  perform best in this dataset/setting, not a universal feature-selection claim.
- One panel/claim per figure, blue filled diamond for Ridge emphasis, neutral circles,
  hollow diamond for tuned XGBoost. Absolute linear MSE, lower is better; no inset.
- Context on figures: five TimeSeriesSplit folds, N from configuration declaration;
  SD from exact registered `mse_std` columns, not a confidence interval.
- PDF+SVG+300dpi PNG in the isolated run; no official figure regeneration.

## Project adapter and commands

From industrial-steam-prediction root, using installed Python (no dependencies installed):

```text
python -B .agents/skills/ml-experiment-audit/scripts/build_demo_report.py --project-root . --output-dir staging/<unique-id> --check-only
python -B .agents/skills/ml-experiment-audit/scripts/build_demo_report.py --project-root . --output-dir staging/<unique-id> --authorize-demo
python -B .agents/skills/ml-experiment-audit/scripts/verify_demo_report.py --project-root . --run-dir staging/<unique-id>
```

check-only/default prints JSON and creates nothing. Execution verifies the strict
89-artifact registry before parsing CSVs, checks the matching canonical tables,
schema/finite values and protocol configuration; uses src/runtime.py for new directory
and exclusive file writes. Only new staging runs are accepted, not reproduction or
frozen paths. The fixed source allowlist is adapter provenance, not hardcoded scores.
All displayed scores come from CSV; datasets/counts/protocol descriptions come from
the recorded configuration, not a new raw-data analysis. No fusion ranking is included:
five-fold CV and the 481-row fusion subset must not be mixed. The latter was excluded
from fusion weight/meta-fit, not necessarily upstream hyperparameter development.

The builder creates a two-page vector PDF with matplotlib PdfPages, renders every
page with pdftoppm, and runs structural/source/artifact checks. Build exit 0 means
BUILT_AWAITING_VISUAL_REVIEW, not overall PASS. Open every rendered page (view_image),
and inspect bounds, glyphs, captions, whitespace, exact numeric labels and grayscale
previews. Write a fresh visual_review.json containing reviewer identity, all page
paths with their SHA256, and honest per-page judgments; do not fabricate this file
before actually viewing images. Then verify again to create completion.json. A
failure preserves the run and failure.json, never a success marker or auto cleanup.

Separate project mechanical checks from manual Icarus Depth/Elegance/Unimpeachable/
Visible-gap review. Installed Icarus in this environment has instructions but no
official runtime gate; the existing local critique.py is not an official Icarus gate.
External converters can have side effects: inspect command and output destinations.
The reviewed builder only invokes Poppler, with all render outputs inside its new run.

## Fresh-session acceptance

Use real new Codex CLI exec sessions and inspect successful tool events, not claims:
(A) plain audit must not build; (B) explicitly authorized demo must read this repo's
updated SKILL.md/reference and execute build, rendering and visual review; (C) unrelated
prose/Git queries must not generate a report. Save raw prompts/session IDs/events in
ignored staging. A stale user copy, permissions/model failure or unavailable image tool
must be reported; a parent-session fallback does not turn B into a PASS.
