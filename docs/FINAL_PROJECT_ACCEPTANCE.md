# 工业蒸汽预测：最终交付验收（第33步）

日期：2026-10-24，Asia/Shanghai。当前状态：**PARTIAL PASS — 发布前门槛已通过，等待正常推送与Fresh Clone**。本文件将在实际验收后补记结果，不以计划代替完成证据。

## 1. 范围与最小修复

- Ridge阶段完整异常捕获，失败保留failure.json与traceback，成功完成后才写completion.json；拒绝已有运行目录。metadata指向最终状态文件而不假称成功。
- 新增src/frozen.py共享严格89项注册表：校验数量、唯一路径、合法SHA256、文件存在、路径穿越及链接；verify/export共用，核心保护不用assert，-O测试通过。
- 导出前核对每个已注册来源哈希；未登记/哈希漂移直接拒绝，不创建导出目录。复制字节一致性仍保留。
- diagnostics拒绝非整数、负数、NaN/Inf/重复row_id；合成最终预测检查标签形状、索引与有限性；保存要求两个模型齐全、融合公式一致，二进制保存复用文本写入的路径/链接/拒绝覆盖保护。
- 增加无原始数据的--check-only；与--dry-run分开，前者不读取或验证真实Schema，避免Fresh Clone伪装有私有数据。
- 修正中文稿英文摘要On an held-out→On a held-out；英文泛指句改为评价排除融合拟合的数据，未把481样本变成外部测试集。
- 中文字体路径改为构建时解析系统字体目录/STEAM_PAPER_FONT_DIR，生成被忽略的local_font_paths.tex；保持原字体文件，不自动安装或偷偷换字体。
- 根README、相关模块说明及Skill归档入口同步；正式报告去除作者本机用户目录，原始本地证据保留在被忽略的staging。

未训练、调参、OOF、SHAP、最终推理或运行Notebook，未改任何冻结CSV/模型/图或两份原论文。修订稿的字体路径修正是移植适配，不是整体期刊格式重构。

## 2. 交付工程结构

configs/experiment.yaml；src的数据/模型/评价/验证/各实验模块、diagnostics/final_prediction/runtime/frozen；scripts统一入口、导出、核验、check_delivery、check_skill_discovery及原论文图脚本；tests合成离线测试；docs正式报告和脱敏证据；.agents/skills/ml-experiment-audit标准Skill；results冻结CSV与来源/哈希；models冻结模型；figures/paper正式图；paper原稿/修订副本及官方材料；skill历史流程说明；notebooks历史实验与写入风险。

不提交完整staging/reproduction、页面PNG/并排图、LaTeX缓存/完整日志、私有原始数据或用户级Skill目录。不删除本机历史证据。原已跟踪成果保持原有身份。

## 3. Notebook与换行保护

notebooks/01_experiment.ipynb已有611行新增修改无法确认发布归属，本次明确排除，继续留在工作区且SHA256为807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be。Fresh Clone包含旧的已提交Notebook，不声称包含未发布工作副本；故克隆执行--hashes-only，只核对注册的89项，不能冒称完成本地Notebook身份核验。

89项中56项工作区与历史Git blob只差CRLF/LF，已逐项证明。精确.gitattributes固定历史检出EOL，使跨平台clone可恢复登记字节；不重存冻结成果、不改变89个旧blob或数字。其余33项原本即字节一致。所有冻结文件发布前仍89/89匹配。

## 4. Python、Skill与CLI预检

本地scripts/check_delivery.py --with-data的全部检查退出0：工程57项，56通过/0失败/1跳过；Skill20项，19通过/0失败/1跳过。两个跳过均为真实Windows symlink权限1314，模拟路径/链接拒绝测试通过，不记为真实链接集成PASS。官方quick_validate退出0。语法/路径/来源安全测试含-O、错误清单/来源、失败标记、输入形状和拒绝覆盖。

| stage | 真实能力 | 本轮预检 |
|---|---|---|
| ridge-baseline | 固定alpha1/5、TSS/KFold | help/check-only/dry-run，无训练 |
| tree-baselines | 四树未调参基线 | 同上 |
| feature-processing | 三种Ridge Pipeline | 同上 |
| ridge-tuning | 原10alpha搜索 | 同上 |
| xgboost-tuning | 原108候选+固定Best分别输出 | 同上 |
| fusion | 协议/索引预检，真实入口禁用 | 预检通过，未执行OOF |
| shap | 文件/路径预检，真实重算禁用 | 预检通过 |
| final-prediction | 文件/路径预检，真实训练/推理禁用 | 预检通过 |

