# Notebook 写入风险登记

单元索引为 JSON 中从 0 开始的索引。当前 diff：611 行新增、0 行删除；新增尾部论文数据导出单元。Notebook 保留原样，未执行。

以下全部写入单元均可能覆盖已有同名文件。RESULTS_DIR=results，MODELS_DIR=models，FIGURES_DIR=figures。未发现直接向 figures/paper 写入的 Notebook 单元；论文数据导出可能间接影响重画图。完整源码片段用于保留动态路径与依赖，不能将此文档作为可执行入口。

## 单元 11

```python
# 数据类型统计
dtype_counts = train_data.dtypes.value_counts()
print(dtype_counts)

# 描述性统计
describe_df = train_data.describe().T
display(describe_df)

# 保存结果
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

dtype_counts.to_csv(
    RESULTS_DIR / "data_type_counts.csv",
    header=["count"]
)

describe_df.to_csv(
    RESULTS_DIR / "descriptive_statistics.csv"
)

print("统计结果已保存到 results/ 目录")
```

## 单元 15

```python
target_stats = train_data["target"].describe()
display(target_stats)

target_stats.to_csv(
    RESULTS_DIR / "target_descriptive_statistics.csv",
    header=["value"]
)
```

## 单元 17

```python
plt.figure(figsize=(7, 4.5))

sns.histplot(
    train_data["target"],
    bins=35,
    kde=True
)

plt.title("Distribution of Target")
plt.xlabel("Target")
plt.ylabel("Count")
plt.tight_layout()

FIGURES_DIR = PROJECT_ROOT / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

plt.savefig(
    FIGURES_DIR / "target_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 22

```python
outlier_df.to_csv(
    RESULTS_DIR / "iqr_outlier_statistics.csv",
    index=False
)

print("IQR异常值统计已保存")
```

## 单元 25

```python
corr_df = corr_with_target.reset_index()
corr_df.columns = ["feature", "correlation"]

corr_df.to_csv(
    RESULTS_DIR / "feature_target_correlation.csv",
    index=False
)

print("特征相关性统计已保存")
```

## 单元 30

```python
corr_matrix.to_csv(
    RESULTS_DIR / "top_features_correlation_matrix.csv"
)

print("相关矩阵已保存")
```

## 单元 47

```python
ridge_cv_df = pd.DataFrame({
    "fold": np.arange(1, len(ridge_mse_scores) + 1),
    "mse": ridge_mse_scores
})

ridge_cv_df.to_csv(
    RESULTS_DIR / "ridge_baseline_cv_mse.csv",
    index=False
)

display(ridge_cv_df)
```

## 单元 50

```python
ridge_metrics_df.to_csv(
    RESULTS_DIR / "ridge_baseline_cv_metrics.csv",
    index=False
)

ridge_summary = pd.DataFrame({
    "model": ["Ridge"],
    "mse_mean": [ridge_metrics_df["mse"].mean()],
    "rmse_mean": [ridge_metrics_df["rmse"].mean()],
    "mae_mean": [ridge_metrics_df["mae"].mean()],
    "r2_mean": [ridge_metrics_df["r2"].mean()]
})

ridge_summary.to_csv(
    RESULTS_DIR / "ridge_baseline_summary.csv",
    index=False
)

display(ridge_summary)
```

## 单元 57

```python
kbest_metrics_df.to_csv(
    RESULTS_DIR / "kbest20_ridge_cv_metrics.csv",
    index=False
)

kbest_summary = pd.DataFrame({
    "model": ["KBest20 + Ridge"],
    "mse_mean": [kbest_metrics_df["mse"].mean()],
    "rmse_mean": [kbest_metrics_df["rmse"].mean()],
    "mae_mean": [kbest_metrics_df["mae"].mean()],
    "r2_mean": [kbest_metrics_df["r2"].mean()]
})

kbest_summary.to_csv(
    RESULTS_DIR / "kbest20_ridge_summary.csv",
    index=False
)
```
## 单元 62

```python
pca_metrics_df.to_csv(
    RESULTS_DIR / "pca95_ridge_cv_metrics.csv",
    index=False
)

