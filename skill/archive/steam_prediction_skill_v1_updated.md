# Industrial Steam Prediction Skill v1

## 1. Skill 目标

本 Skill 用于规范执行工业蒸汽量预测项目的完整机器学习流程。

目标包括：

- 读取训练集与测试集；

- 检查数据质量；

- 进行基础数据分析；

- 构建并比较多个回归模型；

- 调优 Ridge 与 XGBoost；

- 进行模型融合；

- 使用 SHAP 解释模型；

- 分析预测误差；

- 训练最终模型并生成测试集预测；

- 保存实验结果、图像和模型文件；

- 检查实验结果是否完整、可复现。

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

---

## 3. 执行流程

### Step 1：检查运行环境

确认当前 Python 环境为：

```text

steam-prediction

```

检查命令：

```powershell

conda activate steam-prediction

python --version

```

完成标准：

- Python 可以正常运行；

- 项目依赖可以正常导入。

---

### Step 2：读取数据

使用：

```python

from src.data_utils import load_steam_data, split_features_target

```

读取训练集和测试集，并拆分：

```text

X

y

X_test

```

完成标准：

```text

train_data: (2888, 39)

test_data:  (1925, 38)

X:          (2888, 38)

y:          (2888,)

X_test:     (1925, 38)

```

---

### Step 3：数据质量检查

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

- 优先判断异常值是否可能属于真实工业过程状态。

完成标准：

- 数据质量检查结果能够解释；

- 明确是否需要缺失值处理、异常值处理或额外清洗。

---

### Step 4：建立基线模型

使用 Ridge Regression 作为主要线性基线。

模型结构：

```text

StandardScaler

+

Ridge

```

交叉验证：

```text

TimeSeriesSplit(n_splits=5)

```

评价指标：

- MSE

- RMSE

- MAE

- R²

完成标准：

- 得到每折结果；

- 得到平均指标；

- 保存结果到 `results/`。

---

### Step 5：特征处理方法比较

比较：

- 全部 38 个原始特征；

- SelectKBest；

- PCA。

比较时保持模型一致。

完成标准：

- 使用相同 Ridge 模型进行公平比较；

- 根据 MSE、RMSE、MAE 和 R² 判断是否需要特征压缩；

- 记录最终采用的特征方案。

---

### Step 6：多模型比较

至少比较：

- Ridge

- Random Forest

- GBDT

- XGBoost

- LightGBM

完成标准：

- 使用统一交叉验证策略；

- 使用统一评价指标；

- 生成模型性能对比表；

- 不只根据单一指标选择模型。

---

### Step 7：模型调参

重点调优：

#### Ridge

主要参数：

```text

alpha

```

当前最优值：

```text

alpha = 5.0

```

#### XGBoost

当前较优参数：

```text

n_estimators = 300

learning_rate = 0.05

max_depth = 2

subsample = 0.8

colsample_bytree = 1.0

```

完成标准：

- 保存调参结果；

- 保存最优参数；

- 使用最优参数重新进行交叉验证。

---

### Step 8：模型融合

当前融合模型：

```text

Ridge + XGBoost

```

默认权重：

```text

Ridge   = 0.7

XGBoost = 0.3

```

调用：

```python

from src.fusion import weighted_blend

```

融合权重应使用独立验证数据选择，避免在同一批数据上既选择权重又评价最终性能。

完成标准：

- 保存权重搜索结果；

- 在独立验证部分比较 Ridge、XGBoost 与融合模型；

- 只有独立验证结果更优时，才把融合模型描述为有效改进。

---

### Step 9：模型解释

对当前最佳树模型进行 SHAP 分析。

包括：

- SHAP Summary Plot；

- SHAP Feature Importance；

- 关键特征 Dependence Plot。

注意：

> SHAP 当前解释的是 XGBoost 模型，而不是 Ridge + XGBoost 加权融合模型。

完成标准：

- 明确解释对象；

- 保存 SHAP 数值结果；

- 保存解释图像。

---

### Step 10：误差分析

对最终验证预测进行分析：

- 真实值 vs 预测值；

- 残差分布；

- 残差与预测值关系；

- 最大绝对误差样本。

完成标准：

- 至少保存一张真实值与预测值图；

- 至少保存一张残差图；

- 保存高误差样本表。

---

### Step 11：验证策略敏感性分析

比较：

```text

TimeSeriesSplit

```

与：

```text

KFold(n_splits=5, shuffle=True, random_state=42)

```

保持：

- 数据不变；

- 模型不变；

- 超参数不变；

- 指标不变。

仅改变验证策略。

完成标准：

- 保存 `validation_strategy_comparison.csv`；

- 检查模型性能是否明显依赖验证策略；

- 不根据结果更好就直接判断某种验证策略一定正确。

---

### Step 12：训练最终模型

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

- 预测长度必须等于测试集样本数；

- 不允许出现 NaN；

- 保存最终测试预测。

---

## 4. 输出

### 4.1 实验结果

