import numpy as np


def weighted_blend(ridge_pred, xgb_pred, ridge_weight=0.7):
    """
    对 Ridge 和 XGBoost 的预测结果进行加权融合。

    Parameters
    ----------
    ridge_pred : array-like
        Ridge 模型预测值。

    xgb_pred : array-like
        XGBoost 模型预测值。

    ridge_weight : float
        Ridge 的权重，默认 0.7。
        XGBoost 权重自动为 1 - ridge_weight。

    Returns
    -------
    numpy.ndarray
        融合后的预测结果。
    """

    ridge_pred = np.asarray(ridge_pred)
    xgb_pred = np.asarray(xgb_pred)

    xgb_weight = 1.0 - ridge_weight

    blended_pred = (
        ridge_weight * ridge_pred
        + xgb_weight * xgb_pred
    )

    return blended_pred