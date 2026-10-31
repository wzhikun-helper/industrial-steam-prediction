# 第一轮科研仓库整改报告

日期：2026-10-31（Asia/Shanghai）。结论：**PARTIAL PASS**。来源审查、文档整改、现有环境离线回归与冻结保护通过；独立环境创建失败，其后的新环境验收为BLOCKED。本轮没有真实模型实验，也没有重编论文。

[机器可读证据](RESEARCH_REMEDIATION_R1_EVIDENCE.json) · [阶段能力与复现指南](REPRODUCIBILITY.md) · [Notebook差异](NOTEBOOK_WORKTREE_REVIEW.md) · [投稿检查清单](SUBMISSION_CHECKLIST.md)

## 1. 整改前状态与已有实现

| 项目 | 整改前实际状态 |
|---|---|
| 分支/HEAD | main / b9ab96ab9e8938ccb955773cb737c8d51b8dcefc |
| 远程 | https://github.com/wzhikun-helper/industrial-steam-prediction.git |
| 工作区 | 仅notebooks/01_experiment.ipynb有原有未提交修改 |
| 冻结清单 | results/frozen_artifacts_sha256.md，严格89项，整改前逐项哈希一致 |
| 已有工程 | src/runtime.py安全输出；src/frozen.py严格注册核验；八阶段入口；scripts/check_delivery.py验收聚合；合成单元测试和Skill测试 |
| 已有报告 | 工程验收、Fresh Clone记录、第31步措辞与排版验收、第34步发表论文对照、历史运行摘要 |

实际读取README、environment.yml、configs/experiment.yaml、入口与调用模块、冻结表和已有复现记录，未只根据README判断实现。没有重复新增训练入口、环境安装器或通用核验工具；复用已有命令。安装驱动只在本地隔离目录，用于记录本轮尝试，不作为新业务代码提交。

本地证据目录：staging/research_remediation_r1_20261031/，由已有runtime独占创建，未覆盖旧运行。

- baseline.json：89项注册值、所有已跟踪文件的整改前实际哈希、HEAD/工作区/操作系统。
- notebook_diff.json、notebook_worktree.diff：只读完整差异，仅本地保留。
- conda_env_create.log/json、environment_request.json、environment_acceptance.json：实际创建命令、退出码及失败状态。
- clean_config_attempt/：两次配置解析结果和隔离配置草案，均未通过安全检查。
- existing_environment_checks/：复用check_delivery产生的逐项日志和checks.json。
- existing_environment_versions.json、existing_workflow_tests.log、protocol_indices_review.json：实际旧环境、合成测试及不读取数据的索引核对。

完整日志不公开本机路径、代理配置或样本显示；公开JSON保留脱敏事实和日志SHA256，不把它冒称为全部原始日志。

## 2. 独立环境创建实测

使用**原environment.yml**，仅通过prefix选择新的隔离位置；没有替换版本、频道声明或Python约束。命令的可读相对路径形式如下（实际绝对命令保留于本地JSON）：

```text
<existing-conda-python> -m conda env create --prefix staging/research_remediation_r1_20261031/environment --file environment.yml --yes
```

原YAML约束Python 3.11及10项pip直接依赖。spec SHA256为2e47f2bafa7ebb78fc9d7518c089c3d61375b2ebd2817edcf95cb437331431e1，前后不变。使用已安装Conda 26.3.2；系统报告Windows-10-10.0.26200-SP0。该平台字符串来自运行时，不推断营销版名称或跨平台可用性。

| 步骤 | 实测结果 | 可得结论 |
|---|---|---|
| PATH中的conda批处理启动 | 报“The system cannot execute the specified program” | 启动器调用有问题，不等于YAML解析失败 |
| 使用已有Conda Python调用模块 | 能运行，版本26.3.2 | 使用该入口做实际创建 |
| 独立prefix创建 | 退出1，5.42秒；元数据请求HTTP 403 | 环境创建失败，未进入依赖求解/pip安装 |
| 配置隔离预检 | 进程环境变量及独立CONDARC仍解析出本机镜像频道 | 安全检查拒绝后续创建，未发起第二次安装命令 |
| 新环境Python/包版本 | 不可用 | 不伪造pip freeze或安装成功记录 |
| 新环境测试/八阶段/哈希 | NOT RUN / BLOCKED | 不能用旧环境结果代替 |

实际错误摘要：

```text
CondaHTTPError: HTTP 403 Forbidden for url
https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/win-64/repodata.json
```

**CONFIRMED**：YAML只声明defaults，但实际Conda合并了本机镜像/pytorch/conda-forge频道；失败发生于频道元数据读取。首次命令继承的本机配置为ssl_verify=false，日志有InsecureRequestWarning。后续预检显式启用true，但解析后的频道仍不干净，未继续创建。没有编辑全局配置，也没有新增关闭TLS校验的设置。

**UNKNOWN**：403由镜像服务、代理策略还是网络出口的哪一层造成；现有证据不足以唯一归因。没有依赖求解或pip安装结果，不能断言版本可安装，也不能断言某个pin不存在/不兼容。原YAML不能因此被悄悄“修正”为当前旧环境的版本。