pca_summary = pd.DataFrame({
    "model": ["PCA95 + Ridge"],
    "mse_mean": [pca_metrics_df["mse"].mean()],
    "rmse_mean": [pca_metrics_df["rmse"].mean()],
    "mae_mean": [pca_metrics_df["mae"].mean()],
    "r2_mean": [pca_metrics_df["r2"].mean()]
})

pca_summary.to_csv(
    RESULTS_DIR / "pca95_ridge_summary.csv",
    index=False
)
```

## 单元 64

```python
feature_method_summary = pd.concat([
    ridge_summary,
    kbest_summary,
    pca_summary
], ignore_index=True)

display(feature_method_summary)

feature_method_summary.to_csv(
    RESULTS_DIR / "feature_method_comparison.csv",
    index=False
)
```

## 单元 70

```python
rf_metrics_df.to_csv(
    RESULTS_DIR / "random_forest_cv_metrics.csv",
    index=False
)

rf_summary = pd.DataFrame({
    "model": ["Random Forest"],
    "mse_mean": [rf_metrics_df["mse"].mean()],
    "rmse_mean": [rf_metrics_df["rmse"].mean()],
    "mae_mean": [rf_metrics_df["mae"].mean()],
    "r2_mean": [rf_metrics_df["r2"].mean()]
})

rf_summary.to_csv(
    RESULTS_DIR / "random_forest_summary.csv",
    index=False
)
```

## 单元 75

```python
gbdt_metrics_df.to_csv(
    RESULTS_DIR / "gbdt_cv_metrics.csv",
    index=False
)

gbdt_summary = pd.DataFrame({
    "model": ["GBDT"],
    "mse_mean": [gbdt_metrics_df["mse"].mean()],
    "rmse_mean": [gbdt_metrics_df["rmse"].mean()],
    "mae_mean": [gbdt_metrics_df["mae"].mean()],
    "r2_mean": [gbdt_metrics_df["r2"].mean()]
})

gbdt_summary.to_csv(
    RESULTS_DIR / "gbdt_summary.csv",
    index=False
)
```

## 单元 80

```python
xgb_metrics_df.to_csv(
    RESULTS_DIR / "xgboost_cv_metrics.csv",
    index=False
)

xgb_summary = pd.DataFrame({
    "model": ["XGBoost"],
    "mse_mean": [xgb_metrics_df["mse"].mean()],
    "rmse_mean": [xgb_metrics_df["rmse"].mean()],
    "mae_mean": [xgb_metrics_df["mae"].mean()],
    "r2_mean": [xgb_metrics_df["r2"].mean()]
})

xgb_summary.to_csv(
    RESULTS_DIR / "xgboost_summary.csv",
    index=False
)
```

## 单元 85

```python
lgbm_metrics_df.to_csv(
    RESULTS_DIR / "lightgbm_cv_metrics.csv",
    index=False
)

lgbm_summary = pd.DataFrame({
    "model": ["LightGBM"],
    "mse_mean": [lgbm_metrics_df["mse"].mean()],
    "rmse_mean": [lgbm_metrics_df["rmse"].mean()],
    "mae_mean": [lgbm_metrics_df["mae"].mean()],
    "r2_mean": [lgbm_metrics_df["r2"].mean()]
})

lgbm_summary.to_csv(
    RESULTS_DIR / "lightgbm_summary.csv",
    index=False
)
```

## 单元 87

```python
model_comparison = pd.concat([
    ridge_summary,
    rf_summary,
    gbdt_summary,
    xgb_summary,
    lgbm_summary
], ignore_index=True)

model_comparison = model_comparison.sort_values(
    by="mse_mean",
    ascending=True
).reset_index(drop=True)

display(model_comparison)

model_comparison.to_csv(
    RESULTS_DIR / "baseline_model_comparison.csv",
    index=False
)
```

## 单元 91

```python
ridge_tuning_results = pd.DataFrame(ridge_grid.cv_results_)

ridge_tuning_results = ridge_tuning_results[
    [
        "param_ridge__alpha",
        "mean_test_score",
        "std_test_score",
        "rank_test_score"
    ]
].copy()

ridge_tuning_results["mean_mse"] = -ridge_tuning_results["mean_test_score"]

