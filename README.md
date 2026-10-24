# Industrial Steam Prediction

工业蒸汽量回归研究与安全复现工程。结果已经冻结；本仓库不宣称 SOTA、统计显著性、完整端到端重训复现或正式投稿全规范通过。

## 数据与结论边界

训练数据为2,888行、38个匿名特征 V0–V37 和 target；无标签测试数据为1,925行、38列。原始数据不随Git发布，请自行依据数据提供方授权取得并放到：

```text
data/raw/zhengqi_train.txt
data/raw/zhengqi_test.txt
```

二者均为带表头的制表符分隔文本；精确列序和形状见 configs/experiment.yaml。不提供未经核实的下载地址或数据再分发许可。异常工业样本不因误差大而删除。

主协议为5折 TimeSeriesSplit；KFold只是敏感性分析，时间语义尚未完全确认。CV RMSE是逐折RMSE的算术平均，而非平均MSE开方。

- 冻结 Best Ridge：alpha=5，平均MSE=0.130369（展示值0.1304）。
- 历史 Best XGBoost：平均MSE=0.149834；不要用当前环境的重算值替换它。
- 最后481个融合验证样本上，Weighted Blend MSE=0.176594，同集合Best Ridge为0.176921，改善仅约0.19%；权重0.7/0.3。
- 这481样本未参与权重选择或Stacking元模型拟合，但上游调参可能使用过标签，**不是严格独立外部测试集**。
- 约0.125956属于全OOF池权重搜索阶段，不是最终验证性能。
- SHAP仅解释Best XGBoost，平均绝对SHAP不表示方向、因果或显著性。
- 无标签测试数据不能计算真实性能指标。

## 工程结构

```text
.agents/skills/ml-experiment-audit/  标准只读审计Skill
configs/experiment.yaml            固定协议，JSON语法的YAML 1.2子集
src/                              数据、模型、CV、诊断及安全输出模块
scripts/run_experiment.py          八阶段统一入口
scripts/export_paper_results.py    注册来源校验后的CSV字节导出
scripts/verify_frozen_results.py    严格89文件注册表与来源核验
scripts/figures/                   历史正式图脚本，默认不要重跑
tests/                            合成离线测试
results/                          冻结CSV、来源及89文件哈希清单
models/                           冻结模型，审计不反序列化
figures/paper/                    冻结中英文正式图
notebooks/                        历史Notebook及覆盖风险登记
paper/acm_mm/、paper/zju_zh/       原冻结论文，禁止原地编译
paper/*_layout_revision/           独立修订源码、PDF和构建说明
docs/                             历史验收、限制及最终交付报告
skill/                            旧流程文档与演进记录，不是自动触发入口
staging/、reproduction/            本地隔离产物，Git忽略
```

## 环境

原声明环境在 environment.yml，可在有授权的机器上创建：

```powershell
conda env create -f environment.yml
conda activate steam-prediction
```

声明环境不等于已验证的历史全流程环境。本次Fresh Clone复用当前已安装依赖，没有执行新机器安装。已验证运行环境和冻结模型内部版本线索见 docs/PYTHON_ENGINEERING_ACCEPTANCE.md；不同版本可能产生差异，不能为匹配旧值修改参数。配置文件虽名为yaml，入口目前使用json.loads，只支持其JSON子集。

## 无数据预检与离线测试

在仓库根目录执行：

```powershell
python -B -m unittest discover -s tests -v
python -B .agents/skills/ml-experiment-audit/scripts/test_checks.py
python -B scripts/run_experiment.py --help
python -B scripts/run_experiment.py --config configs/experiment.yaml --output-dir staging/config_check_001 --stage ridge-baseline --check-only
python -B scripts/verify_frozen_results.py --hashes-only
```

check-only不需要或读取原始数据，不拟合模型、不创建输出；明确报告data_available及raw_schema_checked=false，不能替代真实Schema检查。目录名必须尚不存在。

取得授权数据后，可只检查数据Schema：

```powershell
python -B scripts/run_experiment.py --config configs/experiment.yaml --output-dir staging/data_check_001 --stage ridge-baseline --dry-run
```

前五阶段dry-run读取数据、验证Schema，不训练；后三阶段dry-run只做协议/文件可用性/输出路径预检，不读取数据。单元测试使用临时合成数据，不把其中结果当论文指标。Windows真实symlink权限测试可能跳过，需阅读跳过原因。

## 八阶段能力矩阵

| stage | 当前能力 | 本轮/默认安全边界 |
|---|---|---|
| ridge-baseline | 固定alpha=1/5，TSS/KFold评价 | 只有显式非预检调用才训练 |
| tree-baselines | RF/GBDT/XGB/LGBM未调参基线 | 同上 |
| feature-processing | Ridge、KBest20、PCA95 | 同上 |
| ridge-tuning | 原10个alpha搜索 | 同上 |
| xgboost-tuning | 原108候选，固定历史Best另评 | 同上 |
| fusion | OOF/开发-验证划分协议预检 | 真实入口禁用 |
| shap | 文件/路径预检，合成explainer接口 | 真实重算禁用 |
| final-prediction | 文件/路径预检，合成函数测试 | 真实训练/预测禁用 |

所有阶段支持 --check-only；数据具备时均支持 --dry-run。没有授权不要去掉预检开关。本轮没有真实训练、搜索、OOF、SHAP或测试推理。原结果目录拒绝作为输出；staging/reproduction下已有目录（包括空目录）也拒绝覆盖。

## 已有数值复现状态

| 内容 | 已归档状态，不是本轮重跑 |
|---|---|
| Ridge、特征处理、Ridge调参 | 严格容差内一致 |
| LightGBM基线 | 严格容差内一致 |
| Random Forest、GBDT | 小幅数值差异 |
| XGBoost基线、搜索、固定Best | 数值差异，历史/当前最优参数须区分 |
| 真实融合、SHAP、最终预测 | 尚未通过新工程重新运行 |

