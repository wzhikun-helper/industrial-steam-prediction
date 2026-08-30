# Industrial Steam Prediction Skill v2

## 1. Skill 目标

本 Skill 用于规范执行工业蒸汽量预测项目的完整机器学习流程，并在 v1 的基础上进一步统一评价指标、区分功能测试与正式实验评估、明确输入输出和完成标准。

目标包括：

- 读取训练集与测试集；
- 检查数据质量；
- 进行基础数据分析；
- 构建并比较多个回归模型；
- 调优 Ridge 与 XGBoost；
- 进行模型融合；
- 使用 SHAP 解释模型；
- 分析预测误差；
- 比较不同验证策略；
- 训练最终模型并生成测试集预测；
- 保存实验结果、图像和模型文件；
- 检查实验结果是否完整、可复现；
- 明确区分功能测试与正式实验评估；
- 统一交叉验证 RMSE 的计算方式。

---

## 2. 输入

### 2.1 原始数据

训练集：

```text
data/raw/zhengqi_train.txt
```

测试集：

```text
data/raw/zhengqi_test.txt
```

训练集包含：

- 38 个特征：`V0` ~ `V37`
- 1 个目标变量：`target`

测试集仅包含 38 个特征。

### 2.2 Python 环境

使用 Conda 环境：

```text
steam-prediction
```

主要依赖：

- numpy
- pandas
- matplotlib
- seaborn
- scikit-learn
- xgboost
- lightgbm
- shap
- joblib
- jupyter

### 2.3 项目模块

主要复用模块：

```text
src/data_utils.py
src/evaluation.py
src/models.py
src/fusion.py
```

---

## 3. 测试类型定义

v2 明确区分两类测试。

### 3.1 功能测试

测试类型：

```text
功能测试
```

目的：

- 检查代码是否能够运行；
- 检查模块能否正常导入；
- 检查模型能否训练和预测；
- 检查输出维度是否正确；
- 检查预测结果是否存在 NaN；
- 检查不同模块能否正常连接。

功能测试可以采用简化的数据划分方式。

但是：

> 功能测试产生的性能结果不得直接作为正式论文实验结果。

### 3.2 正式实验评估

测试类型：

```text
正式实验评估
```

目的：

- 比较模型性能；
- 选择模型；
- 选择超参数；
- 选择融合权重；
- 生成论文中的实验结果。

正式实验必须：

- 使用预先规定的数据划分策略；
- 使用统一的评价指标；
- 保持模型比较条件一致；
- 保存可复核的结果文件。

---

## 4. 评价指标统一规则

评价指标包括：

- MSE
- RMSE
- MAE
- R²

### 4.1 单次验证或独立测试集

对于单次预测结果：

```text
RMSE = sqrt(MSE)
```

### 4.2 K 折交叉验证

对于 K 折交叉验证，统一采用：

```text
mean(sqrt(fold MSE))
```

即：

1. 先计算每一折的 RMSE；
2. 再对各折 RMSE 求平均。

禁止在同一项目不同位置混用：

```text
sqrt(mean(fold MSE))
```

与：

```text
mean(sqrt(fold MSE))
```

项目中交叉验证结果统一使用 `src/evaluation.py` 中的 `summarize_cv_scores()` 汇总。

---

## 5. 执行流程

### Step 1：检查运行环境

测试类型：

```text
功能测试
```

执行：

```powershell
conda activate steam-prediction
python --version
python -c "import numpy, pandas, sklearn, xgboost, lightgbm, shap, joblib; print('environment ok')"
```

完成标准：

- 当前环境为 `steam-prediction`；
- Python 可以正常运行；
- 核心依赖可以正常导入；
- 输出 `environment ok`。

---

### Step 2：读取数据与拆分

测试类型：

```text
功能测试
```

使用：

```python
from src.data_utils import load_steam_data, split_features_target
```

完成标准：

```text
train_data: (2888, 39)
test_data:  (1925, 38)
X:          (2888, 38)
y:          (2888,)
X_test:     (1925, 38)
```

