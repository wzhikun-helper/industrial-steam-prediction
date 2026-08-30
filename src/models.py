from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor


def build_ridge_model(alpha=5.0):
    """
    构建 Ridge 回归模型。

    Parameters
    ----------
    alpha : float
        Ridge 正则化强度。

    Returns
    -------
    sklearn.pipeline.Pipeline
        StandardScaler + Ridge 模型。
    """

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("ridge", Ridge(alpha=alpha))
    ])

    return model


def build_xgboost_model(random_state=42):
    """
    构建当前实验中表现最好的 XGBoost 模型。

    Returns
    -------
    xgboost.XGBRegressor
        配置好超参数的 XGBoost 回归模型。
    """

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=2,
        subsample=0.8,
        colsample_bytree=1.0,
        random_state=random_state,
        n_jobs=-1
    )

    return model