证据见 docs/PYTHON_ENGINEERING_ACCEPTANCE.md、scripts/FUSION_PROTOCOL.md、scripts/REMAINING_PROTOCOLS.md及源CSV。详细本机staging不整体发布；脱敏摘要不能冒充完整日志。Fresh Clone预检不是完整训练复现。

## 冻结来源及Notebook范围

results/frozen_artifacts_sha256.md登记89个结果/模型/图及原稿文件。核验器强制数量、唯一性、路径、文件存在与SHA256；python -O不能跳过。文件换行由.gitattributes逐项固定，保留历史检出字节，未改写实验数字。

```powershell
python -B scripts/export_paper_results.py --output-dir staging/paper_export_check_001 --dry-run
```

导出同时核对注册哈希和复制字节，来源错误或未登记会拒绝；显式去掉dry-run才创建全新隔离目录。

Notebook原有611行工作区修改的发布归属未确认，本次**没有提交**。本地核验登记的是该工作副本哈希；Fresh Clone保留原已提交Notebook，不能宣称包含未发布修改。因此克隆验收使用 --hashes-only；默认完整核验另外检查本地Notebook登记身份和既有CSV关系，克隆中的Notebook身份不应被伪装成该未发布工作副本。不要Run All。

## 论文

最新独立修订稿及构建：

```powershell
./paper/acm_mm_layout_revision/build.ps1
./paper/zju_zh_layout_revision/build.ps1
```

英文使用pdfLaTeX+BibTeX，中文使用XeLaTeX+BibTeX；详见各BUILD.md。需要预先安装LaTeX、acmart/ctex等包与相应字体，脚本禁止自动安装。中文默认从系统Fonts目录解析原SimSun/Times文件，也可设置STEAM_PAPER_FONT_DIR；生成的local_font_paths.tex不提交。字体缺失时报错，不偷偷换字体。

修订PDF为英文6页、中文7页，仍各28篇参考文献。原冻结稿和正式图只读保留。中文文献格式、数学粗体/CJK字体回退、部分图文距离和末页留白尚有差距，不宣称完全符合期刊/会议生产标准。作者/单位信息仍需真实填写；不会编造作者。

## Skill安装与调用

仓库级Skill在 .agents/skills/ml-experiment-audit/，在仓库根启动支持该规则的Codex即可发现；新机器不必依赖作者的用户级安装。跨仓库共享时，经许可将该单个目录复制到用户的 ~/.agents/skills/ml-experiment-audit，不复制整个用户目录、不覆盖已有版本。

显式调用示例：“请使用 $ml-experiment-audit 只读审计本项目的验证协议和结果来源。”

官方结构校验器属于本机Codex系统Skill，不随本仓库捆绑；已安装skill-creator时按其实际位置运行quick_validate.py。仓库自带离线测试不依赖它。真实发现、显式/隐式/跨项目及负面触发的五个独立会话证据见 docs/ML_EXPERIMENT_AUDIT_SKILL_ACCEPTANCE.md。这是已验证环境的有限样例，不保证所有模型、版本或会话必然自动触发。

## 安全与最终状态

### 显式授权的CSV→图表→示范PDF工作流（不训练）

普通审计仍默认只读。只有明确要求生成示范成果时，才执行仓库Skill的
`references/report-workflow.md`分支；用户级安装副本不自动同步。当前示范适配器
只支持本项目已冻结的回归CSV，不读取原始数据或模型，也不混排五折CV与融合验证结果。

```powershell
python -B .agents/skills/ml-experiment-audit/scripts/build_demo_report.py --project-root . --output-dir staging/my_unique_demo --check-only
# 以下命令仅在用户明确授权生成示范成果后运行；目标目录必须不存在。
python -B .agents/skills/ml-experiment-audit/scripts/build_demo_report.py --project-root . --output-dir staging/my_unique_demo --authorize-demo
python -B .agents/skills/ml-experiment-audit/scripts/verify_demo_report.py --project-root . --run-dir staging/my_unique_demo
python -B .agents/skills/ml-experiment-audit/scripts/test_report_workflow.py
```

构建使用现有matplotlib PdfPages及Poppler，不安装依赖。两页渲染须全部实际查看，
再记录带每页SHA256的`visual_review.json`并运行验证器；编译/构建成功不等于视觉PASS。
没有视觉记录时只返回等待视觉验收，不生成成功标记。具体证据与限制见
`docs/END_TO_END_SKILL_WORKFLOW_ACCEPTANCE.md`。

本仓库不包含私有原始数据，不自动上传数据。历史模型文件只应在可信环境按版本加载；哈希不等于反序列化安全。输出guard是工程边界，不是对抗并发攻击的完整OS沙箱。不要删除旧Notebook、覆盖冻结结果、重跑正式图或为了数值一致反复调参。

最终发布/Fresh Clone结果、测试数量、提交身份和未解决问题见 docs/FINAL_PROJECT_ACCEPTANCE.md。保留原研究的匿名特征、非嵌套选模、融合独立性和跨版本差异限制。

### 第三次学习规划收尾

第35步归档结论：**端到端生成已实测成功、独立会话生成受执行策略限制**。
现有冻结CSV到新图表、示范PDF及逐页视觉检查已在父会话实际完成；独立新会话
成功加载Skill，但生成执行遭策略拦截，因此总验收保持PARTIAL PASS，不宣称独立
会话端到端完全通过。详见`docs/END_TO_END_SKILL_WORKFLOW_ACCEPTANCE.md`。
第三次学习规划结束，未解决的环境限制如实保留，不自动继续第36步或新实验。
