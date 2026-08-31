# Figures Directory

本目录用于保存工业蒸汽量预测项目中的数据分析图、模型比较图、SHAP 可解释性图以及误差分析图。

## 图像说明

- `target_distribution.png`
  - 目标变量 `target` 的分布图，用于观察整体分布形态和偏态情况。

- `model_mse_comparison.png`
  - 不同回归模型平均 MSE 的对比图，用于展示模型性能排名。

## SHAP 可解释性分析

- `shap_summary_plot.png`
  - SHAP Summary Plot，用于同时展示特征重要性和特征对预测结果的正负贡献方向。

- `shap_feature_importance.png`
  - 基于平均绝对 SHAP 值绘制的 Top 特征重要性柱状图。

- `shap_dependence_V0.png`
  - V0 特征的 SHAP Dependence Plot，用于分析 V0 取值变化与模型预测贡献之间的关系。

- `shap_dependence_V37.png`
  - V37 特征的 SHAP Dependence Plot，用于分析其负向贡献趋势。

## 最终模型结果与误差分析

- `weighted_blend_true_vs_pred.png`
  - 最终加权融合模型真实值与预测值散点图。

- `weighted_blend_residual_plot.png`
  - 最终加权融合模型残差与预测值之间的关系图。

- `weighted_blend_residual_distribution.png`
  - 最终加权融合模型残差分布图。

## 说明

本目录根层图像主要用于 Notebook 实验分析和结果检查；正式论文图已冻结并保存在 `figures/paper/`。

## 正式论文图

正式投稿图统一保存在 `figures/paper/`，与本目录下的 Notebook 草稿图分开管理。

### Fig. 2 — Final / frozen

- Source: `results/paper_fig2_model_performance.csv`
- Outputs:
  - `figures/paper/fig2_model_performance.pdf`
  - `figures/paper/fig2_model_performance.svg`
  - `figures/paper/fig2_model_performance.png`
- Caption uncertainty statement: “Error bars denote ±1 standard deviation across five TimeSeriesSplit validation folds.”

冻结说明：除非实验数据或验证协议发生经确认的变更，不再修改 Fig. 2 的数据、排序、视觉编码或正式输出。

### Fig. 4 — Final / frozen

- Source: `results/paper_fig4_fusion_comparison.csv`
- Outputs:
  - `figures/paper/fig4_fusion_comparison.pdf`
  - `figures/paper/fig4_fusion_comparison.svg`
  - `figures/paper/fig4_fusion_comparison.png`
- Claim: Weighted Blend achieves the lowest MSE on the independent fusion validation set, with only about 0.19% improvement over Best Ridge.
- Status:
  - Mechanical checks: PASS
  - Manual visual review: PASS

冻结说明：除非独立融合验证集的数据或评估协议发生经确认的变更，不再修改 Fig. 4 的数据、排序、视觉编码或正式输出。

### Fig. 6 — Final / frozen

- Source: `results/paper_fig6_prediction_diagnostics.csv`
- Outputs:
  - `figures/paper/fig6_prediction_diagnostics.pdf`
  - `figures/paper/fig6_prediction_diagnostics.svg`
  - `figures/paper/fig6_prediction_diagnostics.png`
- Key metrics:
  - N = 481
  - MSE = 0.176594
  - RMSE = 0.420
  - MAE = 0.287
  - R² = 0.819
- Status:
  - Mechanical checks: PASS
  - Manual visual review: PASS

冻结说明：除非独立融合验证集的数据或评估协议发生经确认的变更，不再修改 Fig. 6 的数据、坐标范围、视觉编码或正式输出。

### Fig. 5 — Final / frozen

- Source: `results/paper_fig5_shap_importance.csv`
- Outputs:
  - `figures/paper/fig5_shap_importance.pdf`
  - `figures/paper/fig5_shap_importance.svg`
  - `figures/paper/fig5_shap_importance.png`
- Interpretation boundary: Explained model = Best XGBoost only
- Status:
  - Mechanical checks: PASS
  - Manual visual review: PASS

冻结说明：除非 Best XGBoost 模型、SHAP 计算数据或解释口径发生经确认的变更，不再修改 Fig. 5 的数据、排序、视觉编码或正式输出。

### Fig. 3 — Final / frozen

- Source:
  - `results/paper_fig3_feature_method_comparison.csv`
  - `results/paper_fig3_ridge_alpha_sensitivity.csv`
- Outputs:
  - `figures/paper/fig3_feature_ridge_sensitivity.pdf`
  - `figures/paper/fig3_feature_ridge_sensitivity.svg`
  - `figures/paper/fig3_feature_ridge_sensitivity.png`
- Status:
  - Mechanical checks: PASS
  - Manual visual review: PASS
- Notes:
  - Panel (a): mean MSE ± 1 SD across five TimeSeriesSplit folds
  - Panel (b): mean MSE only
  - No confidence intervals
  - No significance inference
  - `α = 5` is a shallow numerical optimum

冻结说明：除非特征处理实验、Ridge 参数敏感性数据或验证协议发生经确认的变更，不再修改 Fig. 3 的数据、排序、统计表达或正式输出。

### Fig. 1 — Final / frozen

- Source: `results/paper_fig1_target_distribution.csv`
- Outputs:
  - `figures/paper/fig1_target_distribution.pdf`
  - `figures/paper/fig1_target_distribution.svg`
  - `figures/paper/fig1_target_distribution.png`
- Status:
  - Mechanical checks: PASS
  - Manual visual review: PASS

冻结说明：除非 target 数据或数据处理口径发生经确认的变更，不再修改 Fig. 1 的数据、FD binning、坐标范围、视觉编码或正式输出。