ridge_tuning_results.to_csv(
    RESULTS_DIR / "ridge_alpha_tuning.csv",
    index=False
)

display(
    ridge_tuning_results.sort_values("rank_test_score")
)
```

## 单元 98

```python
best_xgb_metrics_df.to_csv(
    RESULTS_DIR / "best_xgboost_cv_metrics.csv",
    index=False
)

best_xgb_summary = pd.DataFrame({
    "model": ["Best XGBoost"],
    "mse_mean": [best_xgb_metrics_df["mse"].mean()],
    "rmse_mean": [best_xgb_metrics_df["rmse"].mean()],
    "mae_mean": [best_xgb_metrics_df["mae"].mean()],
    "r2_mean": [best_xgb_metrics_df["r2"].mean()]
})

best_xgb_summary.to_csv(
    RESULTS_DIR / "best_xgboost_summary.csv",
    index=False
)
```

## 单元 100

```python
best_ridge_summary = pd.DataFrame({
    "model": ["Best Ridge"],
    "mse_mean": [best_ridge_metrics_df["mse"].mean()],
    "rmse_mean": [best_ridge_metrics_df["rmse"].mean()],
    "mae_mean": [best_ridge_metrics_df["mae"].mean()],
    "r2_mean": [best_ridge_metrics_df["r2"].mean()]
})

tuning_comparison = pd.concat([
    ridge_summary,
    best_ridge_summary,
    xgb_summary,
    best_xgb_summary
], ignore_index=True)

display(tuning_comparison)

tuning_comparison.to_csv(
    RESULTS_DIR / "tuning_comparison.csv",
    index=False
)
```

## 单元 101

```python
best_ridge_cv_result = cross_validate(
    best_ridge_pipeline,
    X,
    y,
    cv=tscv,
    scoring={
        "mse": "neg_mean_squared_error",
        "mae": "neg_mean_absolute_error",
        "r2": "r2"
    }
)

best_ridge_cv_metrics = pd.DataFrame({
    "fold": np.arange(1, 6),
    "mse": -best_ridge_cv_result["test_mse"],
    "rmse": np.sqrt(-best_ridge_cv_result["test_mse"]),
    "mae": -best_ridge_cv_result["test_mae"],
    "r2": best_ridge_cv_result["test_r2"]
})

display(best_ridge_cv_metrics)

print("Mean MSE :", best_ridge_cv_metrics["mse"].mean())
print("Mean RMSE:", best_ridge_cv_metrics["rmse"].mean())
print("Mean MAE :", best_ridge_cv_metrics["mae"].mean())
print("Mean R2  :", best_ridge_cv_metrics["r2"].mean())

best_ridge_cv_metrics.to_csv(
    RESULTS_DIR / "best_ridge_cv_metrics.csv",
    index=False
)
```

## 单元 103

```python
final_model_comparison = pd.concat([
    ridge_summary,
    best_ridge_summary,
    rf_summary,
    gbdt_summary,
    xgb_summary,
    best_xgb_summary,
    lgbm_summary
], ignore_index=True)

final_model_comparison = (
    final_model_comparison
    .sort_values("mse_mean")
    .reset_index(drop=True)
)

display(final_model_comparison)

final_model_comparison.to_csv(
    RESULTS_DIR / "final_model_comparison.csv",
    index=False
)
```

## 单元 105

```python
plot_df = final_model_comparison.sort_values(
    "mse_mean",
    ascending=True
)

plt.figure(figsize=(9, 5))

sns.barplot(
    data=plot_df,
    x="mse_mean",
    y="model"
)

plt.xlabel("Mean MSE")
plt.ylabel("Model")
plt.title("Comparison of Regression Models")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "model_mse_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 111

