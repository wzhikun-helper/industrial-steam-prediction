# Results

本目录保存冻结的实验评估、融合、解释、误差分析和测试集预测结果。

## A. Main evaluation

- `final_model_comparison.csv`
- `feature_method_comparison.csv`
- `ridge_alpha_tuning.csv`
- `tuning_comparison.csv`
- `validation_strategy_comparison.csv`

## B. Fusion evaluation

- `fusion_model_comparison.csv`
- `paper_fig4_fusion_comparison.csv`
- `paper_fig6_prediction_diagnostics.csv`

最终融合性能采用独立融合验证集（N = 481）。`weighted_blending_summary.csv` 仅记录 weight-search process；其中 same-pool OOF MSE 更乐观，不能作为 final fusion performance。

## C. Interpretation

- `shap_feature_importance.csv`
- `paper_fig5_shap_importance.csv`
- `weighted_blend_error_analysis.csv`

SHAP 仅解释 Best XGBoost；误差分析对应独立融合验证集上的 Weighted Blend。

## D. Paper-specific frozen CSV

- `paper_fig1_target_distribution.csv`
- `paper_fig2_model_performance.csv`
- `paper_fig3_feature_method_comparison.csv`
- `paper_fig3_ridge_alpha_sensitivity.csv`
- `paper_fig4_fusion_comparison.csv`
- `paper_fig5_shap_importance.csv`
- `paper_fig6_prediction_diagnostics.csv`

这些文件是 Fig. 1–Fig. 6 的冻结绘图数据源。论文数字清单见 `paper_result_manifest.md`。

## Other outputs

- `final_test_prediction.csv`：无标签测试集的最终预测。
- `test_predictions_all_models.csv`：多个模型的测试集预测，不能用于计算真实测试指标。