无数据check-only八阶段均通过；dry-run前五阶段检查真实Schema，后三阶段不加载数据；均不创建试验输出。export dry-run通过注册哈希校验；Python -O冻结核验89/89。scripts/check_delivery.py可在clone无数据运行，只保存全新隔离检查日志，不编译论文、不执行训练。

## 5. 实验数值复现矩阵

| 内容 | 既有归档结论 |
|---|---|
| Ridge alpha1/5 | 严格容差内一致 |
| KBest/PCA与Ridge搜索 | 严格容差内一致 |
| LightGBM基线 | 严格容差内一致 |
| Random Forest / GBDT | 小幅数值差异 |
| XGBoost基线/搜索/固定Best | 数值差异；历史和当前选参不同 |
| 真实融合/SHAP/最终预测 | 新工程尚未重跑 |

脱敏归档见REPRODUCTION_EVIDENCE.json；历史诊断详见PYTHON_ENGINEERING_ACCEPTANCE.md。本轮没有重新生成这些实验，严格容差atol=1e-12、rtol=1e-10不变。CV RMSE逐折开方后平均。最后481个样本并非严格外部测试；历史Fig6原始逐行ID未保存；SHAP仅解释Best XGBoost；无标签测试不能报告真实性能。

## 6. 两份独立修订稿

- paper/acm_mm_layout_revision/main.pdf：6页，6图/3表、2个公式、28篇参考文献；Fig1–6在2/3/4/4/4/5页，表在3/3/4页，参考文献p6。
- paper/zju_zh_layout_revision/main.pdf：7页，6图/4表、6个公式、28篇参考文献；Fig1–6在2/3/4/4/4/5页，表在4/5/5/5页，参考文献p6–7。

两稿完整四步构建退出0，逐页渲染13页并全部查看。正文数字token、表体、公式、文献字节及引用身份不变，图表页码不变。无未定义引用、Overfull或缺字；Underfull英文3/中文6。保留CJK斜体/STIX数学粗体回退、英文6项文献字段警告、ACM reference block提示、中文文献样式与个别图文距离及末页留白。没有宣称完整投稿合规。

第一次按字体名称解析失败，未输出新PDF；现用同一原字体文件解析并完整重编译通过，失败日志只在本机留存，没有忽略失败退出码继续发布。

## 7. Skill归档与真实触发

仓库12文件与用户级安装12/12相同，没有提交用户级目录。.agents/skills/ml-experiment-audit/元数据、引用分层和离线脚本完整，默认READ-ONLY。本机实际skills/list再次确认enabled的repo条目，用户级条目不作为仓库交付缺失的替代品。

第32步真实显式、自然语言、HAR跨仓库以及普通润色/Git负面测试5个独立会话均有成功/不触发证据；报告ML_EXPERIMENT_AUDIT_SKILL_ACCEPTANCE.md保留会话ID、方法与限制。完整含本地路径的原始日志不公开；脱敏状态摘要不是模拟触发。当前CLI默认模型曾不受支持，测试临时用model/list返回可用默认项，未改全局配置。有限样例不保证所有环境自动路由。

## 8. Git候选范围与发布门槛

逐项选择源码、测试、配置、正式文档、Skill、来源清单及两份修订稿必要源码/PDF/构建说明；不用git add .或-A。不包含未确认Notebook修改、本地验证工具脚本、私密/原始数据、临时日志或逐页渲染。历史冻结字体路径按原稿保留，新增修订源码不含作者本机绝对路径。合法公开文献作者与既有Git作者元数据不冒充私密资料删除。

执行前历史HEAD为508c8e1a974b7869c7ce4143028cfe224b4ede64，origin为用户指定GitHub仓库，远程main已只读核实相同。仅在候选文件审计、diff检查、测试、冻结保护和论文验收完成后正常提交/推送，绝不强推。

## 9. 发布与Fresh Clone（待实际完成）

尚未提交或推送，本段在真实成功后更新提交SHA、远程同步和独立clone验收。Fresh Clone必须只来自远程，不复制旧项目文件；复用当前已装依赖，不冒称新机器安装或完整训练复现。必须验证仓库Skill的repo条目、无原始数据、离线测试/八阶段check-only、冻结哈希及两稿从克隆源码构建和页面对照。

## 10. 未解决问题与完成边界

Notebook工作副本发布归属待确认；真实symlink权限集成未完成；当前环境不是全部历史环境；树模型数值差异、OOF/SHAP/最终训练未重跑及研究统计边界保留；中文参考文献与正式投稿格式仍待专项。上述已知科研/投稿限制不伪装解决。只有发布与Fresh Clone本轮所有必要项实际通过后，才可按本任务定义标注FULL PASS。