```python
best_ridge_weight = best_weight_row["ridge_weight"]
best_xgb_weight = best_weight_row["xgb_weight"]

best_blend_pred = (
    best_ridge_weight * oof_ridge
    + best_xgb_weight * oof_xgb
)

blend_mse = mean_squared_error(oof_true, best_blend_pred)
blend_rmse = np.sqrt(blend_mse)
blend_mae = mean_absolute_error(oof_true, best_blend_pred)
blend_r2 = r2_score(oof_true, best_blend_pred)

print("融合 MSE：", blend_mse)
print("融合 RMSE：", blend_rmse)
print("融合 MAE：", blend_mae)
print("融合 R²：", blend_r2)

weight_results_df.to_csv(
    RESULTS_DIR / "weighted_blending_search.csv",
    index=False
)

blend_summary = pd.DataFrame({
    "model": ["Weighted Ridge + XGBoost"],
    "mse": [blend_mse],
    "rmse": [blend_rmse],
    "mae": [blend_mae],
    "r2": [blend_r2],
    "ridge_weight": [best_ridge_weight],
    "xgb_weight": [best_xgb_weight]
})

blend_summary.to_csv(
    RESULTS_DIR / "weighted_blending_summary.csv",
    index=False
)
```

## 单元 123

```python
plt.figure()

shap.summary_plot(
    shap_values,
    X,
    show=False,
    max_display=15
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "shap_summary_plot.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 126

```python
shap_importance_df = pd.DataFrame({
    "feature": X.columns,
    "mean_abs_shap": np.abs(shap_values).mean(axis=0)
})

shap_importance_df = (
    shap_importance_df
    .sort_values("mean_abs_shap", ascending=False)
    .reset_index(drop=True)
)

display(shap_importance_df.head(15))

shap_importance_df.to_csv(
    RESULTS_DIR / "shap_feature_importance.csv",
    index=False
)
```

## 单元 127

```python
top15_shap = shap_importance_df.head(15).sort_values(
    "mean_abs_shap",
    ascending=True
)

plt.figure(figsize=(7, 6))

sns.barplot(
    data=top15_shap,
    x="mean_abs_shap",
    y="feature"
)

plt.xlabel("Mean |SHAP value|")
plt.ylabel("Feature")
plt.title("Top 15 Features by Mean Absolute SHAP Value")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "shap_feature_importance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 129

