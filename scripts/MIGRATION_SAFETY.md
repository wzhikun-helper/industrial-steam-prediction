# 安全迁移与冻结来源

这是第20步建立边界时的历史记录；文末“尚无统一入口”描述当时状态。第21–33步的当前入口、已完成能力和发布验收请以根README及docs/FINAL_PROJECT_ACCEPTANCE.md为准，不据此重跑历史Notebook。

## 输出约定

现有 results/、models/、figures/paper/ 和两套论文目录默认按只读处理；这是项目执行约定，尚未施加操作系统 ACL。现有绘图脚本和 Notebook 仍能覆盖文件，执行前必须检查写入目标。

后续实验只允许写入 staging/<唯一运行ID>/ 或 reproduction/<唯一运行ID>/。入口须先检查目标不存在，再以拒绝覆盖的方式创建目录（exist_ok=False）；文件写入也须拒绝覆盖。不得删除旧目录以通过检查，不得用新入口直接覆盖冻结文件。正式发布结果须另行明确授权。

不得为迁移验收运行旧 Notebook Run All、删除旧结果或重存已冻结模型。当前阶段不迁移全部 Notebook。

## 已核对冻结事实

以下数字从现有 CSV 读取核对，未重新训练：

| 事实 | 数值与来源 |
|---|---|
| Best Ridge MSE | 0.13036913621734353；results/final_model_comparison.csv |
| Ridge alpha | 5.0；results/ridge_alpha_tuning.csv，rank_test_score=1 |
| Best XGBoost MSE | 0.14983440587129646；results/final_model_comparison.csv |
| TimeSeriesSplit MSE | 0.13036913621734353；results/validation_strategy_comparison.csv |
| KFold MSE | 0.11294028976877002；同上，仅为协议敏感性比较 |
| 最终 Weighted Blend MSE | 0.17659368600599726（六位小数0.176594）；results/fusion_model_comparison.csv |
| 同集合 Best Ridge MSE | 0.1769213533906335（六位小数0.176921）；同上 |
| 融合验证样本 | results/paper_fig6_prediction_diagnostics.csv，481行 |
| SHAP | 仅解释 Best XGBoost；results/shap_feature_importance.csv → results/paper_fig5_shap_importance.csv；Notebook SHAP分支为来源，不解释融合模型 |

正式中英文 PDF、全部正式图像、模型和结果 CSV 的逐文件 SHA256 见 results/frozen_artifacts_sha256.md。Notebook 写入单元及目标见 notebooks/WRITE_RISK_REGISTER.md。

## 最小迁移依赖顺序

1. 数据读取、schema/样本数检查与输出目录保护。
2. 固定 TimeSeriesSplit 与指标聚合口径，依赖第1步。
3. Ridge/XGBoost 与基线 Pipeline、CV，依赖第2步。
4. 特征处理与超参数搜索，依赖第3步；保留原协议并明确选择偏差。
5. OOF预测 → 融合开发/验证切分 → 权重选择与Stacking → 最终评价，依赖第4步。保存样本索引，避免划分漂移。
6. SHAP与误差诊断，依赖对应模型及验证预测；SHAP仅为Best XGBoost。
7. staging论文数据导出 → 与冻结CSV逐项比对。冻结图表与模型保持原位。

本轮仅建立文档与哈希边界；尚无统一实验入口或自动拒绝覆盖实现。
