# Optional project-specific evidence routes

Industrial steam: configs/experiment.yaml; src/data_utils.py, evaluation.py, models.py,
validation.py, runtime.py; scripts/FUSION_PROTOCOL.md and REMAINING_PROTOCOLS.md;
docs/PYTHON_ENGINEERING_ACCEPTANCE.md (Step28), ENGLISH_LATEX_LAYOUT_REVIEW.md (29),
CHINESE_LATEX_LAYOUT_REVIEW.md (30), STEP31_SCIENTIFIC_WORDING_AND_ACCEPTANCE.md (31).
Step20 protection: results/frozen_artifacts_sha256.md and Notebook write-risk register.
Read results/paper_result_manifest.md, exact archived CSVs and staging comparison reports
for result provenance. Old skill v2 is not a discoverable skill and is not permission
to run its workflow. Current tree-model version differences remain recorded; Ridge and
LightGBM strict reproduction cannot be generalized to all models.

Steam historical fusion: use fusion_model_comparison.csv for final subset comparison;
weighted_blending_summary.csv is a different search-stage score. Last validation rows
were excluded from weight/meta-fit, not necessarily upstream tuning. Fig6 historical
CSV discarded original row IDs; exact per-row ID recovery is UNKNOWN. Do not substitute
rounded plot labels for precise CSVs. All values are project evidence, not universal
expected outputs.

ESP-Fi HAR: configs/formal_seed42.yaml; results/dataset_split.csv (metadata only);
results/formal_seed42/summary.json and test/evaluation_metadata.json, test_metrics.json;
scripts/evaluate.py, fit_normalizer.py, run_experiment.py; src/dataset.py.
47-file historical protection is reports/wifi_csi_baseline_report_final/provenance/
step16/verification.json under protected_file_sha256. Current release index is
reports/wifi_csi_baseline_report_final/release_integrity.json under current_file_sha256;
do not silently substitute it for the 47-file baseline. Public-redaction migrations may
explain historical mismatches; verify exact mappings rather than declaring unchanged.
Never traverse data/raw/ESP-Fi_dataset or open its MAT/CSV files. Split metadata and
saved scaler/checkpoint hashes suffice for this audit; no CNN training or test inference.
