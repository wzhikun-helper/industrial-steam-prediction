# Regression-specific review

Trace numeric target/feature schemas, exact ordered features and test-label availability.
Without test labels, no MSE/RMSE/MAE/R² may be reported for that test set. Review metrics
implementation, score sign and aggregation: distinguish mean(sqrt(fold MSE)) from
sqrt(mean(fold MSE)); use the actual documented project protocol, not a universal rule.
Single-set RMSE is sqrt(MSE). Fold SD is not a confidence interval or significance test.

Preprocessing must fit within each CV training fold; inspect actual caller/Pipeline,
not just its constructor. Compare validation protocols descriptively, not as proof that
the better score identifies the correct splitting assumption. For TimeSeriesSplit OOF,
early rows can have no validation prediction: never fill them as genuine OOF.

Fusion selection scores are not held-out performance. Exclusion from weight/meta-fit
does not establish external-test independence if upstream tuning used those labels.
Do not silently repair the historical design. SHAP identifies its actual explained
model, not automatically an ensemble; mean absolute SHAP is magnitude, not causal
direction or uncertainty. Numerical tolerances must precede comparisons; don't retrain
or alter parameters repeatedly to match historical numbers.
