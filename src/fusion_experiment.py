"""OOF protocol primitives. Real-data orchestration remains disabled."""
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from src.validation import make_folds
from src.evaluation import evaluate_regression
from src.fusion import weighted_blend


def oof_plan(n_samples):
    folds = make_folds(n_samples, "TimeSeriesSplit")
    covered = np.concatenate([va for _, va in folds])
    if len(np.unique(covered)) != len(covered):
        raise ValueError("Repeated OOF coverage")
    if not np.all(np.diff(covered) > 0):
        raise ValueError("OOF rows must follow source order")
    return folds, covered, np.setdiff1d(np.arange(n_samples), covered)


def generate_oof(X, y, ridge_factory, xgb_factory):
    """Injected factories create fresh fold models; never loads saved models."""
    if len(X) != len(y):
        raise ValueError("X/y length mismatch")
    folds, covered, uncovered = oof_plan(len(X))
    records = []
    for fold, (tr, va) in enumerate(folds, 1):
        ridge, xgb = ridge_factory(), xgb_factory()
        ridge.fit(X.iloc[tr], y.iloc[tr])
        xgb.fit(X.iloc[tr], y.iloc[tr])
        rp, xp = ridge.predict(X.iloc[va]), xgb.predict(X.iloc[va])
        records.extend({"row_id": int(row), "fold": fold, "true_value": float(y.iloc[row]),
                        "ridge_pred": float(rp[j]), "xgb_pred": float(xp[j])}
                       for j, row in enumerate(va))
    frame = pd.DataFrame(records)
    if frame.row_id.tolist() != covered.tolist():
        raise ValueError("OOF alignment failure")
    return frame, uncovered


def split_oof(oof, expected_validation_size=None):
    required = ["row_id", "fold", "true_value", "ridge_pred", "xgb_pred"]
    if not set(required).issubset(oof.columns) or oof.empty:
        raise ValueError("Invalid OOF schema")
    ids = oof.row_id.to_numpy()
    if len(np.unique(ids)) != len(ids) or not np.all(np.diff(ids) > 0):
        raise ValueError("OOF ids must be unique and ascending")
    if not np.isfinite(oof[required].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite OOF data")
    cut = int(len(oof) * .8)
    development, validation = oof.iloc[:cut].copy(), oof.iloc[cut:].copy()
    if development.empty or validation.empty:
        raise ValueError("Empty fusion partition")
    if expected_validation_size is not None and len(validation) != expected_validation_size:
        raise ValueError("Unexpected validation sample count")
    return development, validation


def search_development_weights(development):
    """Only receives development labels; no validation argument or global state."""
    records = []
    for weight in np.arange(0, 1.01, .05):
        pred = weighted_blend(development.ridge_pred, development.xgb_pred, weight)
        records.append({"ridge_weight": float(weight), "xgb_weight": float(1-weight),
                        "development_mse": evaluate_regression(development.true_value, pred)["mse"]})
    result = pd.DataFrame(records)
    return result, float(result.loc[result.development_mse.idxmin(), "ridge_weight"])


def fit_meta_model(development, factory=None):
    model = (factory or (lambda: Ridge(alpha=1.0)))()
    model.fit(development[["ridge_pred", "xgb_pred"]], development.true_value)
    return model


def evaluate_validation(validation, selected_weight, meta_model):
    """All four models evaluated against identical rows and labels."""
    predictions = validation[["row_id", "true_value"]].copy()
    predictions["Best Ridge"] = validation.ridge_pred.to_numpy()
    predictions["Best XGBoost"] = validation.xgb_pred.to_numpy()
    predictions["Weighted Blend"] = weighted_blend(validation.ridge_pred, validation.xgb_pred, selected_weight)
    predictions["Stacking"] = meta_model.predict(validation[["ridge_pred", "xgb_pred"]])
    metrics = [{"model": name, "n_samples": len(validation),
                **evaluate_regression(predictions.true_value, predictions[name])}
               for name in ("Best Ridge", "Best XGBoost", "Weighted Blend", "Stacking")]
    fixed = weighted_blend(validation.ridge_pred, validation.xgb_pred, .7)
    return predictions, pd.DataFrame(metrics), evaluate_regression(validation.true_value, fixed)


def run_real_fusion(*args, **kwargs):
    raise ValueError("Real fusion execution is disabled; use --stage fusion --dry-run")


def protocol_precheck(n_samples=2888):
    _, covered, uncovered = oof_plan(n_samples)
    cut = int(len(covered) * .8)
    return {"mode": "protocol_precheck_only", "training_enabled": False,
            "oof_count": len(covered), "uncovered_count": len(uncovered),
            "oof_first_row": int(covered[0]), "oof_last_row": int(covered[-1]),
            "development_count": cut, "validation_count": len(covered)-cut,
            "validation_first_row": int(covered[cut]),
            "independence": "Validation excluded from weight/meta-model fit; upstream hyperparameter development may use these labels; not external test."}
