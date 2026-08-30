# Skill v1 实际测试问题记录

## 测试目的

按照 `steam_prediction_skill_v1.md` 的流程进行最小可复现测试，记录执行过程中发现的问题，为后续 Skill v2 修改提供依据。

---

## 问题 1：RMSE 计算方式不一致

### 发现位置

验证策略敏感性分析：

- `TimeSeriesSplit`

- `KFold`

### 发现现象

Notebook 第 8 章中，KFold 的 RMSE 为：

```text

0.336066

```

使用 `src/evaluation.py` 中的 `summarize_cv_scores()` 后，KFold 的 RMSE 为：

```text

0.335365

```

两者的 MSE、MAE 和 R² 一致，只有 RMSE 存在差异。

### 原因

存在两种 RMSE 汇总方式。

方式 1：

```text

sqrt(mean(fold MSE))

```

方式 2：

```text

mean(sqrt(fold MSE))

```

Notebook 第 8 章采用方式 1，而前面的主要交叉验证实验和 `src/evaluation.py` 采用方式 2。

因此，两种结果虽然都来自相同的各折 MSE，但由于计算顺序不同，最终 RMSE 数值略有差异。

### 处理决定

后续统一采用：

```text

mean(sqrt(fold MSE))

```

即：

1. 先计算每一折的 RMSE；

2. 再对各折 RMSE 求平均。

这样与当前项目主要实验的评价方式保持一致。

### 后续修改

Skill v2 需要明确规定交叉验证 RMSE 的计算方式，避免不同实验部分出现不一致结果。

Notebook 第 8 章中的验证策略对比结果也需要后续统一修正。

---

## 问题 2：功能测试与正式实验评估没有明确区分

### 发现位置

模型融合功能测试与最终预测功能测试。

### 发现现象

为了验证 `src/data_utils.py`、`src/models.py` 和 `src/fusion.py` 是否能够协同运行，测试中使用了临时随机划分，并检查了 Ridge、XGBoost 与加权融合预测的输出维度和 NaN 情况。

该测试能够确认代码链路可运行，但这种临时划分并不是项目正式论文实验中的性能评估方案。

### 风险

如果 Skill 没有明确区分“功能测试”和“正式实验评估”，容易：

1. 将临时测试性能误当作正式实验结果；
2. 使用不同数据划分方式直接比较模型；
3. 造成 Notebook、脚本和论文实验设置不一致。

### 处理决定

Skill v2 中明确区分：

- **功能测试**：只检查代码、维度、NaN 和模块连接；
- **正式实验评估**：用于模型比较、调参、融合权重选择和论文结果。

功能测试结果不得直接作为论文性能结论。

### 修复状态

已在 Skill v2 中完成修复。

状态：

```text
[已修复]
```

---

## 修复汇总

### 问题 1：RMSE 计算方式不一致

已完成修复：

- Notebook 第 8.2 节已统一采用 `mean(sqrt(fold MSE))`；
- `TimeSeriesSplit` RMSE 更新为 `0.359262`；
- `KFold` RMSE 更新为 `0.335365`；
- `results/validation_strategy_comparison.csv` 已重新生成；
- 当前验证策略对比与项目主实验的 RMSE 定义保持一致。

状态：

```text
[已修复]
```

### 问题 2：功能测试与正式实验评估未区分

已完成修复：

- Skill v2 新增“测试类型定义”；
- 关键步骤均标明“功能测试”或“正式实验评估”；
- Step 12 被拆分为“功能测试”和“正式实验输出”两个阶段；
- 功能测试结果明确禁止直接用于论文性能结论。

状态：

```text
[已修复]
```
