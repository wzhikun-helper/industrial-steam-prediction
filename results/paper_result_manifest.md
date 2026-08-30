# 论文结果主清单

## 1. 数据集与描述统计

主要来源：

- `target_descriptive_statistics.csv`
- `descriptive_statistics.csv`
- `iqr_outlier_statistics.csv`
- `feature_target_correlation.csv`
- `top_features_correlation_matrix.csv`

用途：

- 数据集描述；
- target 分布；
- 异常值分析；
- 特征相关性分析。

---

## 2. 特征处理实验

主要来源：

- `feature_method_comparison.csv`

辅助来源：

- `kbest20_ridge_summary.csv`
- `pca95_ridge_summary.csv`

用途：

- 比较全部 38 个特征、SelectKBest 和 PCA；
- 确定最终采用全部原始特征。

---

## 3. 基础模型比较

主结果来源：

- `final_model_comparison.csv`

辅助来源：

- `baseline_model_comparison.csv`
- `random_forest_summary.csv`
- `gbdt_summary.csv`
- `xgboost_summary.csv`
- `lightgbm_summary.csv`

原则：

> 论文中的模型性能主表优先统一引用 `final_model_comparison.csv`。

---

## 4. Ridge 调参

主要来源：

- `ridge_alpha_tuning.csv`

用途：

- 展示不同 alpha 的性能；
- 最终采用 `alpha = 5.0`。

---

## 5. XGBoost 调参

主要来源：

- `best_xgboost_summary.csv`
- `best_xgboost_cv_metrics.csv`
- `tuning_comparison.csv`

当前最终参数：

```text
n_estimators = 300
learning_rate = 0.05
max_depth = 2
subsample = 0.8
colsample_bytree = 1.0
```

---

## 6. 模型融合

主要来源：

- `fusion_model_comparison.csv`
- `weighted_blending_summary.csv`

辅助来源：

- `weighted_blending_search.csv`

当前融合权重：

```text
Ridge   = 0.7
XGBoost = 0.3
```

注意：

> 加权融合相比 Ridge 只获得小幅提升，论文中不得夸大。

---

## 7. SHAP 模型解释

主要来源：

- `shap_feature_importance.csv`

对应图片：

- `figures/shap_summary_plot.png`
- `figures/shap_dependence_V0.png`
- `figures/shap_dependence_V37.png`

解释对象：

```text
Best XGBoost
```

注意：

> SHAP 解释的不是 Ridge + XGBoost 加权融合模型。

---

## 8. 误差分析

主要来源：

- `weighted_blend_error_analysis.csv`

用途：

- 真实值与预测值分析；
- 残差分析；
- 大误差样本分析。

---

## 9. 验证策略敏感性分析

主要来源：

- `validation_strategy_comparison.csv`

统一结果：

| Validation Strategy | MSE | RMSE | MAE | R² |
|---|---:|---:|---:|---:|
| TimeSeriesSplit | 0.130369 | 0.359262 | 0.263933 | 0.852496 |
| KFold | 0.112940 | 0.335365 | 0.244574 | 0.882662 |

统一 RMSE 定义：

```text
mean(sqrt(fold MSE))
```

注意：

> KFold 指标更好不代表 KFold 一定更合理，只能说明结果对验证策略存在敏感性。

---

## 10. 最终测试集预测

输出文件：

- `final_test_prediction.csv`
- `test_predictions_all_models.csv`

说明：

> 测试集没有 target，因此这些文件不能用于计算或报告测试集 MSE、RMSE、MAE 和 R²。

---

## 11. 中文论文与英文论文统一原则

中文论文和 ACM MM 英文论文必须：

- 使用同一套真实实验结果；
- 使用同一套最终模型参数；
- 使用统一 RMSE 定义；
- 模型主表优先来源于 `final_model_comparison.csv`；
- 所有图表均能追溯到 `results/` 或 `figures/`；
- 不因为写作语言不同而修改实验数字。
