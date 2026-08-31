# Figure Titles and Captions

This file is the single source of truth for the titles, captions, and reported numerical results of Fig. 1–Fig. 6 in both the Chinese manuscript and the ACM MM manuscript. Do not edit figure-specific numbers independently in either manuscript; update and verify them here first.

The titles and captions are not embedded in the figure images. For the Chinese manuscript, typeset the Chinese title in bold SimSun at 小5号 and the English title in Times New Roman at 小5号. Chinese and English content must remain aligned in meaning.

## Fig. 1

**Source:** `results/paper_fig1_target_distribution.csv`

### 中文图题

图1 工业蒸汽量目标变量的分布

### English title

Fig.1 Distribution of industrial steam target variable

### 中文图注

训练集共包含 2 888 个样本。直方图采用 Freedman-Diaconis 规则确定分箱，虚线和点划线分别表示目标变量的均值（0.126）和中位数（0.313）。目标变量主要集中于中间取值区域，同时保留两侧尾部样本，为后续回归误差分析提供数据尺度背景。

### English caption

The training set contains 2,888 samples. Histogram bins are determined using the Freedman-Diaconis rule. The dashed and dash-dotted lines indicate the mean (0.126) and median (0.313), respectively. The target variable is concentrated mainly in the central range while retaining observations in both tails, providing distributional and scale context for subsequent regression error analysis.

## Fig. 2

**Source:** `results/paper_fig2_model_performance.csv`

### 中文图题

图2 不同回归模型在5折 TimeSeriesSplit 验证下的预测性能

### English title

Fig.2 Prediction performance of regression models under five-fold TimeSeriesSplit validation

### 中文图注

比较 Ridge、XGBoost、GBDT、LightGBM、Random Forest 及其调优模型的均方误差（MSE）。误差棒表示5折 TimeSeriesSplit 验证结果的 ±1 个标准差。Best Ridge 的平均 MSE 最低，为 0.1304，但与未调优 Ridge 的差异较小。Best XGBoost 调优后性能有所改善，但平均 MSE 仍高于 Ridge 系列。图中不进行统计显著性推断。

### English caption

Mean squared error (MSE) is compared for Ridge, XGBoost, GBDT, LightGBM, Random Forest, and the corresponding tuned models. Error bars denote ±1 standard deviation across five TimeSeriesSplit validation folds. Best Ridge achieves the lowest mean MSE of 0.1304, although the difference from the untuned Ridge model is small. Tuning improves XGBoost performance, but its mean MSE remains higher than those of the Ridge models. No statistical significance inference is made.

## Fig. 3

**Sources:**

- `results/paper_fig3_feature_method_comparison.csv`
- `results/paper_fig3_ridge_alpha_sensitivity.csv`

### 中文图题

图3 特征处理方法和 Ridge 正则化参数对预测误差的影响

### English title

Fig.3 Effects of feature processing and Ridge regularization parameter on prediction error

### 中文图注

（a）比较使用全部38个特征的 Ridge、KBest20 + Ridge 和 PCA95 + Ridge 的平均 MSE，误差棒表示5折 TimeSeriesSplit 验证结果的 ±1 个标准差。在当前数据集和验证设置下，使用全部特征的 Ridge 获得最低平均 MSE。（b）给出不同正则化参数 α 下 Ridge 的平均交叉验证 MSE。α=5 时取得最低观测均值 0.1304，但与邻近参数相比差异较小，属于浅幅数值最优；当 α 增大至20以上时，MSE 呈上升趋势。为保证趋势可读性，子图（b）未绘制折间标准差。

### English caption

(a) Mean MSE values are compared for Ridge using all 38 features, KBest20 + Ridge, and PCA95 + Ridge. Error bars denote ±1 standard deviation across five TimeSeriesSplit validation folds. Under the current dataset and validation setting, Ridge using all features achieves the lowest mean MSE. (b) Mean cross-validation MSE of Ridge is shown for different regularization parameters α. The lowest observed mean MSE of 0.1304 occurs at α=5, but the difference from neighboring settings is small, indicating only a shallow numerical optimum. MSE increases when α becomes larger than 20. Fold-wise standard deviations are omitted from panel (b) to preserve trend readability.

## Fig. 4

**Source:** `results/paper_fig4_fusion_comparison.csv`

### 中文图题

图4 独立融合验证集上不同模型的均方误差比较

### English title

Fig.4 Comparison of model mean squared errors on independent fusion validation set

### 中文图注

