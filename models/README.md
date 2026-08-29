# Models Directory

本目录用于保存工业蒸汽量预测项目训练得到的最终模型文件及模型融合配置。

## 文件说明

### `best_ridge_model.joblib`

- 使用全部训练数据重新训练得到的最优 Ridge 模型。
- 最优正则化参数为 `alpha=5`。
- 模型内部包含 `StandardScaler` 和 Ridge 回归器，可直接用于后续预测。

### `best_xgboost_model.joblib`

- 使用全部训练数据重新训练得到的最优 XGBoost 模型。
- 主要参数包括：
  - `n_estimators=300`
  - `learning_rate=0.05`
  - `max_depth=2`
  - `subsample=0.8`
  - `colsample_bytree=1.0`

### `weighted_fusion_config.joblib`

- 保存最终加权融合模型的权重配置。
- Ridge 权重为 `0.7`。
- XGBoost 权重为 `0.3`。

## 最终预测方式

最终预测结果按照以下方式计算：

`Final Prediction = 0.7 × Ridge Prediction + 0.3 × XGBoost Prediction`

模型融合方案是在交叉验证与独立二层测试的基础上确定的。

## 模型加载示例

```python
import joblib

ridge_model = joblib.load("models/best_ridge_model.joblib")
xgb_model = joblib.load("models/best_xgboost_model.joblib")
fusion_config = joblib.load("models/weighted_fusion_config.joblib")
```

加载模型后，可以分别获得 Ridge 和 XGBoost 的预测结果，再按照保存的融合权重生成最终预测。