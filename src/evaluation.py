import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)


def evaluate_regression(y_true, y_pred):
    """
    计算回归模型常用评价指标。

    Parameters
    ----------
    y_true : array-like
        真实值。
    y_pred : array-like
        模型预测值。

    Returns
    -------
    dict
        包含 MSE、RMSE、MAE 和 R²。
    """

    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    return {
    "mse": float(mse),
    "rmse": float(rmse),
    "mae": float(mae),
    "r2": float(r2),
}
def summarize_cv_scores(cv_scores):
    """
    汇总 sklearn cross_validate 返回的交叉验证结果。

    Parameters
    ----------
    cv_scores : dict
        cross_validate 返回的结果字典。

    Returns
    -------
    dict
        各折平均的 MSE、RMSE、MAE 和 R²。
    """

    mse_values = -cv_scores["test_mse"]
    mae_values = -cv_scores["test_mae"]
    r2_values = cv_scores["test_r2"]

    rmse_values = np.sqrt(mse_values)

    return {
        "mse": float(np.mean(mse_values)),
        "rmse": float(np.mean(rmse_values)),
        "mae": float(np.mean(mae_values)),
        "r2": float(np.mean(r2_values)),
    }