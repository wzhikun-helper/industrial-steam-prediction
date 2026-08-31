# Industrial Steam Prediction

## Overview

本项目围绕工业蒸汽量回归预测，比较正则化线性模型、树模型、特征处理、超参数优化、模型融合与 SHAP 解释。项目用于实验研究和论文整理，不宣称 SOTA，也不夸大边际性能差异。

## Dataset

- 训练集：2,888 个样本、38 个匿名特征（`V0`–`V37`）和目标变量 `target`。
- 测试集：1,925 个样本、38 个匿名特征，无公开真实标签。

## Methods

Ridge、XGBoost、GBDT、LightGBM、Random Forest、KBest、PCA、Weighted Blend、Stacking 和 SHAP。

## Validation

主评估使用 5 折 `TimeSeriesSplit`；`KFold` 仅用于验证策略敏感性分析。数据的严格时间语义尚未完全确认，因此不能据此证明某一种划分必然更合理。

## Key Results

Best Ridge（`alpha = 5`）：MSE = 0.1304，RMSE = 0.3593，MAE = 0.2639，R² = 0.8525。

独立融合验证集 N = 481。Weighted Blend（0.7 Ridge + 0.3 XGBoost）：MSE = 0.1766，RMSE = 0.420，MAE = 0.287，R² = 0.819。其 MSE 相对 Best Ridge 仅降低约 0.19%，属于边际数值改善。

## Interpretability

SHAP 仅解释 Best XGBoost 分支，不解释 Weighted Blend 或完整融合模型。全局平均绝对 SHAP 值中，`V0 = 0.329`、`V1 = 0.179`；匿名特征不支持物理或因果含义推断。

## Project Structure

- `data/`：原始数据与预处理数据位置。
- `figures/`：Notebook 草稿图及 `figures/paper/` 冻结论文图。
- `models/`：冻结模型与融合配置。
- `notebooks/`：主实验 Notebook。
- `paper/`：中英文论文及共享图注、表注和文献池。
- `results/`：实验输出与论文专用冻结 CSV。
- `scripts/`：论文图生成和辅助检查脚本。
- `skill/`：项目工作流 Skill 及历史版本。
- `src/`：可复用 Python 模块。

## Reproducibility

环境定义见 `environment.yml`，主要实验见 `notebooks/01_experiment.ipynb`。当前实验结果已经冻结；论文写作和绘图应直接引用 `results/` 下的正式 CSV，不应重新训练模型或重算指标。

## Papers

- 中文稿：`paper/zju_zh/main.pdf`，目标版式为《浙江大学学报（工学版）》。
- 英文稿：`paper/acm_mm/main.pdf`，ACM Multimedia / ACM MM working draft。

两篇稿件共享同一套冻结实验结果，但不是逐句翻译关系。

## Figures

- 英文正式图：`figures/paper/fig1_*.pdf` 至 `fig6_*.pdf`。
- 中文正式图：文件名以 `_zh.pdf` 结尾。
- PDF 为正式矢量输出，SVG 为可编辑矢量版本，PNG 为 300 dpi 预览。

## Limitations

- 特征语义匿名，无法作可靠物理解释。
- 数据的严格时间语义未完全确认。
- 融合收益仅约 0.19%。
- 未开展重复独立试验或统计显著性分析。
- SHAP 仅解释 Best XGBoost。
- 预测残差仍存在尾部和少量较大误差。
- 无标签测试集无法计算真实泛化指标。

## Repository Status

这是已冻结的实验研究项目，不宣称 SOTA。仓库用于成果归档、复核与投稿材料维护。