如维度不一致，应立即停止后续正式实验并检查：

- 数据文件是否正确；
- 分隔符是否正确；
- `target` 是否存在；
- 是否误改原始数据。

---

### Step 3：数据质量检查

测试类型：

```text
正式实验评估
```

检查：

- 缺失值；
- 重复值；
- 无穷值；
- 数据类型；
- 描述性统计；
- target 分布；
- IQR 异常值；
- 特征与 target 相关性；
- 高相关特征之间的相关性。

原则：

- 不因存在异常值而直接删除样本；
- 优先判断异常值是否可能属于真实工业过程状态；
- 数据处理决策必须记录原因。

完成标准：

- 数据质量问题有明确结论；
- 明确是否需要额外清洗；
- 相关统计结果已保存至 `results/`；
- 关键图像已保存至 `figures/`。

---

### Step 4：建立 Ridge 基线

测试类型：

```text
正式实验评估
```

模型：

```text
StandardScaler
+
Ridge
```

默认验证策略：

```text
TimeSeriesSplit(n_splits=5)
```

评价指标：

- MSE
- RMSE
- MAE
- R²

统一通过：

```python
from src.evaluation import summarize_cv_scores
```

进行汇总。

完成标准：

- 得到每折结果；
- 得到平均指标；
- RMSE 采用 `mean(sqrt(fold MSE))`；
- 保存结果到 `results/`。

---

### Step 5：特征处理方法比较

测试类型：

```text
正式实验评估
```

比较：

- 全部 38 个原始特征；
- SelectKBest；
- PCA。

控制变量：

- 模型保持一致；
- 验证策略保持一致；
- 评价指标保持一致。

完成标准：

- 使用相同 Ridge 模型公平比较；
- 根据 MSE、RMSE、MAE 和 R² 判断特征处理效果；
- 保存比较结果；
- 记录最终特征方案和选择理由。

---

### Step 6：多模型比较

测试类型：

```text
正式实验评估
```

至少比较：

- Ridge
- Random Forest
- GBDT
- XGBoost
- LightGBM

控制变量：

- 使用统一数据；
- 使用统一交叉验证策略；
- 使用统一评价指标；
- 使用统一 RMSE 汇总定义。

完成标准：

- 生成模型性能对比表；
- 不只根据单一指标选择模型；
- 保存各模型每折结果和平均结果。

---

### Step 7：模型调参

测试类型：

```text
正式实验评估
```

#### Ridge

主要参数：

```text
alpha
```

当前实验最优值：

```text
alpha = 5.0
```

#### XGBoost

当前实验较优参数：

```text
n_estimators = 300
learning_rate = 0.05
max_depth = 2
subsample = 0.8
colsample_bytree = 1.0
```

完成标准：

- 保存完整调参搜索结果；
- 保存最优参数；
- 使用最优参数重新进行交叉验证；
- 不使用测试集参与调参。

---

### Step 8：模型融合

测试类型：

```text
正式实验评估
```

融合模型：

```text
Ridge + XGBoost
```

当前权重：

```text
Ridge   = 0.7
XGBoost = 0.3
```

调用：

```python
from src.fusion import weighted_blend
```

原则：

- 融合权重必须使用训练阶段的独立验证数据选择；
- 不能在同一批数据上既选择权重又评价最终性能；
- 融合模型必须和 Ridge、XGBoost 在相同验证样本上比较；
- 如果改进很小，应如实描述为“小幅改进”。

完成标准：

- 保存权重搜索结果；
- 保存独立验证比较结果；
- 明确最终选择融合模型还是单模型；
- 不夸大提升幅度。

---

### Step 9：模型解释

测试类型：

```text
正式实验评估
```

对当前最佳树模型进行 SHAP 分析。

包括：

- SHAP Summary Plot；
- SHAP Feature Importance；
- 关键特征 Dependence Plot。

当前解释对象：

```text
Best XGBoost
```

注意：

