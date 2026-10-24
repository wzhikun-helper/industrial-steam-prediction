from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

RIDGE_ALPHA_GRID = [0.01, 0.1, 0.5, 1, 2, 5, 10, 20, 50, 100]
XGBOOST_GRID = {"n_estimators": [200, 300, 500], "learning_rate": [0.03, 0.05, 0.1],
                "max_depth": [2, 3, 4], "subsample": [0.8, 1.0], "colsample_bytree": [0.8, 1.0]}


def build_xgboost_search(folds):
    from sklearn.model_selection import GridSearchCV
    from xgboost import XGBRegressor
    return GridSearchCV(XGBRegressor(random_state=42, n_jobs=-1, objective="reg:squarederror"),
                        XGBOOST_GRID, cv=folds, scoring="neg_mean_squared_error",
                        n_jobs=-1, verbose=1, refit=True)


def build_feature_pipeline(name):
    from sklearn.feature_selection import SelectKBest, f_regression
    from sklearn.decomposition import PCA
    if name == "Ridge":
        return build_ridge_model(alpha=1.0)
    if name == "KBest20 + Ridge":
        return Pipeline([("kbest", SelectKBest(score_func=f_regression, k=20)),
                         ("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
    if name == "PCA95 + Ridge":
        return Pipeline([("scaler", StandardScaler()), ("pca", PCA(n_components=0.95)),
                         ("ridge", Ridge(alpha=1.0))])
    raise ValueError("Unknown feature pipeline")


def build_ridge_search(folds):
    from sklearn.model_selection import GridSearchCV
    return GridSearchCV(build_ridge_model(alpha=1.0), {"ridge__alpha": RIDGE_ALPHA_GRID},
                        cv=folds, scoring="neg_mean_squared_error", n_jobs=-1, refit=True)

TREE_BASELINE_PARAMS = {
    "Random Forest": dict(n_estimators=300, random_state=42, n_jobs=-1),
    "GBDT": dict(n_estimators=300, learning_rate=0.05, max_depth=3, random_state=42),
    "XGBoost": dict(n_estimators=300, learning_rate=0.05, max_depth=3,
                    subsample=0.8, colsample_bytree=0.8, random_state=42,
                    n_jobs=-1, objective="reg:squarederror"),
    "LightGBM": dict(n_estimators=300, learning_rate=0.05, max_depth=-1,
                     num_leaves=31, subsample=0.8, colsample_bytree=0.8,
                     random_state=42, n_jobs=-1, verbosity=-1),
}


def build_tree_baseline(name):
    """Unscaled, untuned estimators transcribed from Notebook cells 67/72/77/82."""
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    if name == "Random Forest":
        constructor = RandomForestRegressor
    elif name == "GBDT":
        constructor = GradientBoostingRegressor
    elif name == "XGBoost":
        from xgboost import XGBRegressor
        constructor = XGBRegressor
    elif name == "LightGBM":
        from lightgbm import LGBMRegressor
        constructor = LGBMRegressor
    else:
        raise ValueError("Unknown tree baseline")
    return constructor(**TREE_BASELINE_PARAMS[name])


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

    from xgboost import XGBRegressor

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=2,
        subsample=0.8,
        colsample_bytree=1.0,
        random_state=random_state,
        objective="reg:squarederror",
        n_jobs=-1
    )

    return model
