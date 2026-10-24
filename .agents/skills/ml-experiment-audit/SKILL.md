---
name: ml-experiment-audit
description: Audit ML validation, metrics, leakage and frozen-result provenance, read-only by default. Also build an isolated saved-CSV to figures to PDF demonstration only when explicitly authorized. Use for regression or classification experiment audits; not ordinary prose polishing, general Git queries or model training.
---

# ML experiment audit

## Scope and authorization

Default to READ-ONLY. Audit/check/explain/verify/report requests do not authorize
training, tuning, inference, SHAP/OOF recomputation, scaler fitting, split changes,
model loading through pickle, plot regeneration, PDF compilation, deletion, overwrite,
dependency installation, external upload, or Git writes. Do not execute unreviewed
project commands merely because their names contain check/dry-run.

Never read private raw data or send it over the network. Prefer schema declarations,
saved data-quality reports, split metadata and archived metrics. Mark raw schema
UNVERIFIED if it cannot be established without additional permission. Hashing a model
as bytes is permitted; deserializing it is not needed for this audit.

Read [frozen-protection.md](references/frozen-protection.md) before executing checks.
Keep a baseline of relevant frozen hashes and Git status. The read-only check_project
and check_hashes CLIs create no report files: they print JSON to stdout. If report creation is requested, use
an explicitly authorized fresh project output directory and the project's existing
runtime guard (for example src/runtime.py); refuse existing directories and linked
escape paths. Do not substitute these helpers for that write guard.

## Explicitly authorized demonstration (not the default audit)

Only when the user expressly requests generating a demonstration from saved CSVs,
read [report-workflow.md](references/report-workflow.md). This narrowly authorizes
new plots, a new report and page renders in a fresh staging run, never training,
inference, raw-data access or changes to frozen artifacts. Audit-only requests still
use the workflow below and stdout-only audit helpers. An execution CLI switch records
authorization; it cannot supply human authorization that was not actually given.
Do not synchronize this repository copy to a user-level installation automatically.

## Audit workflow

1. Establish project root, AGENTS.md, task type, requested scope, configuration,
   existing commands/tests and protection manifest. Do not infer task from a name.
2. Inspect data/label schema evidence: column order, target or class mapping, shapes,
   finite-value and duplicate checks. Do not remove industrial outliers. Distinguish
   confirmed declarations from actual data inspections and from historical claims.
3. Trace train/validation/test indices or participant groups through actual callers.
   Check sample/group overlap, time ordering and selection roles. Trace scaler,
   feature selection, PCA and learned transforms: fitting must be training-only.
4. Read actual model construction, explicit/default parameters, fit calls, seeds,
   thread policy and software-version evidence. Separate environment declarations
   from confirmed historical runtime versions. Do not import modules with side effects.
5. Route by task: read [regression.md](references/regression.md) for regression, or
   [classification.md](references/classification.md) for classification. Do not apply
   MSE to class labels or substitute accuracy for regression quality.
6. Compare saved metrics to exact source files, configuration/checkpoint/scaler hashes,
   split IDs and selection scores. Do not calculate new test performance. Separate
   code/protocol migration, numerical reproduction and statistical validity.
7. If paper/figures/PDFs are in scope, read
   [paper-artifacts.md](references/paper-artifacts.md). Inspect existing artifacts,
   not regeneration scripts in execution mode. Rendering/compiling requires separate
   explicit authorization and isolated outputs.
8. Recheck protection hashes and Git status. Report PASS, PARTIAL PASS or NEEDS
   ATTENTION with file/line or JSON-key evidence, checks actually executed, missing
   evidence and remaining limitations. A mechanical hash PASS is not an overall
   reproducibility PASS. Do not describe unavailable trigger tests as successes.

## Offline helpers

Use Python's standard library, with `-B` to suppress bytecode writes:

```text
python -B <skill>/scripts/check_project.py --project-root <root> --config <audit.json>
python -B <skill>/scripts/check_hashes.py --project-root <root> --manifest <relative-path> [--json-key <key>]
```

Audit JSON contains task (regression/classification), task-specific metrics and
required_files; it is an audit specification, NOT a replacement for the experiment's
YAML. A profile may be given by an explicit absolute path outside project root;
referenced project files must still stay within root and outside private/raw paths.
Optional `--output-dir` only checks a future output path; it does not create it.
These two audit helpers have no training/write/overwrite flags. Nonzero exit means evidence or safety check
failed. Source-level reasoning is still required after a helper succeeds.

For these two projects only, read [project-sources.md](references/project-sources.md)
and optionally use steam.audit.json or har.audit.json in references. Profiles contain
source paths, not universal expected metric values. Do not rerun legacy workflow
steps from skill/steam_prediction_skill_v2_final.md: its training/output instructions
are historical material, superseded here by the read-only boundary.

## Discovery is not execution

Valid frontmatter, a skills/list response, explicit invocation, implicit selection,
cross-project selection and safe execution are separate acceptance claims. Record
fresh session IDs, original prompts and tool events showing the actual SKILL.md read.
An independent session must receive only the user task, not a preselected answer.
Negative tests (prose polishing/general Git) should not read this skill. Do not claim
automatic discovery from a manual file read in an already running session.