> 当前 SHAP 结果不能描述为对 Ridge + XGBoost 加权融合模型的直接解释。

完成标准：

- 明确解释对象；
- 保存 SHAP 数值结果；
- 保存解释图像；
- 论文图注中标明所解释的模型。

---

### Step 10：误差分析

测试类型：

```text
正式实验评估
```

分析：

- 真实值 vs 预测值；
- 残差分布；
- 残差与预测值关系；
- 最大绝对误差样本。

完成标准：

- 保存真实值与预测值图；
- 保存残差图；
- 保存高误差样本表；
- 分析模型在哪些样本区域误差较大。

---

### Step 11：验证策略敏感性分析

测试类型：

```text
正式实验评估
```

比较：

```text
TimeSeriesSplit(n_splits=5)
```

与：

```text
KFold(n_splits=5, shuffle=True, random_state=42)
```

控制变量：

- 数据不变；
- 模型不变；
- 超参数不变；
- 评价指标不变；
- RMSE 计算方式不变。

统一使用：

```python
summarize_cv_scores()
```

完成标准：

- 保存 `validation_strategy_comparison.csv`；
- 两种验证策略的 RMSE 均使用 `mean(sqrt(fold MSE))`；
- 检查结果是否对验证策略敏感；
- 不因为 KFold 指标更好就直接判断 KFold 一定正确；
- 论文中明确说明数据顺序语义尚未被完全确认。

---

### Step 12：最终模型训练与测试集预测

分为两个阶段。

#### 12.1 功能测试

测试类型：

```text
功能测试
```

检查：

- Ridge 能否训练；
- XGBoost 能否训练；
- 融合函数能否运行；
- 测试集预测长度是否为 1925；
- 是否存在 NaN。

功能测试结果不得作为模型性能结论。

#### 12.2 最终预测生成

测试类型：

```text
正式实验输出
```

使用完整训练集重新训练：

- Best Ridge；
- Best XGBoost。

生成：

```text
ridge_prediction
xgboost_prediction
weighted_prediction
```

完成标准：

- 每组预测长度为 1925；
- 不存在 NaN；
- 保存最终预测文件；
- 保存最终模型；
- 保存融合配置；
- 在称其为“官方提交文件”前核查竞赛提交格式。

---

## 6. 输出

### 6.1 实验结果

保存位置：

```text
results/
```

至少包括：

- 数据统计结果；
- 特征方法比较；
- 模型比较结果；
- 调参结果；
- 融合结果；
- SHAP 特征重要性；
- 误差分析；
- 验证策略对比；
- 最终测试预测。

### 6.2 图像

保存位置：

```text
figures/
```

包括：

- target 分布；
- 模型性能比较；
- SHAP 图；
- 残差图；
- 真实值与预测值对比图。

正式论文绘图阶段应统一：

- 字体；
- 字号；
- 坐标轴；
- 图例；
- 分辨率；
- 输出尺寸；
- 中英文论文图注格式。

### 6.3 模型

保存位置：

```text
models/
```

包括：

```text
best_ridge_model.joblib
best_xgboost_model.joblib
weighted_fusion_config.joblib
```

---

## 7. v2 完成检查

完整实验结束后检查：

- [ ] Conda 环境为 `steam-prediction`
- [ ] 核心依赖可以正常导入
- [ ] 数据维度正确
- [ ] 无异常读取错误
- [ ] 数据质量检查完成
- [ ] Ridge 基线完成
- [ ] 特征处理比较完成
- [ ] 多模型比较完成
- [ ] Ridge 调参完成
- [ ] XGBoost 调参完成
- [ ] 模型融合完成
- [ ] SHAP 分析完成
- [ ] 误差分析完成
- [ ] 验证策略敏感性分析完成
- [ ] 所有交叉验证 RMSE 均采用统一定义
- [ ] 功能测试与正式实验结果已明确区分
- [ ] 最终预测长度为 1925
- [ ] 最终预测不存在 NaN
- [ ] 结果文件保存完整
- [ ] 图像文件保存完整
- [ ] 模型文件保存完整
- [ ] Notebook 保存成功且文件大小正常
- [ ] Git 工作区状态已检查
- [ ] 正式论文引用的结果可追溯到对应 CSV / 图像 / 模型
- [ ] 最终提交格式在正式提交前已核查

