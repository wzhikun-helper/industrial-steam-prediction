"""Testable final-fit primitives; real-data entry is disabled."""
import pandas as pd
from src.models import build_ridge_model, build_xgboost_model
from src.fusion import weighted_blend
from src.diagnostics import finite
from src.runtime import create_run_dir, open_new_output, open_new_binary_output


def final_fit_predict(X, y, X_test, *, synthetic=False, factories=None):
    if not synthetic:
        raise ValueError("Real final training/prediction disabled")
    if not isinstance(X,pd.DataFrame) or not isinstance(X_test,pd.DataFrame) or X.empty or X_test.empty:
        raise ValueError("Expected nonempty feature DataFrames")
    if list(X.columns) != list(X_test.columns) or X.columns.has_duplicates or "target" in X_test:
        raise ValueError("Feature schema mismatch")
    labels=finite(y)
    if labels.shape!=(len(X),) or X.index.has_duplicates or X_test.index.has_duplicates:
        raise ValueError("Label length mismatch")
    if isinstance(y,pd.Series) and not y.index.equals(X.index):
        raise ValueError("X/y indices differ")
    finite(X); finite(y); finite(X_test)
    ridge_factory, xgb_factory = factories or (lambda: build_ridge_model(5.), build_xgboost_model)
    ridge, xgb = ridge_factory(), xgb_factory()
    ridge.fit(X,y); xgb.fit(X,y)
    import numpy as np
    rp, xp = np.asarray(ridge.predict(X_test)), np.asarray(xgb.predict(X_test))
    finite(rp); finite(xp)  # Check without changing native prediction precision.
    if rp.shape != (len(X_test),) or xp.shape != rp.shape:
        raise ValueError("Prediction length mismatch")
    frame = pd.DataFrame({"ridge_prediction":rp,"xgboost_prediction":xp,
                          "weighted_prediction":weighted_blend(rp,xp,.7)},index=X_test.index)
    return frame, {"ridge":ridge,"xgboost":xgb}


def save_synthetic_prediction(root, output, frame, models):
    """Exclusive isolated model persistence for synthetic tests only."""
    import joblib
    import json
    create_run_dir(root,output)
    try:
        finite(frame)
        if not isinstance(frame,pd.DataFrame) or frame.empty or frame.index.has_duplicates or list(frame.columns) != ["ridge_prediction","xgboost_prediction","weighted_prediction"]:
            raise ValueError("Prediction columns mismatch")
        if set(models)!={"ridge","xgboost"}:
            raise ValueError("Both ridge and xgboost models are required")
        import numpy as np
        expected=weighted_blend(frame.ridge_prediction.to_numpy(),frame.xgboost_prediction.to_numpy(),.7)
        if not np.allclose(frame.weighted_prediction,expected,atol=1e-12,rtol=1e-10):
            raise ValueError("Weighted prediction formula mismatch")
        for filename, data in (("test_predictions_all_models.csv",frame),
                ("final_test_prediction.csv",frame[["weighted_prediction"]].rename(columns={"weighted_prediction":"prediction"}))):
            with open_new_output(root,output,filename) as stream:
                data.to_csv(stream,index=False)
        for name, model in models.items():
            if name not in ("ridge","xgboost"):
                raise ValueError("Unexpected model key")
            with open_new_binary_output(root,output,f"best_{name}_model.joblib") as stream:
                joblib.dump(model,stream)
        with open_new_binary_output(root,output,"weighted_fusion_config.joblib") as stream:
            joblib.dump({"ridge_weight":.7,"xgboost_weight":.3},stream)
        with open_new_output(root,output,"completion.json") as stream:
            json.dump({"mode":"synthetic","status":"complete"},stream)
    except Exception as error:
        with open_new_output(root,output,"failure.json") as stream:
            json.dump({"status":"failed","message":str(error)},stream)
        raise
