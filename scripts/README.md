# Scripts

## Purpose

本目录包含结果整理、论文图生成和辅助检查脚本。论文写作阶段不应重算或改写冻结实验结果。

## Figure scripts

英文图（ACM MM）：`figures/fig1_target_distribution.py` 至 `figures/fig6_prediction_diagnostics.py`。

中文图（《浙江大学学报（工学版）》）：对应的 `figures/*_zh.py`。

所有论文图均从 `results/paper_fig*.csv` 冻结数据动态生成。

## Shared style and checks

## Isolated migration stages

`python scripts/run_experiment.py --config configs/experiment.yaml --output-dir staging/<unique_run_id> --stage <stage>`

Supported stages: `ridge-baseline`, `tree-baselines`, `feature-processing`, `ridge-tuning`.
Additional explicit stage: `xgboost-tuning` reproduces Notebook's 108-candidate search and separately evaluates the historical fixed Best XGBoost. It writes search scores/selection, fixed-fold metrics and trained internal configurations only into a new run directory. No full historical search CSV exists; comparison is limited to saved best selection/score and frozen fixed-model fold metrics.
`fusion` is protocol-precheck-only: invoke with `--dry-run`; real execution is disabled. See FUSION_PROTOCOL.md for covered/uncovered row rules, development-only selection and future outputs.
`shap` and `final-prediction` are also precheck-only with `--dry-run`; real execution is refused before data loading. src/diagnostics.py and src/final_prediction.py expose synthetic-test primitives only for this step.

`python scripts/verify_frozen_results.py` performs a read-only hash and CSV consistency audit.
`python scripts/export_paper_results.py --output-dir staging/<new_id> [--dry-run]` exports explicit frozen CSVs byte-for-byte, with a figure/table source mapping and SHA256 manifest. It never derives paper results from Notebook state.
`--check-only` checks config/output safety without requiring or reading raw data; it reports missing data explicitly. `--dry-run` checks the real data Schema for the first five stages; fusion/shap/final-prediction only precheck protocol/files/paths. Neither mode fits or creates a run directory.
All output directories must be new, under staging/ or reproduction/. Frozen directories cannot be outputs.
Feature processing reproduces the three Notebook Pipelines with fold-local fitting. Ridge tuning uses the original 10 alphas, TimeSeriesSplit(5), negative MSE, n_jobs=-1 and refit=True; no tree tuning is invoked.

- `figures/_style.py`：项目局部统一绘图样式。
- `figures/critique.py`：项目局部 mechanical check，不是 Icarus 官方 full quality gate。