在相同的独立融合验证集上比较 Weighted Blend、Best Ridge、Stacking 和 Best XGBoost 的 MSE。Weighted Blend 的 MSE 最低，为 0.1766；Best Ridge 的 MSE 为 0.1769，两者数值非常接近。相对于 Best Ridge，Weighted Blend 的 MSE 仅降低约 0.19%，属于边际数值改善。Stacking 略差于 Best Ridge，Best XGBoost 的误差最高。由于当前结果没有独立重复实验或置信区间，不进行统计显著性推断。

### English caption

MSE values of Weighted Blend, Best Ridge, Stacking, and Best XGBoost are compared on the same independent fusion validation set. Weighted Blend achieves the lowest MSE of 0.1766, while Best Ridge obtains an MSE of 0.1769, indicating very similar numerical performance. Relative to Best Ridge, Weighted Blend reduces MSE by only approximately 0.19%, representing a marginal numerical improvement. Stacking performs slightly worse than Best Ridge, while Best XGBoost has the highest error. No statistical significance inference is made because independent repeated experiments or confidence intervals are unavailable.

## Fig. 5

**Source:** `results/paper_fig5_shap_importance.csv`

### 中文图题

图5 Best XGBoost 模型的全局 SHAP 特征重要性

### English title

Fig.5 Global SHAP feature importance of Best XGBoost model

### 中文图注

展示 Best XGBoost 模型中平均绝对 SHAP 值最大的15个特征。V0 的平均绝对 SHAP 值最高，为 0.329，V1 次之，为 0.179，此后特征贡献快速下降，表明该 XGBoost 分支的全局预测贡献主要集中于少数头部特征。平均绝对 SHAP 值仅反映特征贡献幅度，不表示影响方向、因果关系或统计显著性。本图仅解释 Best XGBoost，不直接解释 Weighted Blend 或完整融合模型。

### English caption

The 15 features with the largest mean absolute SHAP values for Best XGBoost are shown. V0 has the highest mean absolute SHAP value of 0.329, followed by V1 with 0.179, after which feature contributions decline rapidly, indicating that global prediction contributions in the XGBoost branch are concentrated among a small number of dominant features. Mean absolute SHAP values represent contribution magnitude only and do not indicate effect direction, causality, or statistical significance. This figure explains Best XGBoost only and does not directly explain Weighted Blend or the complete fusion model.

## Fig. 6

**Source:** `results/paper_fig6_prediction_diagnostics.csv`

### 中文图题

图6 Weighted Blend 模型在独立融合验证集上的预测与残差诊断

### English title

Fig.6 Prediction and residual diagnostics of Weighted Blend on independent fusion validation set

### 中文图注

独立融合验证集包含481个样本，Weighted Blend 的 MSE、RMSE、MAE 和 R² 分别为0.1766、0.420、0.287和0.819。（a）观测值与预测值的关系，虚线表示理想预测关系 y=x；大多数样本分布在参考线附近，但仍存在少量较大预测偏差。（b）预测值与残差的关系，虚线表示零残差；残差在零值两侧均有分布，并存在较长的正残差尾部。（c）残差频数分布，用于辅助展示残差的集中区域及尾部特征。所有481个验证样本均保留，未删除或裁剪大误差样本。

### English caption

The independent fusion validation set contains 481 samples. Weighted Blend obtains MSE, RMSE, MAE, and R² values of 0.1766, 0.420, 0.287, and 0.819, respectively. (a) Relationship between observed and predicted values, where the dashed line denotes the ideal prediction relationship y=x. Most samples lie near the reference line, although several relatively large prediction deviations remain. (b) Relationship between predicted values and residuals, where the dashed line denotes zero residual. Residuals occur on both sides of zero and exhibit a longer positive tail. (c) Residual frequency distribution, providing complementary information on residual concentration and tail behavior. All 481 validation samples are retained without removal or clipping of large-error observations.

## Locked numerical facts

The following values are shared across the Chinese and English manuscripts and must not be edited independently:

| Figure | Locked facts |
|---|---|
| Fig. 1 | N = 2,888; mean = 0.126; median = 0.313; Freedman-Diaconis binning |
| Fig. 2 | Best Ridge mean MSE = 0.1304; error bars = ±1 SD across five TimeSeriesSplit folds |
| Fig. 3 | 38 features; α = 5; lowest observed mean MSE = 0.1304; panel (a) includes ±1 SD; panel (b) is mean-only |
| Fig. 4 | Weighted Blend MSE = 0.1766; Best Ridge MSE = 0.1769; relative reduction ≈ 0.19% |
| Fig. 5 | explained model = Best XGBoost only; V0 = 0.329; V1 = 0.179; Top-15 retained |
| Fig. 6 | N = 481; MSE = 0.1766; RMSE = 0.420; MAE = 0.287; R² = 0.819; no sample clipping |

