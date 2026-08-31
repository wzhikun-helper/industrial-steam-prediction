# Scripts

## Purpose

本目录包含结果整理、论文图生成和辅助检查脚本。论文写作阶段不应重算或改写冻结实验结果。

## Figure scripts

英文图（ACM MM）：`figures/fig1_target_distribution.py` 至 `figures/fig6_prediction_diagnostics.py`。

中文图（《浙江大学学报（工学版）》）：对应的 `figures/*_zh.py`。

所有论文图均从 `results/paper_fig*.csv` 冻结数据动态生成。

## Shared style and checks

- `figures/_style.py`：项目局部统一绘图样式。
- `figures/critique.py`：项目局部 mechanical check，不是 Icarus 官方 full quality gate。
