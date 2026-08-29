# Results Directory

本目录用于保存工业蒸汽量预测项目运行过程中产生的实验结果文件，包括数据统计结果、模型评估指标、参数优化结果、模型融合结果、SHAP 特征重要性以及最终测试集预测结果。

## 主要文件说明

### 数据分析结果

- `data_type_counts.csv`
  - 保存训练数据中不同数据类型的数量。

- `descriptive_statistics.csv`
  - 保存各特征及目标变量的描述性统计结果。

- `target_descriptive_statistics.csv`
  - 保存目标变量 `target` 的统计信息。

- `iqr_outlier_statistics.csv`
  - 保存基于 IQR 方法统计得到的各特征异常值数量和比例。

- `feature_target_correlation.csv`
  - 保存各输入特征与目标变量之间的 Pearson 相关系数。

- `top_features_correlation_matrix.csv`
  - 保存高相关特征之间的相关系数矩阵。

## 特征处理实验

- `feature_method_comparison.csv`
  - 比较全部特征、KBest 特征筛选和 PCA 降维三种方案。

- `kbest20_ridge_cv_metrics.csv`
  - KBest 选择 20 个特征后 Ridge 模型的交叉验证结果。

- `pca95_ridge_cv_metrics.csv`
  - PCA 保留 95% 累计解释方差后 Ridge 模型的交叉验证结果。

## 基础模型实验

- `ridge_baseline_cv_metrics.csv`
- `random_forest_cv_metrics.csv`
- `gbdt_cv_metrics.csv`
- `xgboost_cv_metrics.csv`
- `lightgbm_cv_metrics.csv`

以上文件分别保存各基础模型在交叉验证中的 MSE、RMSE、MAE 和 R²。

- `baseline_model_comparison.csv`
  - 保存基础模型性能汇总与排名。

## 参数优化

- `ridge_alpha_tuning.csv`
  - Ridge 正则化参数 `alpha` 的网格搜索结果。

- `tuning_comparison.csv`
  - Ridge 和 XGBoost 参数优化前后的性能比较。

- `best_xgboost_cv_metrics.csv`
  - 优化后 XGBoost 的交叉验证结果。

- `final_model_comparison.csv`
  - 保存所有主要模型及优化模型的最终性能排名。

## 模型融合

- `weighted_blending_search.csv`
  - 保存 Ridge 与 XGBoost 不同加权比例下的 MSE。

- `weighted_blending_summary.csv`
  - 保存最优加权融合方案及其指标。

- `fusion_model_comparison.csv`
  - 比较 Best Ridge、Best XGBoost、Weighted Blend 和 Stacking。

## SHAP 分析

- `shap_feature_importance.csv`
  - 保存各特征的平均绝对 SHAP 值，用于分析特征整体重要性。

## 误差分析

- `weighted_blend_error_analysis.csv`
  - 保存最终融合模型在独立二层测试集上的真实值、预测值、残差和绝对误差。

## 最终预测

- `test_predictions_all_models.csv`
  - 保存 Ridge、XGBoost 和最终加权融合模型在官方测试集上的全部预测结果。

- `final_test_prediction.csv`
  - 保存最终加权融合模型的官方测试集预测结果。