```python
shap.dependence_plot(
    "V0",
    shap_values,
    X,
    interaction_index=None,
    show=False
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "shap_dependence_V0.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 131

```python
shap.dependence_plot(
    "V37",
    shap_values,
    X,
    interaction_index=None,
    show=False
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "shap_dependence_V37.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 134

```python
plt.figure(figsize=(6, 6))

plt.scatter(
    stack_y_test,
    blend_test_pred,
    alpha=0.55,
    s=24
)

min_value = min(stack_y_test.min(), blend_test_pred.min())
max_value = max(stack_y_test.max(), blend_test_pred.max())

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--"
)

plt.xlabel("True Value")
plt.ylabel("Predicted Value")
plt.title("True vs Predicted Values of Weighted Blend")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "weighted_blend_true_vs_pred.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 136

```python
residuals = stack_y_test - blend_test_pred

plt.figure(figsize=(7, 5))

plt.scatter(
    blend_test_pred,
    residuals,
    alpha=0.55,
    s=24
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.xlabel("Predicted Value")
plt.ylabel("Residual")
plt.title("Residual Plot of Weighted Blend")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "weighted_blend_residual_plot.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 138

```python
plt.figure(figsize=(7, 4.5))

sns.histplot(
    residuals,
    bins=35,
    kde=True
)

plt.axvline(
    x=0,
    linestyle="--"
)

plt.xlabel("Residual")
plt.ylabel("Count")
plt.title("Residual Distribution of Weighted Blend")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "weighted_blend_residual_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

## 单元 140

```python
error_analysis_df = pd.DataFrame({
    "true_value": stack_y_test,
    "predicted_value": blend_test_pred,
    "residual": residuals,
    "absolute_error": np.abs(residuals)
})

error_analysis_df = (
    error_analysis_df
    .sort_values("absolute_error", ascending=False)
    .reset_index(drop=True)
)

display(error_analysis_df.head(10))

error_analysis_df.to_csv(
    RESULTS_DIR / "weighted_blend_error_analysis.csv",
    index=False
)
```

## 单元 147

```python
prediction_df = pd.DataFrame({
    "ridge_prediction": ridge_test_final_pred,
    "xgboost_prediction": xgb_test_final_pred,
    "weighted_prediction": final_test_pred
})

display(prediction_df.head(10))

prediction_df.to_csv(
    RESULTS_DIR / "test_predictions_all_models.csv",
    index=False
)

pd.DataFrame({
    "prediction": final_test_pred
}).to_csv(
    RESULTS_DIR / "final_test_prediction.csv",
    index=False
)

print("预测结果已保存")
```

## 单元 149

```python
import joblib

MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)

joblib.dump(
    final_ridge_model,
    MODELS_DIR / "best_ridge_model.joblib"
)

joblib.dump(
    final_xgb_model,
    MODELS_DIR / "best_xgboost_model.joblib"
)

fusion_config = {
    "ridge_weight": 0.7,
    "xgboost_weight": 0.3
}

joblib.dump(
    fusion_config,
    MODELS_DIR / "weighted_fusion_config.joblib"
)

print("模型与融合配置已保存")
```

## 单元 159

```python
# =========================
# 8.5 保存验证策略对比结果
# =========================

validation_strategy_comparison.to_csv(
    RESULTS_DIR / "validation_strategy_comparison.csv",
    index=True
)

print("已保存：results/validation_strategy_comparison.csv")
```

## 单元 163

```python
paper_fig2_df = pd.DataFrame({
    "model": [
        "Ridge",
        "Best Ridge",
        "XGBoost",
        "Best XGBoost",
        "GBDT",
        "LightGBM",
        "Random Forest"
    ],
    "mse_mean": [
        ridge_baseline_cv_metrics["mse"].mean(),
        best_ridge_cv_metrics["mse"].mean(),
        xgboost_cv_metrics["mse"].mean(),
        best_xgboost_cv_metrics["mse"].mean(),
        gbdt_cv_metrics["mse"].mean(),
        lightgbm_cv_metrics["mse"].mean(),
        random_forest_cv_metrics["mse"].mean()
    ],
    "mse_std": [
        ridge_baseline_cv_metrics["mse"].std(ddof=1),
        best_ridge_cv_metrics["mse"].std(ddof=1),
        xgboost_cv_metrics["mse"].std(ddof=1),
        best_xgboost_cv_metrics["mse"].std(ddof=1),
        gbdt_cv_metrics["mse"].std(ddof=1),
        lightgbm_cv_metrics["mse"].std(ddof=1),
        random_forest_cv_metrics["mse"].std(ddof=1)
    ],
    "rmse_mean": [
        ridge_baseline_cv_metrics["rmse"].mean(),
        best_ridge_cv_metrics["rmse"].mean(),
        xgboost_cv_metrics["rmse"].mean(),
        best_xgboost_cv_metrics["rmse"].mean(),
        gbdt_cv_metrics["rmse"].mean(),
        lightgbm_cv_metrics["rmse"].mean(),
        random_forest_cv_metrics["rmse"].mean()
    ],
    "mae_mean": [
        ridge_baseline_cv_metrics["mae"].mean(),
        best_ridge_cv_metrics["mae"].mean(),
        xgboost_cv_metrics["mae"].mean(),
        best_xgboost_cv_metrics["mae"].mean(),
        gbdt_cv_metrics["mae"].mean(),
        lightgbm_cv_metrics["mae"].mean(),
        random_forest_cv_metrics["mae"].mean()
    ],
    "r2_mean": [
        ridge_baseline_cv_metrics["r2"].mean(),
        best_ridge_cv_metrics["r2"].mean(),
        xgboost_cv_metrics["r2"].mean(),
        best_xgboost_cv_metrics["r2"].mean(),
        gbdt_cv_metrics["r2"].mean(),
        lightgbm_cv_metrics["r2"].mean(),
        random_forest_cv_metrics["r2"].mean()
    ]
})

paper_fig2_df = paper_fig2_df.sort_values(
    by="mse_mean",
    ascending=True
).reset_index(drop=True)

display(paper_fig2_df)

paper_fig2_df.to_csv(
    RESULTS_DIR / "paper_fig2_model_performance.csv",
    index=False
)
```

## 单元 166

```python
best_ridge_mse = fusion_df.loc[
    fusion_df["model"] == "Best Ridge",
    "mse"
].iloc[0]

paper_fig4_df = fusion_df.copy()

paper_fig4_df["mse_difference_vs_best_ridge"] = (
    paper_fig4_df["mse"] - best_ridge_mse
)

paper_fig4_df["mse_change_percent_vs_best_ridge"] = (
    (paper_fig4_df["mse"] - best_ridge_mse)
    / best_ridge_mse
    * 100
)

paper_fig4_df = paper_fig4_df.sort_values(
    by="mse",
    ascending=True
).reset_index(drop=True)

display(paper_fig4_df)

paper_fig4_df.to_csv(
    RESULTS_DIR / "paper_fig4_fusion_comparison.csv",
    index=False
)
```

## 单元 170

```python
paper_fig6_export = paper_fig6_df[
    [
        "true_value",
        "predicted_value",
        "residual",
        "absolute_error"
    ]
].copy()

paper_fig6_export.to_csv(
    RESULTS_DIR / "paper_fig6_prediction_diagnostics.csv",
    index=False
)

print(paper_fig6_export.shape)
display(paper_fig6_export.head())
```

## 单元 172

```python
paper_fig5_df = pd.read_csv(
    RESULTS_DIR / "shap_feature_importance.csv"
)

paper_fig5_df = (
    paper_fig5_df
    .sort_values("mean_abs_shap", ascending=False)
    .reset_index(drop=True)
)

paper_fig5_top15 = paper_fig5_df.head(15).copy()

display(paper_fig5_top15)

paper_fig5_top15.to_csv(
    RESULTS_DIR / "paper_fig5_shap_importance.csv",
    index=False
)
```

## 单元 174

```python
paper_fig3_feature_df = pd.read_csv(
    RESULTS_DIR / "feature_method_comparison.csv"
)

paper_fig3_feature_df = (
    paper_fig3_feature_df
    .sort_values("mse_mean", ascending=True)
    .reset_index(drop=True)
)

display(paper_fig3_feature_df)

paper_fig3_feature_df.to_csv(
    RESULTS_DIR / "paper_fig3_feature_method_comparison.csv",
    index=False
)
```

## 单元 175

```python
paper_fig3_alpha_df = pd.read_csv(
    RESULTS_DIR / "ridge_alpha_tuning.csv"
)

paper_fig3_alpha_df = paper_fig3_alpha_df[
    [
        "param_ridge__alpha",
        "mean_mse",
        "std_test_score"
    ]
].copy()

paper_fig3_alpha_df = paper_fig3_alpha_df.sort_values(
    "param_ridge__alpha"
).reset_index(drop=True)

display(paper_fig3_alpha_df)

paper_fig3_alpha_df.to_csv(
    RESULTS_DIR / "paper_fig3_ridge_alpha_sensitivity.csv",
    index=False
)
```

## 单元 176

```python
ridge_feature_cv = pd.read_csv(
    RESULTS_DIR / "ridge_baseline_cv_metrics.csv"
)

kbest_feature_cv = pd.read_csv(
    RESULTS_DIR / "kbest20_ridge_cv_metrics.csv"
)

pca_feature_cv = pd.read_csv(
    RESULTS_DIR / "pca95_ridge_cv_metrics.csv"
)

feature_mse_std = {
    "Ridge": ridge_feature_cv["mse"].std(ddof=1),
    "KBest20 + Ridge": kbest_feature_cv["mse"].std(ddof=1),
    "PCA95 + Ridge": pca_feature_cv["mse"].std(ddof=1)
}

paper_fig3_feature_df["mse_std"] = (
    paper_fig3_feature_df["model"].map(feature_mse_std)
)

display(paper_fig3_feature_df)

paper_fig3_feature_df.to_csv(
    RESULTS_DIR / "paper_fig3_feature_method_comparison.csv",
    index=False
)
```

## 单元 178

```python
paper_fig1_df = train_data[["target"]].copy()

display(paper_fig1_df.head())

print("shape:", paper_fig1_df.shape)
print("missing values:", paper_fig1_df["target"].isna().sum())

paper_fig1_df.to_csv(
    RESULTS_DIR / "paper_fig1_target_distribution.csv",
    index=False
)
```

本登记是静态覆盖风险证据，不授权重新执行上述Notebook单元。
