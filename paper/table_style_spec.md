# Table Style Specification

本文件规定中英文论文表格的共享数据与排版边界。表中数值必须来自 `results/` 下冻结 CSV，不得在论文排版阶段重新计算。

## Shared invariants

- 中英文稿使用相同数据、模型排序、指标定义和小数精度。
- 仅翻译表题、列名和必要注释，不改变实验口径。
- 不将折间标准差描述为置信区间，不作统计显著性推断。
- 5 折 `TimeSeriesSplit` 主评估与独立融合验证集结果不得直接横向比较。
- Weighted Blend 相对 Best Ridge 的约 0.19% 改善属于边际数值改善。
- SHAP 表述仅解释 Best XGBoost。

## Chinese manuscript

- 采用《浙江大学学报（工学版）》风格的三线表。
- 中文表题与英文表题内容一一对应，表题在 Word/LaTeX 正文中排版。
- 表注仅保留理解评估口径所必需的信息。
- 中文使用宋体；英文、数字和模型名称使用 Times New Roman。

## ACM manuscript

- 使用 ACM 模板原生 `table` / `table*`、`booktabs` 风格。
- Caption 保持简洁、自明，避免重复正文分析。
- 双栏表仅在单栏宽度无法保证可读性时使用。

## Numeric presentation

- MSE、RMSE、MAE 和 R² 通常保留 4 位小数；正文中已冻结的简写精度保持不变。
- 模型名称保持一致：Best Ridge、Best XGBoost、Weighted Blend、Stacking。
- 最优值可使用克制的粗体，但不通过颜色或装饰暗示显著性。
