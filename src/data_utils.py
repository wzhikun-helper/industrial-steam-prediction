from pathlib import Path
import pandas as pd


def load_steam_data(data_dir, train_file="zhengqi_train.txt", test_file="zhengqi_test.txt"):
    """
    读取工业蒸汽预测训练集和测试集。

    Parameters
    ----------
    data_dir : str or pathlib.Path
        原始数据目录，例如 data/raw。

    Returns
    -------
    train_data : pandas.DataFrame
        训练集，包含 target。

    test_data : pandas.DataFrame
        测试集，不包含 target。
    """

    data_dir = Path(data_dir)

    train_path = data_dir / train_file
    test_path = data_dir / test_file

    # pandas mangles duplicate headers; reject them before parsing.
    import csv
    for path in (train_path, test_path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream, delimiter="\t"))
        if len(header) != len(set(header)):
            raise ValueError(f"Duplicate columns: {path}")

    train_data = pd.read_csv(train_path, sep="\t")
    test_data = pd.read_csv(test_path, sep="\t")

    return train_data, test_data


def split_features_target(train_data, test_data):
    """
    将训练集拆分为特征 X 和目标 y。

    Returns
    -------
    X : pandas.DataFrame
        训练特征。

    y : pandas.Series
        训练目标 target。

    X_test : pandas.DataFrame
        测试特征。
    """

    X = train_data.drop(columns=["target"])
    y = train_data["target"]
    X_test = test_data.copy()

    return X, y, X_test


def validate_steam_data(train, test, features, target, train_shape, test_shape):
    """Validate without filtering, transforming or fitting data."""
    import numpy as np
    for frame, shape, columns in (
        (train, train_shape, features + [target]),
        (test, test_shape, features),
    ):
        if frame.columns.has_duplicates:
            raise ValueError("Duplicate columns")
        if list(frame.shape) != list(shape) or list(frame.columns) != columns:
            raise ValueError("Incorrect shape or ordered schema")
        if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in frame.dtypes):
            raise ValueError("All values must have numeric dtypes")
        if not np.isfinite(frame.to_numpy(dtype=float)).all():
            raise ValueError("NaN or Inf values are forbidden")
