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

当前图像主要用于 Notebook 实验分析和结果检查。

后续在撰写中文论文和英文论文时，将进一步统一字体、线宽、配色、图例和版式，并重新输出适合论文排版的高质量科研图。