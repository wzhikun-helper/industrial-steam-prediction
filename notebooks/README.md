# Notebooks Directory

本目录用于保存工业蒸汽量预测项目的 Jupyter Notebook 实验文件。

## 主要文件

### `01_experiment.ipynb`

- 项目的主实验 Notebook。
- 包含从数据读取到最终测试集预测的完整机器学习流程。

## Notebook 主要内容

`01_experiment.ipynb` 主要包括以下部分：

1. 项目背景与环境说明；
2. 数据读取与原始数据副本保留；
3. 数据质量检查；
4. 目标变量与特征分布分析；
5. 异常值和相关性分析；
6. Ridge 基线模型；
7. KBest 和 PCA 特征处理实验；
8. Random Forest、GBDT、XGBoost、LightGBM 多模型比较；
9. Ridge 与 XGBoost 参数优化；
10. 加权融合和 Stacking 融合；
11. SHAP 特征重要性与贡献方向分析；
12. 最终模型真实值与预测值分析；
13. 残差与大误差样本分析；
14. 使用全部训练集重新训练最终模型；
15. 官方测试集预测与结果保存。

## 使用说明

建议在项目根目录启动 Jupyter。

使用 JupyterLab：

```powershell
jupyter lab
```

或者使用 Jupyter Notebook：

```powershell
jupyter notebook
```

然后打开：

```text
notebooks/01_experiment.ipynb
```

## Python 环境

Notebook 使用的 Python 内核为：

```text
Python (steam-prediction)
```

建议运行环境：

```text
Python 3.11
Conda environment: steam-prediction
```

## 实验原则

- 尽量按照 Notebook 单元格顺序执行；
- 重要实验结果同时显示并保存到 `results/`；
- 重要图像保存到 `figures/`；
- 最终模型保存到 `models/`；
- 特征处理尽量通过 Pipeline 完成，降低数据泄漏风险；
- 当前 Notebook 中的图片主要用于实验分析，正式论文图片将在后续科研作图阶段重新整理。