包缓存计划位于本轮新隔离目录；未启动旧环境更新或conda base更新。安装在元数据阶段失败，没有模型反序列化。后续建议是另行核验洁净Conda配置及可信TLS链，再尝试**原文件**；若需要修改依赖，另立兼容配置并保留历史声明，而非覆盖原件。本轮停止安装重试，不绕过403、认证或证书检查。

## 3. 测试：仅现有环境，不是新环境验收

实际解释器为已有Python 3.9.13；主要包：NumPy 1.24.4、pandas 2.0.3、SciPy 1.10.1、scikit-learn 1.6.1、XGBoost 2.1.4、LightGBM 4.6.0、SHAP 0.49.1、matplotlib 3.7.5。它与environment.yml的Python及版本不同。Jupyter发行包在该解释器未发现，不能据此推断系统其他环境没有Notebook工具。

实际运行：

```text
python -B scripts/check_delivery.py --output-dir staging/research_remediation_r1_20261031/existing_environment_checks --official-validator <installed-skill-creator>/scripts/quick_validate.py
python -B .agents/skills/ml-experiment-audit/scripts/test_report_workflow.py
```

| 检查 | 已有环境结果 |
|---|---|
| 工程离线测试 | 57项：56通过，1跳过，0失败 |
| Skill审计测试 | 20项：19通过，1跳过，0失败 |
| Skill示范工作流测试 | 16通过，0失败 |
| 官方Skill结构校验 | 退出0；不是新的独立会话触发验收 |
| 五个工具help | 全部退出0 |
| 八阶段check-only | 全部退出0；未创建任何待运行目录 |
| python -O冻结核验 | 89项通过 |
| 论文结果导出dry-run | 退出0；没有复制或覆盖正式结果 |

两项跳过均为Windows真实符号链接权限1314，模拟链接拒绝测试不替代真实链接集成测试。合成测试可能拟合极小的合成模型，不能当作真实训练/调参或论文性能复现。check-only不验证真实数据Schema；本轮没有打开私有原始数据或计算新模型指标。

## 4. 八阶段能力与证据类型

完整矩阵已更新到[复现指南](REPRODUCIBILITY.md)，由scripts/run_experiment.py实际分派及src/validation.py、feature_experiment.py、tree_experiment.py、xgboost_experiment.py、fusion_experiment.py和diagnostics.py审查得到。

- **只读核验**：文件来源、配置、索引计划、注册SHA256；不拟合模型。
- **check-only**：八阶段均支持；不读原始数组、不检查真实Schema、不创建目录。
- **dry-run**：前五阶段读取授权数据检查Schema；后三阶段只查文件存在、协议和路径，仍可能因数据文件缺失而停止。
- **真实训练**：仅前五阶段显式非预检入口可进入拟合/搜索；本轮均未执行。
- **禁用阶段**：fusion、shap、final-prediction真实CLI明确拒绝；函数原语的合成测试可执行不等于真实运行获准。
- **历史数值复现**：引用既有运行CSV及比较记录，不能由本轮预检通过推出。Ridge/特征处理/Ridge搜索和LightGBM已有严格容差内一致证据；RF/GBDT/XGBoost保留差异。

已有历史报告按当时版本保留，例如第28步写“无check-only”是当时状态；本轮以当前源码及矩阵为准，不覆盖历史记录。

## 5. 实验协议与结论审查

### 划分与预处理

configs/experiment.yaml固定主协议TimeSeriesSplit(5)，对照KFold(5,shuffle=True,random_state=42)。src/validation.make_folds对2888个行位置生成的TSS训练数为483、964、1445、1926、2407；每折验证481，训练/验证行位置无重叠。这里只重建索引计划，没有修改原划分或训练。

StandardScaler→Ridge Pipeline每折重新构造拟合；KBest20为KBest→Scaler→Ridge，PCA95为Scaler→PCA→Ridge，均在折内拟合。树模型忠于原协议，不强行添加Scaler。评价复用summarize_cv_scores，RMSE为逐折开方后取均值。

TimeSeriesSplit保证位置顺序，不证明匿名工业数据的真实时间语义已经核实。KFold的较低分数只能显示协议敏感性，不能证明它更合理。

### 结果事实、解释与限制

| 已保存事实 | 来源 | 允许解释及边界 |
|---|---|---|
| Best Ridge α=5，平均MSE 0.13036913621734353；Ridge为0.13057163122601453 | final_model_comparison.csv、ridge_alpha_tuning.csv | α=5是浅幅数值最优，不作显著性推断 |
| Best XGBoost平均MSE 0.14983440587129646 | best_xgboost_summary.csv、final_model_comparison.csv | 调参改善历史分数但未超过Ridge；不以XGBoost 2.1.4重算值覆盖 |
| Best Ridge TSS MSE 0.13036913621734353，KFold MSE 0.11294028976877002 | validation_strategy_comparison.csv；已提交Notebook索引153/155/159 | 同一Best Ridge的协议敏感性，非选择“正确验证法”的证据 |
| Weighted Blend最终MSE 0.17659368600599726，同集合Best Ridge 0.1769213533906335 | fusion_model_comparison.csv | 仅约0.19%改善；不能和五折均值直接排名 |
| 全OOF池权重搜索MSE 0.12595591736078293 | weighted_blending_summary.csv | 搜索/选择分数，不是最终验证性能 |

