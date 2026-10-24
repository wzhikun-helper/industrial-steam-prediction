# Fusion migration protocol (Step26)

Notebook source: cells107,109,111,113–119. Original code concatenates TimeSeriesSplit(5) validation predictions in fold order, without storing source row IDs. Migration explicitly records zero-based source row positions and fold IDs; it does not impute OOF predictions for uncovered rows.

For 2888 rows, first 483 rows (0–482) lack OOF. Covered rows483–2887 total2405. int(2405*0.8)=1924 development rows483–2406; final481 validation rows2407–2887. This is an 80/20 split of covered OOF rows, not an arbitrary last481 split for all datasets.

Base models: StandardScaler→Ridge(alpha=5); XGBRegressor(n_estimators=300,learning_rate=.05,max_depth=2,subsample=.8,colsample_bytree=1.,random_state=42,n_jobs=-1,objective=reg:squarederror). Both refit per fold on raw X/y with no saved model loading. Future orchestration must inject existing build_ridge_model(alpha=5) and build_xgboost_model, never the current search winner.

Two historical searches must be distinguished: cells109/111 search the entire OOF pool with np.arange(0,1.01,.05) and export weighted_blending_summary.csv (MSE about0.125956, in-sample selection score). Cells114/115 split OOF first, then select weights on development rows only; cell116 evaluates selected weights on validation. Migration's search_development_weights only receives development data. The historical development search score is a third quantity and must not be labeled as the all-OOF search score.

Cell119 meta-model: Ridge(alpha=1), fitted directly on two OOF prediction columns in development set, with intercept/default settings and no StandardScaler. It is manual stacking, not StackingRegressor with another hidden CV. Validation predictions use the last OOF fold's base predictions. All four comparisons share labels/rows; fixed .7/.3 evaluation is saved separately from development-selected weight evaluation even when weights coincide. No validation-driven reselection.

Known limitation: final481 labels excluded from weight and meta-model fitting, but upstream hyperparameter development may use those labels. This is not an independent external test. Migration does not repair historical design by changing wording or splitting rules. Original exact runtime threads/defaults and persisted OOF row-ID artifacts are UNKNOWN.

## Current execution boundary

`--stage fusion --dry-run` validates config, file availability and output isolation, then computes index counts only. It does not load data or train. Without --dry-run the fusion stage refuses execution before data loading or directory creation. Module primitives are executable for synthetic testing; no real-data output runner exists. Historical all-OOF search remains documented only and is not silently performed by the development-only selector.

## Future isolated output contract

Under a new staging/<run_id>/ or reproduction/<run_id>/ only:

- config_snapshot.json, metadata.json: actual versions, seeds, explicit and resolved parameters, base-model internal configs, execution mode, source hashes and independence limits.
- fold_indices.json, uncovered_indices.json, oof_predictions.csv: row_id/fold/true_value/ridge_pred/xgb_pred.
- development_indices.json, validation_indices.json.
- development_weight_search.csv and selection.json: development scores/selected weights only.
- optional all_oof_exploratory_search.csv: explicitly labeled historical same-pool diagnostic, never final validation score or input to final selection.
- validation_predictions.csv: identical row_id and true_value for four models.
- validation_metrics.csv and fixed_07_03_metrics.csv: selected blend and fixed blend kept distinct.
- comparison_report.md: strict prospective tolerance and frozen-source comparisons; no experimental values hardcoded as generated results.
- completion.json only after success; failure.json on exception, no success marker.

Minimum future plan requires separate authorization: preflight frozen hashes and row-index checks; one historical fixed-base OOF run, development-only selection/meta-fit, single final481 evaluation; compare without replacing results. Current XGBoost version differences must remain recorded and may propagate into fusion. No current real fusion run is authorized by this step.
