"""Prediction diagnostics and synthetic-only SHAP calculation."""
import numpy as np
import pandas as pd
from src.evaluation import evaluate_regression


def finite(values):
    array = np.asarray(values, dtype=float)
    if not np.isfinite(array).all():
        raise ValueError("NaN/Inf forbidden")
    return array


def error_analysis(true, predicted, row_ids, expected_n=None):
    true, predicted = finite(true), finite(predicted)
    ids = np.asarray(row_ids)
    if true.ndim != 1 or predicted.shape != true.shape or ids.shape != true.shape:
        raise ValueError("Lengths/dimensions differ")
    if (ids.dtype.kind not in 'iu' or ids.dtype.kind=='b' or (ids<0).any()
            or len(set(ids.tolist())) != len(ids) or len(true)<2):
        raise ValueError("Invalid row IDs")
    if expected_n is not None and len(true) != expected_n:
        raise ValueError("Unexpected sample count")
    residual = true - predicted
    frame = pd.DataFrame(dict(row_id=ids, true_value=true, predicted_value=predicted,
                              residual=residual, absolute_error=np.abs(residual)))
    # Historical pandas default sorting; no claim about stable order within ties.
    return frame.sort_values("absolute_error", ascending=False).reset_index(drop=True), evaluate_regression(true, predicted)


def shap_importance(model, X, *, explained_model, synthetic=False, explainer_factory=None):
    if explained_model != "Best XGBoost":
        raise ValueError("SHAP is restricted to Best XGBoost")
    if not synthetic or explainer_factory is None:
        raise ValueError("Real SHAP disabled; synthetic tests must inject an explainer")
    if not isinstance(X,pd.DataFrame) or X.empty or X.columns.has_duplicates:
        raise ValueError("Expected nonempty SHAP DataFrame with unique columns")
    finite(X)
    values = finite(explainer_factory(model).shap_values(X))
    if values.shape != X.shape or X.columns.has_duplicates:
        raise ValueError("SHAP shape/features mismatch")
    return pd.DataFrame({"feature": X.columns, "mean_abs_shap": np.abs(values).mean(axis=0)}).sort_values(
        "mean_abs_shap", ascending=False).reset_index(drop=True)