所有数字从已有CSV读取，不是本轮训练输出。

### OOF与481样本

位置0–482没有TSS OOF，不能填作真实OOF；覆盖483–2887共2405行。按覆盖行的80/20划分，开发1924行（483–2406）、验证481行（2407–2887）。0.7/0.3权重和Stacking元模型只在开发部分选择/拟合；末尾验证标签未参与这两个步骤。

但上游超参数开发可能使用这些标签，且不是嵌套评价，因此不是严格独立外部测试集。历史误差CSV没有逐行原始索引，当前代码的计划索引不能反向证明历史每一预测行的ID。SHAP只解释Best XGBoost；匿名特征不能被赋予未经证实的物理因果意义。

## 6. Notebook与投稿归档

只读对比已提交171单元与工作副本179单元：前171单元和顶层metadata相同，末尾新增3个Markdown、5个代码单元，已保存执行计数95–99，含Fig.1/3/5导出及fold SD计算。没有新训练代码，但有真实CSV覆盖行为与尚未提交的历史来源价值。详见[独立Notebook审查](NOTEBOOK_WORKTREE_REVIEW.md)。Notebook保持未暂存，本轮不执行。

新增[独立投稿检查清单](SUBMISSION_CHECKLIST.md)，区分官方已有证据、发表实例观察、项目建议及当前尚未核验的投稿要求。既有中文参考文献/前置区、ACM字体/字段等差距继续保留，不把可编译当正式投稿合规。本轮没有改动论文、参考文献、图或PDF，也没有新视觉验收结论。

## 7. 文件变化、公开安全与保护

| 文件 | 整改前 | 整改后 |
|---|---|---|
| README.md | 已有公开首页 | 增加简短新用户导航和真实环境阻塞状态；实验数字不变 |
| docs/README.md | 已有索引 | 增加本轮报告、证据、Notebook和投稿清单入口 |
| docs/REPRODUCIBILITY.md | 已有指南/矩阵 | 区分check-only、dry-run、训练和历史数值复现；登记新环境失败 |
| docs/RESEARCH_REMEDIATION_R1.md | 不存在 | 本报告 |
| docs/RESEARCH_REMEDIATION_R1_EVIDENCE.json | 不存在 | 脱敏机器可读实测证据 |
| docs/NOTEBOOK_WORKTREE_REVIEW.md | 不存在 | 未确认Notebook的差异分类与保留理由 |
| docs/SUBMISSION_CHECKLIST.md | 不存在 | 独立投稿准备清单 |
| staging/research_remediation_r1_20261031/ | 不存在 | 本地基线、失败日志、配置预检和已有环境测试日志，不提交 |

未改environment.yml、configs/experiment.yaml、任何src/scripts/tests业务文件、Skill或历史验收记录。没有搬迁成果、删除失败记录或创建新训练工具。冻结89项和Notebook哈希前后核验；六个修订稿tex/PDF/bib另与整改前逐字节基线核对。

.gitignore已覆盖staging/reproduction、环境和缓存、原始数据及构建日志；不重复添加规则。提交仅上表7个公开Markdown/JSON文件。检查公开相对链接、敏感键和本机路径，不提交日志、配置隔离草案、未确认Notebook、用户级Skill或私有数据。

## 8. 状态、未完成项与发布

| 项目 | 状态 |
|---|---|
| 来源/能力/协议审查与文档 | PASS |
| 现有环境离线检查 | PASS，保留2项真实symlink跳过 |
| 第一次环境创建 | FAILED：频道元数据HTTP 403 |
| 后续干净配置预检 | BLOCKED：实际频道未隔离，拒绝再次创建 |
| 新环境依赖安装、测试、八阶段预检 | NOT RUN / BLOCKED |
| 冻结、Notebook及修订论文保护 | PASS |
| 完整训练、真实Schema、模型加载、新PDF视觉验收 | 本轮未执行，不宣称通过 |
| 当期正式投稿要求/作者信息 | 待教师/作者及正式材料核验 |

本轮可公开真实失败及审查改进，但不能标记“独立环境复现已完成”。推送前只暂存明确列出的7个文档，核对远程及本地SHA；具体身份以Git历史和最终回复为准，不在文件内部填入自指commit。**不创建正式Release或版本标签。**

下一步最小阻塞项是：在不继承问题频道、且TLS可信的Conda配置/机器中再次验证原environment.yml，然后才运行新环境离线测试和八阶段check-only。若安装仍失败，应保留错误另议兼容声明，不改论文或冻结结果来制造成功。
