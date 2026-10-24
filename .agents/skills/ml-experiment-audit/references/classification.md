# Classification-specific review

Check class ID/name mapping, fixed label order, missing classes and subject/session
grouping. Participant-disjoint train/validation/test is not equivalent to random
window split; inspect CSV split metadata, sample IDs and actual dataloader filtering.
Check overlapping windows and source recording leakage across groups.

Accuracy = correct/all; Macro-F1 = unweighted mean of per-class F1 for the specified
label set. Record zero_division handling, averaging, percentage vs fraction and
confusion-matrix row/column orientation. Weighted-F1 is not Macro-F1. Read archived
test metrics and their code definitions; do not infer again or recompute test scores.

Trace validation-only checkpoint selection/early stopping and checkpoint hashes.
Scaler/normalizer provenance must identify train-only participants and split hash.
Read metadata and source, hash weights as bytes; do not load PyTorch/joblib pickles.
Class mapping, saved checkpoint, scaler and test-evaluation metadata must agree.
Do not require regression metrics or interpret integer class labels as a regression
target. Treat synthetic tests as functionality evidence, never new classification
performance. Cross-subject claims remain bounded to the archived split and dataset.