保存位置：

```text

results/

```

包括：

- 模型比较结果；

- 调参结果；

- 融合结果；

- SHAP 特征重要性；

- 误差分析；

- 验证策略对比；

- 最终测试预测。

### 4.2 图像

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

### 4.3 模型

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

## 5. 完成检查

完整实验结束后检查：

- [ ] Python 环境正确；

- [ ] 数据维度正确；

- [ ] 无异常读取错误；

- [ ] 基线模型完成；

- [ ] 多模型比较完成；

- [ ] Ridge 调参完成；

- [ ] XGBoost 调参完成；

- [ ] 模型融合完成；

- [ ] SHAP 分析完成；

- [ ] 误差分析完成；

- [ ] 验证策略敏感性分析完成；

- [ ] 最终预测生成；

- [ ] 结果文件保存；

- [ ] 图像文件保存；

- [ ] 模型文件保存；

- [ ] Notebook 保存成功且文件大小正常；

- [ ] Git 工作区状态已检查。

---

## 6. v1 已知风险

当前 v1 存在以下需要继续验证的问题：

1. 数据来自分钟级工业过程，但当前文件行顺序是否严格对应时间顺序尚未被明确确认；

2. 因此 `TimeSeriesSplit` 是否是唯一合理验证策略仍需进一步核查；

3. KFold 与 TimeSeriesSplit 得到的性能存在差异，说明结果对验证方式具有一定敏感性；

4. 当前不同实验部分存在 RMSE 汇总方式不一致的问题：

   ```text
   sqrt(mean(fold MSE))
   ```

   与：

   ```text
   mean(sqrt(fold MSE))
   ```

   后续需要统一评价指标计算方式，避免不同实验部分出现数值不一致；

5. 加权融合相对于 Ridge 的独立验证改进幅度较小，需要避免夸大；

6. 当前 SHAP 解释对象是 XGBoost，而不是 Ridge + XGBoost 加权融合模型；

7. 当前 Skill 尚未明确区分“功能测试”和“正式实验评估”。

   功能测试主要用于：

   - 检查代码是否能够运行；
   - 检查模型能否正常训练；
   - 检查预测维度；
   - 检查 NaN；
   - 检查不同模块是否能够连接。

   正式实验评估则用于：

   - 比较模型性能；
   - 选择模型；
   - 选择融合权重；
   - 生成论文实验结果。

   两者必须明确区分，功能测试产生的临时性能结果不能直接作为正式实验结论；

8. 最终测试预测文件是否完全符合原始竞赛官方提交格式，需要在正式提交前再次核查。

---

## 7. v1 后续测试目标

下一步需要实际按照本 Skill 执行一次，并记录：

- 哪些步骤描述不够清楚；
- 哪些输入或输出没有说明；
- 哪些步骤仍依赖 Notebook 中隐含变量；
- 哪些结果不能通过独立脚本复现；
- 哪些步骤容易产生误操作；
- 是否存在评价指标定义不一致的问题；
- 是否明确区分了“功能测试”和“正式实验评估”；
- 是否存在使用临时数据划分结果替代正式实验结果的风险；
- 是否所有正式实验都采用统一的数据划分策略和评价指标。

根据实际执行问题修改为 Skill v2。

在 Skill v2 中，每个实验步骤应尽量明确标注：

```text
测试类型：功能测试
```

或：

```text
测试类型：正式实验评估
```

从而避免两类测试用途混淆。

---

## 8. v1 问题修复状态

### 问题 1：RMSE 计算方式不一致

已在 Skill v2 中完成修复。

处理结果：

- Notebook 第 8.2 节已统一采用 `mean(sqrt(fold MSE))`；
- `TimeSeriesSplit` RMSE 更新为 `0.359262`；
- `KFold` RMSE 更新为 `0.335365`；
- `results/validation_strategy_comparison.csv` 已重新生成；
- 当前验证策略对比与项目主实验的 RMSE 定义保持一致。

状态：

```text
[已修复]

---

## 8. v1 问题修复状态

### 问题 1：RMSE 计算方式不一致

已在 Skill v2 中完成修复。

处理结果：

- Notebook 第 8.2 节已统一采用 `mean(sqrt(fold MSE))`；
- `TimeSeriesSplit` RMSE 更新为 `0.359262`；
- `KFold` RMSE 更新为 `0.335365`；
- `results/validation_strategy_comparison.csv` 已重新生成；
- 当前验证策略对比与项目主实验的 RMSE 定义保持一致。

状态：

```text
[已修复]
```

### 问题 2：功能测试与正式实验评估没有明确区分

已在 Skill v2 中完成修复。

处理结果：

- v2 新增“测试类型定义”；
- 明确区分“功能测试”和“正式实验评估”；
- 每个关键步骤均标注测试类型；
- 功能测试结果不得用于正式模型性能结论；
- Step 12 拆分为“功能测试”和“正式实验输出”两个阶段。

状态：

```text
[已修复]
```
