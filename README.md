# Industrial Steam Prediction

工业蒸汽量预测机器学习项目。

本项目基于天池工业蒸汽量预测数据集，完成了从数据探索、特征分析、模型训练、参数优化、模型融合、SHAP 可解释性分析，到最终测试集预测的完整机器学习流程。

## 项目目标

根据 38 个匿名工业特征 `V0`～`V37` 预测目标变量 `target`，并建立一套：

- 可复现；
- 可比较；
- 可解释；
- 可用于论文整理。

的机器学习实验流程。

## 项目结构

```text
industrial-steam-prediction/
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── notebooks/
│   ├── 01_experiment.ipynb
│   └── README.md
│
├── src/
│   └── README.md
│
├── figures/
│   └── README.md
│
├── results/
│   └── README.md
│
├── models/
│   └── README.md
│
├── paper/
│   └── README.md
│
├── skill/
│   └── README.md
│
└── README.md
```

## 数据集

训练集包含：

- 2888 个样本；
- 38 个匿名特征 `V0`～`V37`；
- 1 个目标变量 `target`。

测试集包含：

- 1925 个样本；
- 38 个输入特征；
- 不包含目标变量。

原始数据保存在：

```text
data/raw/
```

## 实验流程

主要实验流程包括：

1. 数据读取与质量检查；
2. 描述性统计与目标变量分布分析；
3. IQR 异常值分析；
4. Pearson 相关性分析；
5. KBest 特征筛选；
6. PCA 降维；
7. Ridge、Random Forest、GBDT、XGBoost、LightGBM 模型比较；
8. Ridge 与 XGBoost 参数优化；
9. Ridge + XGBoost 加权融合；
10. Stacking 融合；
11. SHAP 特征重要性和贡献方向分析；
12. 真实值与预测值分析；
13. 残差与大误差样本分析；
14. 最终模型训练；
15. 官方测试集预测与模型保存。

## 主要实验结果

基础模型中，Ridge 表现最好。

### 优化后的 Ridge

- `alpha = 5`
- 平均 MSE：`0.130369`
- 平均 RMSE：`0.359262`
- 平均 MAE：`0.263933`
- 平均 R²：`0.852496`

### 优化后的 XGBoost

- 平均 MSE：`0.149834`
- 平均 RMSE：`0.385839`
- 平均 MAE：`0.288822`
- 平均 R²：`0.826074`

### 最终加权融合方案

```text
0.7 × Ridge + 0.3 × XGBoost
```

在独立二层测试集上，加权融合略优于 Best Ridge。

## SHAP 可解释性结果

SHAP 分析表明，模型中较重要的特征包括：

- V0
- V1
- V2
- V3
- V10
- V27
- V8
- V37

其中：

- V0 和 V1 整体表现为明显正向贡献；
- V37 整体表现为负向贡献；
- V0 是当前 XGBoost 模型中最重要的特征。

## 运行环境

推荐环境：

```text
Python 3.11
Conda environment: steam-prediction
```

主要依赖：

```text
numpy
pandas
matplotlib
seaborn
scikit-learn
xgboost
lightgbm
shap
joblib
jupyter
```

## 启动 Notebook

激活环境：

```powershell
conda activate steam-prediction
```

进入项目目录：

```powershell
cd D:\Projects\industrial-steam-prediction
```

启动 Jupyter：

```powershell
jupyter lab
```

然后打开：

```text
notebooks/01_experiment.ipynb
```

## 结果文件

实验指标和预测结果保存在：

```text
results/
```

实验图保存在：

```text
figures/
```

训练模型保存在：

```text
models/
```

## 论文计划

中文论文参考《浙江大学学报（工学版）》近期相关文章的结构、行文方式和版式规范。

英文论文使用 ACM MM 官方模板进行整理。

两篇论文使用同一套真实实验结果，不人为修改实验指标。

## Skill

项目后续将把完整实验流程整理为可复用 Skill，并进行：

```text
v1 → 实际执行 → 问题记录 → v2 → 版本比较
```

以验证工作流的完整性和可复现性。