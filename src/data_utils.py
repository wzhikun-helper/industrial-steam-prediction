from pathlib import Path
import pandas as pd


def load_steam_data(data_dir):
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

    train_path = data_dir / "zhengqi_train.txt"
    test_path = data_dir / "zhengqi_test.txt"

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