# 复现与安全运行指南

[项目首页](../README.md) · [文档导航](README.md)

## 环境与数据

声明环境位于[environment.yml](../environment.yml)，可在独立环境中尝试：

```bash
conda env create -f environment.yml
conda activate steam-prediction
```

声明文件不等于跨机器安装已验证。**2026-10-31按原文件创建隔离环境实测失败：本机继承的镜像频道返回HTTP 403，尚未进入依赖解析及pip安装阶段。** 后续配置隔离预检也未能排除全局频道，因此没有再次发起安装。新环境的测试和包兼容性均未验证，不以现有环境通过替代。详见[整改报告](RESEARCH_REMEDIATION_R1.md)及[机器可读证据](RESEARCH_REMEDIATION_R1_EVIDENCE.json)。历史依赖声明未修改。

历史版本证据见[工程验收](PYTHON_ENGINEERING_ACCEPTANCE.md)。配置文件虽名为YAML，当前入口以json.loads读取，只接受JSON语法子集。上方创建命令为预期使用方式，不表示已在本轮环境成功运行。

依据数据提供方授权自行取得带表头、制表符分隔的数据，放置为：

```text
data/raw/zhengqi_train.txt  # 2888×39，V0–V37及target
data/raw/zhengqi_test.txt   # 1925×38，仅V0–V37
```

Schema和列顺序见[配置](../configs/experiment.yaml)。不分发原始数据，不提供未经核实的下载来源或再分发许可。

## 预检与真实运行

首页的check-only不读取原始数据，不训练、不创建输出目录。授权数据就绪后，可只检查Schema：

```bash
python -B scripts/run_experiment.py --config configs/experiment.yaml --output-dir staging/schema_check_001 --stage ridge-baseline --dry-run
```

前五阶段dry-run读取数据并检查Schema，后三阶段只预检协议、文件和路径。所有输出必须位于新的staging/或reproduction/目录，已有目录包括空目录均拒绝覆盖。

| stage | 非预检入口实际能力 | dry-run | 历史数值复现证据 |
|---|---|---|---|
| ridge-baseline | 固定α=1/5，TimeSeriesSplit/KFold；可训练 | 读取真实数据、检查Schema，不拟合 | 已有运行记录在严格容差内一致 |
| tree-baselines | 四种未调参树模型；可训练 | 同上 | LightGBM一致；RF/GBDT/XGBoost有差异 |
| feature-processing | Ridge、KBest20、PCA95；可训练 | 同上 | 已有运行记录在严格容差内一致 |
| ridge-tuning | 原10个α候选、搜索及refit；可训练 | 同上 | 已有运行记录在严格容差内一致 |
| xgboost-tuning | 原108候选搜索、固定历史Best单独评价；可训练 | 同上 | 历史/当前最佳参数及分数存在差异 |
| fusion | 明确拒绝真实执行；合成测试使用模块原语 | 文件存在/索引协议/路径预检，不读数组 | 新工程未运行真实融合 |
| shap | 明确拒绝真实重算；合成测试注入explainer | 文件存在/路径预检，不读数组 | 新工程未重算真实SHAP |
| final-prediction | 明确拒绝真实训练/预测；合成函数测试 | 文件存在/路径预检，不读数组 | 新工程未重跑最终预测 |

各阶段均支持check-only。请先阅读[脚本说明](../scripts/README.md)及[安全约定](../scripts/MIGRATION_SAFETY.md)，不要为运行审核而去掉预检开关。

所有阶段的check-only仅核对配置、数据文件可用性和输出安全，报告raw_schema_checked=false，不读取原始数据、不创建目录。dry-run仍先检查数据文件存在；后三阶段的dry-run不等于无原始文件也一定可运行。CLI禁用是正常入口边界，不是阻止任意Python调用训练的操作系统沙箱。

上表“历史数值复现”引用已归档迁移记录，不是本轮重跑，更不是environment.yml的新环境验收。2026-10-31仅在已有Python 3.9.13环境中重新执行离线检查；新环境结果为NOT RUN。

## 测试与冻结来源

```bash
python -B -m unittest discover -s tests -v
python -B .agents/skills/ml-experiment-audit/scripts/test_checks.py
python -B .agents/skills/ml-experiment-audit/scripts/test_report_workflow.py
python -B scripts/verify_frozen_results.py --hashes-only
python -B scripts/export_paper_results.py --output-dir staging/export_check_001 --dry-run
```

测试仅使用临时合成数据。Windows真实符号链接测试可能因权限1314跳过，必须保留原因。89项核验检查注册数量、路径、唯一性和字节哈希；不要批量转换冻结文本换行。导出从已登记CSV读取，显式去掉dry-run才创建新的隔离目录，不依赖Notebook隐含状态。

Notebook有未确认发布的本地修改，登记SHA256为807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be。它没有提交到GitHub，新克隆保留已提交版本，因此使用hashes-only核验公开清单，不把本地工作副本身份冒充克隆内容。不要Run All。审计只需哈希模型字节，不需要反序列化joblib。

## 数值复现和解释边界

- 已严格复现：Ridge、特征处理、Ridge调参、LightGBM基线。
- 存在差异：RF、GBDT、XGBoost；具体致因未全部确认，不反复调参追求匹配。
- 尚未通过新工程真实重跑：融合、SHAP、最终训练和测试预测。
- CV RMSE为mean(sqrt(fold MSE))，不是sqrt(mean(fold MSE))；折间SD不是CI。
- weighted_blending_summary.csv约0.125956是搜索阶段分数，不是481样本最终验证MSE。
- 481样本未参与权重或元模型拟合，但可能参与上游超参数开发，不能称严格外部测试集。
- 历史Fig.6 CSV未保留逐行原始索引，精确行号来源仍为UNKNOWN。
- SHAP仅解释Best XGBoost，mean absolute SHAP不表示方向或因果；无标签测试数据没有真实性能指标。

证据：[工程验收](PYTHON_ENGINEERING_ACCEPTANCE.md)、[融合协议](../scripts/FUSION_PROTOCOL.md)、[其余协议](../scripts/REMAINING_PROTOCOLS.md)、[来源清单](../results/paper_result_manifest.md)。

## 论文与Skill

中文使用XeLaTeX/BibTeX，英文使用pdfLaTeX/BibTeX。把源码及所需图复制到隔离目录，保持相对路径，再按[中文构建说明](../paper/zju_zh_layout_revision/BUILD.md)或[英文说明](../paper/acm_mm_layout_revision/BUILD.md)执行，不原地覆盖已验收PDF。构建脚本禁用自动安装；中文字体可通过STEAM_PAPER_FONT_DIR指定，缺失时应报错。

仓库级Skill位于.agents/skills/ml-experiment-audit/，默认只读；用户级安装副本不自动同步。显式调用示例：“请使用 $ml-experiment-audit 只读审计验证协议和结果来源。”只有明确授权才能执行CSV→新图表→示范PDF分支。

**端到端生成已实测成功、独立会话生成受执行策略限制**。不把父会话成功或结构校验替代独立会话执行证据。参见[真实触发记录](ML_EXPERIMENT_AUDIT_SKILL_ACCEPTANCE.md)和[工作流验收](END_TO_END_SKILL_WORKFLOW_ACCEPTANCE.md)。