---

## 8. v1 → v2 修改说明

### 修改 1：统一 RMSE 计算方式

v1 实际测试发现，Notebook 验证策略对比部分与主实验使用了不同的 RMSE 汇总方式。

v2 统一规定交叉验证 RMSE 为：

```text
mean(sqrt(fold MSE))
```

并要求正式实验统一通过 `summarize_cv_scores()` 汇总。

### 修改 2：区分功能测试与正式实验评估

v1 中没有明确区分代码功能测试和正式性能评估。

v2 增加：

```text
测试类型：功能测试
```

和：

```text
测试类型：正式实验评估
```

功能测试只验证代码和数据流程是否正常，不用于论文性能结论。

### 修改 3：强化控制变量

模型比较、特征方法比较和验证策略比较必须明确保持除待比较因素之外的其他条件一致。

### 修改 4：明确 SHAP 解释对象

SHAP 当前解释对象为 Best XGBoost，不直接解释加权融合模型。

### 修改 5：强化融合评估约束

融合权重选择和最终评价不能使用同一批数据，且融合提升较小时必须谨慎表述。

### 修改 6：完善最终输出检查

最终预测必须检查：

- 样本数；
- NaN；
- 模型文件；
- 融合配置；
- 提交格式。

---

## 9. v2 后续执行目标

下一步按照 v2 重新运行关键步骤，并检查：

- RMSE 是否已完全统一；
- Notebook 第 8 章结果是否需要修正；
- 正式实验和功能测试是否能够清晰分离；
- 所有论文结果是否都能追溯到保存文件；
- 是否仍存在依赖 Notebook 隐含变量的步骤；
- 最终提交文件格式是否符合竞赛要求。

完成 v2 测试后，再决定是否需要生成 Skill v3。

---

## 10. v2 当前验证状态

以下结果来自本项目已经实际执行的关键验证。

### 10.1 运行环境

核心依赖导入结果：

```text
environment ok
```

状态：

```text
[已通过]
```

### 10.2 数据读取与拆分

```text
train_data: (2888, 39)
test_data:  (1925, 38)
X:          (2888, 38)
y:          (2888,)
X_test:     (1925, 38)
```

状态：

```text
[已通过]
```

### 10.3 Best Ridge + TimeSeriesSplit

统一采用 `mean(sqrt(fold MSE))` 后：

```text
MSE  = 0.130369
RMSE = 0.359262
MAE  = 0.263933
R²   = 0.852496
```

状态：

```text
[已通过]
```

### 10.4 验证策略敏感性分析

统一 RMSE 定义后的结果：

| Validation Strategy | MSE | RMSE | MAE | R² |
|---|---:|---:|---:|---:|
| TimeSeriesSplit | 0.130369 | 0.359262 | 0.263933 | 0.852496 |
| KFold | 0.112940 | 0.335365 | 0.244574 | 0.882662 |

`results/validation_strategy_comparison.csv` 已重新生成。

状态：

```text
[已通过]
```

### 10.5 模型融合功能测试

实际结果：

```text
ridge: (578,)
xgb:   (578,)
blend: (578,)
nan:   0
```

该测试仅用于确认模块链路可运行，不作为正式论文性能结果。

状态：

```text
[已通过]
```

### 10.6 最终训练与测试集预测功能测试

实际结果：

```text
ridge: (1925,) nan=0
xgb:   (1925,) nan=0
blend: (1925,) nan=0
```

状态：

```text
[已通过]
```

### 10.7 尚未完成的核查

- 原始数据文件行顺序是否具有严格时间语义；
- 竞赛官方提交文件格式；
- 论文图表的统一出版级样式；
- 论文中所有结果与 CSV、图像和模型文件的逐项追溯。
