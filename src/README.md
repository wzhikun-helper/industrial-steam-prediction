# src

本目录用于存放工业蒸汽量预测项目中可复用的 Python 模块。

相比于直接将所有代码集中写在 Jupyter Notebook 中，将数据读取、模型构建、模型评估和模型融合等功能拆分到独立模块，可以提高代码的可读性、复用性和实验可复现性。

## 文件说明

### `data_utils.py`

负责数据读取与基础拆分。

主要功能：

- 读取 `data/raw/zhengqi_train.txt`
- 读取 `data/raw/zhengqi_test.txt`
- 将训练集拆分为特征 `X` 和目标变量 `y`
- 构造测试特征 `X_test`

主要函数：

```python
load_steam_data()
split_features_target()
```

---

### `evaluation.py`

负责回归模型的评价指标计算和交叉验证结果汇总。

主要指标：

- MSE
- RMSE
- MAE
- R²

主要函数：

```python
evaluate_regression()
summarize_cv_scores()
```

其中 `summarize_cv_scores()` 对各折交叉验证结果进行汇总，RMSE 采用“先计算每一折 RMSE，再求平均”的方式，与当前 Notebook 中的主要实验保持一致。

---

### `models.py`

负责构建项目中的核心预测模型。

目前包含：

- Ridge Regression
- XGBoost Regressor

主要函数：

```python
build_ridge_model()
build_xgboost_model()
```

当前默认 Ridge 参数：

```text
alpha = 5.0
```

当前 XGBoost 主要参数：

```text
n_estimators = 300
learning_rate = 0.05
max_depth = 2
subsample = 0.8
colsample_bytree = 1.0
```

这些参数来源于 Notebook 中的模型调参与验证结果。

---

### `fusion.py`

负责模型预测结果的加权融合。

当前主要融合方式为：

```text
Ridge   = 0.7
XGBoost = 0.3
```

主要函数：

```python
weighted_blend()
```

该函数根据给定权重，对 Ridge 和 XGBoost 的预测结果进行线性加权。

---

## 模块调用示例

```python
from src.data_utils import load_steam_data, split_features_target
from src.models import build_ridge_model, build_xgboost_model
from src.evaluation import evaluate_regression
from src.fusion import weighted_blend
```

这些模块主要用于支持：

- Jupyter Notebook 实验
- 模型复现
- 后续脚本化训练
- 论文实验结果复核
- 最终预测结果生成

## 说明

`src/` 中的代码应尽量保持模块化和通用化。

Notebook 主要用于：

- 数据探索
- 实验过程展示
- 结果分析
- 可视化

而 `src/` 主要用于：

- 可复用函数
- 模型定义
- 评估逻辑
- 数据处理逻辑
- 模型融合逻辑

后续如增加新的训练流程、特征工程或可视化模块，可继续在本目录中扩展。