"""Read-only hash/source audit; never loads fitted model pickle files."""
import json
import hashlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from src.diagnostics import error_analysis, finite
from src.frozen import verify_registry


def verify(root=ROOT, *, hashes_only=False):
    root=Path(root)
    pairs=verify_registry(root)
    changed=[]
    if hashes_only:
        return {"frozen_count":len(pairs),"changed":[],"status":"PASS",
                "scope":"89 registered artifacts only; Notebook and derived CSV checks not performed"}
    notebook=hashlib.sha256((root/"notebooks/01_experiment.ipynb").read_bytes()).hexdigest()
    shap=pd.read_csv(root/"results/shap_feature_importance.csv")
    top=pd.read_csv(root/"results/paper_fig5_shap_importance.csv")
    pd.testing.assert_frame_equal(shap.sort_values("mean_abs_shap",ascending=False).head(15).reset_index(drop=True),top)
    diag=pd.read_csv(root/"results/paper_fig6_prediction_diagnostics.csv")
    original=pd.read_csv(root/"results/weighted_blend_error_analysis.csv")
    pd.testing.assert_frame_equal(diag,original[list(diag.columns)])
    _,metrics=error_analysis(diag.true_value,diag.predicted_value,np.arange(len(diag)),expected_n=481)
    np.testing.assert_allclose(diag.residual,diag.true_value-diag.predicted_value,atol=1e-12)
    np.testing.assert_allclose(diag.absolute_error,np.abs(diag.residual),atol=1e-12)
    if not diag.absolute_error.is_monotonic_decreasing:
        raise ValueError("Error order mismatch")
    fusion=pd.read_csv(root/"results/fusion_model_comparison.csv")
    row=fusion[fusion.model=="Weighted Blend"].iloc[0]
    for m,v in metrics.items():
        np.testing.assert_allclose(v,row[m],atol=1e-12,rtol=1e-10)
    predictions=pd.read_csv(root/"results/test_predictions_all_models.csv")
    final=pd.read_csv(root/"results/final_test_prediction.csv")
    if list(predictions.columns)!=["ridge_prediction","xgboost_prediction","weighted_prediction"]:
        raise ValueError("Prediction columns differ")
    if final.shape!=(1925,1) or list(final.columns)!=["prediction"] or len(predictions)!=1925:
        raise ValueError("Final prediction schema/length differs")
    finite(predictions); finite(final)
    float64_blend=.7*predictions.ridge_prediction.to_numpy()+.3*predictions.xgboost_prediction.to_numpy()
    mixed_blend=.7*predictions.ridge_prediction.to_numpy()+np.float32(.3)*predictions.xgboost_prediction.to_numpy().astype(np.float32)
    float64_difference=float(np.max(np.abs(predictions.weighted_prediction-float64_blend)))
    mixed_difference=float(np.max(np.abs(predictions.weighted_prediction-mixed_blend)))
    np.testing.assert_allclose(predictions.weighted_prediction,mixed_blend,atol=1e-12,rtol=1e-10)
    np.testing.assert_allclose(final.prediction,predictions.weighted_prediction,atol=1e-12)
    return {"frozen_count":len(pairs),"changed":changed,"notebook_sha256":notebook,
        "notebook_match":notebook=="807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be",
        "shap_top15":"PASS; Best XGBoost only","diagnostics":metrics,
        "prediction_rows":len(final),"prediction_columns":list(predictions.columns),
        "float64_formula_max_difference":float64_difference,"float32_xgb_term_max_difference":mixed_difference,
        "precision_note":"CSV float64 arithmetic differs; mixed float32 XGBoost term reconstructs saved values. Historical native dtype not archived directly.",
        "historical_row_ids":"UNKNOWN: error CSV reset_index drops original row IDs; no exact provenance proof from row order alone",
        "model_files":"Hash verified only; no pickle deserialization"}


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hashes-only",action="store_true",help="Only the 89 registered artifacts; excludes unpublished Notebook working-copy check")
    args=parser.parse_args()
    try:
        report=verify(hashes_only=args.hashes_only)
        print(json.dumps(report,indent=2))
        raise SystemExit(0 if not report["changed"] and report.get("notebook_match",True) else 2)
    except (ValueError,OSError,KeyError,AssertionError) as error:
        print(json.dumps({"status":"NEEDS ATTENTION","error":str(error)}))
        raise SystemExit(2)
