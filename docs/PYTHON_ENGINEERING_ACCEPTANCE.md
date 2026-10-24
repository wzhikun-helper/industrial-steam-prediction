# Python工程总验收与交付审计（第28步）

日期：2026-10-23（Asia/Shanghai）。总状态：**PARTIAL PASS**。

本轮不是机器学习实验。仅新增本报告；业务代码、Notebook、冻结成果、论文和Skill均未修改。执行了合成数据测试、CLI help/dry-run/拒绝行为及已有文件只读审计。没有真实训练、调参、OOF、SHAP、推理、依赖安装或Git写操作。Python运行可能生成已忽略的__pycache__；不清理历史文件。

## 1. 工程结构与代码核查

```text
configs/experiment.yaml             相对路径配置，JSON语法的YAML 1.2子集
src/data_utils.py                  TSV读取、Schema、NaN/Inf及重复列检查
src/models.py                      原Notebook固定模型、特征Pipeline、搜索构造
src/validation.py                  固定TSS/KFold、折内拟合、指标及Ridge阶段
src/evaluation.py                  四项指标、逐折RMSE算术平均
src/runtime.py                     路径隔离、运行目录独占创建、拒绝覆盖
src/tree_experiment.py              四树基线、冻结对比、失败状态
src/feature_experiment.py           特征处理和Ridge搜索
src/xgboost_experiment.py           搜索与历史固定Best模型分开输出
src/fusion.py                      加权公式
src/fusion_experiment.py            OOF、开发/验证划分及融合原语；真实入口禁用
src/diagnostics.py                  残差、误差排序及合成SHAP接口
src/final_prediction.py             合成最终训练/预测及隔离保存
scripts/run_experiment.py           8阶段统一CLI
scripts/export_paper_results.py     8份明确来源CSV的字节一致导出
scripts/verify_frozen_results.py    只读冻结哈希与CSV一致性核验
scripts/figures/                    6套英文、6套中文绘图脚本及样式/检查
tests/                             7个test_*.py；45项测试
notebooks/                         原实验和写入风险登记，继续保留
results/                           冻结CSV、来源说明和89文件SHA256登记
models/                            冻结模型、融合配置，保持原位
figures/                           历史草稿与paper正式图，保持原位
paper/                             两份稿件、官方模板和共享事实文档
staging/                           6个已归档运行目录
skill/                             工作流Markdown及历史归档；没有标准SKILL.md
environment.yml、README.md          声明环境与项目概述
```

实际检查了函数调用链：CLI加载配置→输出路径检查→数据Schema检查→显式分派阶段。训练输出来自拟合及预测；冻结CSV只用于运行后的比较，没有发现用冻结指标替代计算结果。论文导出明确是复制历史来源，不冒充新实验。

Ridge Pipeline、模型构造和summarize_cv_scores得到复用。各阶段仍重复环境元数据、CSV保存和完成/失败逻辑；这不是当前数值差异的证据，但已造成状态记录不统一。fusion的手工元模型Ridge(alpha=1)无Scaler，忠于Notebook，不能用基础模型Pipeline替换。

扫描configs/src/scripts/tests中的.py/.yaml未发现本机驱动器绝对路径；ROOT由脚本位置推导。历史staging内部XGBoost配置可能包含实际线程/环境信息，应作为运行证据看待。AST检查未发现模块顶层fit/predict/save调用；主要脚本由__main__保护，顶层sys.path.insert有进程内路径副作用。没有发现导入即训练或写业务结果的行为；第三方缓存不属于冻结文件写入。

## 2. CLI能力与实际检查

所有8个阶段分别执行了--help、--dry-run，退出码均0，无运行目录创建。通用--help会在argparse解析阶段返回，不加载配置/数据，不能视为训练可用性证明。

| stage | 当前真实能力 | 本轮执行 | 真实训练开关 |
|---|---|---|---|
| ridge-baseline | α=1/5，TSS和KFold，折索引/指标 | help+dry-run | 显式选择可训练，本轮未调用 |
| tree-baselines | RF/GBDT/XGB/LGBM固定基线TSS | help+dry-run | 同上 |
| feature-processing | 三种Ridge特征Pipeline TSS | help+dry-run | 同上 |
| ridge-tuning | 原10α搜索及refit | help+dry-run | 同上 |
| xgboost-tuning | 原108候选搜索+历史固定Best评价 | help+dry-run | 同上 |
| fusion | 索引协议预检；模块可用合成数据调用 | help+dry-run、真实调用拒绝 | 禁用 |
| shap | 配置/文件存在/输出路径预检；注入explainer测试 | help+dry-run、真实调用拒绝 | 禁用 |
| final-prediction | 配置/文件存在/输出路径预检；合成函数测试 | help+dry-run、真实调用拒绝 | 禁用 |

前5阶段dry-run检查真实训练/测试Schema；后三阶段在数据读取前返回，因此只检查配置、数据文件存在性、路径或索引计划，不应称为已检查数据Schema。新功能说明有这个措辞差异，见问题清单。

独立工具：export_paper_results.py的help和dry-run通过，未重新导出；verify_frozen_results.py的help和只读实际核验通过。没有check-only参数；已有dry-run满足对应预检需要。历史绘图脚本没有统一安全dry-run，本轮不执行绘图脚本，防止覆盖正式图。

临时目录拒绝检查（临时配置/合成占位文件，无冻结写入）：

| 场景 | 实测结果 |
|---|---|
| 非法stage | argparse退出2、列出合法stage |
| 非法配置内容 | 退出2，JSON解析错误信息 |
| 缺少数据文件 | 退出2，Missing data file |
| 空的已有staging目录 | 退出2，FileExistsError对应路径 |
| results输出 | 退出2，允许根目录限制报错 |
| staging/../results路径穿越 | 退出2，拒绝traversal |
| 无stage且非dry-run | 退出2，不加载数据 |
| fusion/shap/final-prediction非dry-run | 退出2，不加载数据、不创建目录、不产生completion |

模型模块中的synthetic布尔标志和注入factory属于API约定，不是操作系统沙箱；绕过CLI手工传真实数据依然可能训练。当前验收仅确认正常入口及已测试调用路径。

## 3. 离线测试结果

命令：`python -m unittest discover -s tests -v`。

- 总数45，通过44，失败0，跳过1。
- 跳过：test_foundation.FoundationTests.test_symlink_escape，Windows创建目录符号链接失败，WinError1314，缺少所需特权。
- 模拟链接拒绝测试通过；不能将其等同于真实链接集成测试。
- 测试使用临时合成数据，不训练真实数据，也不要求冻结结果写权限。
- 覆盖Schema/重复表头/非有限数据、固定折、折内预处理、指标、模型参数、失败状态、独占输出、OOF首段缺失、融合开发/验证隔离、SHAP对象限制、最终预测禁用和字节导出。
- XGBoost的test_search_and_fixed_outputs_separate仅检查源码字符串；通过不代表该测试完成端到端输出隔离验证。真实历史运行提供了额外证据，未来应替换该弱测试。

测试通过并不意味着下述全部工程缺口已消除。

## 4. 已归档运行与数值复现状态

统一严格容差为atol=1e-12、rtol=1e-10。复现状态来自既有staging记录及只读CSV检查，本轮没有重新训练。

| 阶段 | 入口/归档目录 | 真实执行状态 | 测试状态 | 数值复现 | 历史来源与限制 |
|---|---|---|---|---|---|
| Ridge α=1/5 | ridge-baseline；ridge_step22_20261023_001 | 已执行TSS/KFold | 本轮通过 | PASS，TSS平均值一致；逐折最大约1.11e-16 | ridge_baseline_cv_metrics、best_ridge_cv_metrics、final_model_comparison |
| 特征处理 | feature-processing；feature_step24_20261023_001 | 已执行15折拟合 | 本轮通过 | PASS，四指标逐折最大3.89e-16 | feature_method_comparison、KBest/PCA及Ridge逐折CSV |
| Ridge搜索 | ridge-tuning；ridge_tuning_step24_20261023_001 | 已执行10候选搜索/refit | 本轮通过 | PASS；α=5；搜索均值/SD最大8.67e-17 | ridge_alpha_tuning；历史无逐split搜索分数 |
| RF | tree-baselines；tree_step23_20261023_001 | 已执行5折 | 本轮通过 | NUMERIC DIFFERENCE | random_forest_cv_metrics；平均MSE差+0.000020579958 |
| GBDT | 同上 | 已执行5折 | 本轮通过 | NUMERIC DIFFERENCE | gbdt_cv_metrics；平均MSE差−0.000016338828 |
| XGB基线 | 同上 | 已执行5折 | 本轮通过 | NUMERIC DIFFERENCE | xgboost_cv_metrics；平均MSE差−0.006500789097 |
| LGBM基线 | 同上 | 已执行5折 | 本轮通过 | PASS，逐折四指标最大约8.33e-17 | lightgbm_cv_metrics；版本并非相同 |
| XGB搜索 | xgboost-tuning；xgboost_step25_20261023_001 | 已执行108候选及refit | 本轮通过 | 协议迁移PASS；选择结果NUMERIC DIFFERENCE | Notebook95保存最优输出；没有完整历史候选CSV |
| 固定Best XGB | 同上独立评价 | 已执行5折 | 本轮通过 | NUMERIC DIFFERENCE；平均MSE0.151741308024 vs0.149834405871 | best_xgboost_cv_metrics及summary；不是当前搜索胜者 |
| OOF/融合 | fusion | 仅合成测试/索引预检 | 本轮通过 | 未验证真实复现 | Notebook107–119；没有真实staging目录，不能编造运行归档 |
| SHAP | shap | 仅合成explainer/只读旧CSV | 本轮通过 | 未重新计算 | shap_feature_importance→paper_fig5；仅Best XGB |
| 最终预测 | final-prediction | 仅合成测试/旧预测审计 | 本轮通过 | 未重新训练或推理 | 旧两份1925行预测及模型哈希 |
| 论文导出 | 独立export CLI；paper_export_step27_20261023_001 | 已导出一次8份CSV | 本轮通过 | 8/8字节一致 | export_manifest、validation_report、completion |

staging实际只有上述6个目录：第22、23、24两个、25、27。第26协议预检及第27禁用检查按设计不产生目录，因此测试源码/本轮终端结果是执行证据，不能宣称存在持久化真实融合日志。

当前XGB搜索最优：colsample=.8、lr=.05、depth=3、trees=200、subsample=.8，MSE0.147410404298。历史最优：colsample=1、lr=.05、depth=2、trees=300、subsample=.8，MSE0.149834405871。两个参数组必须保留区别。具体跨版本差异原因尚未证明。

## 5. 验证独立性与统计边界

- StandardScaler/KBest/PCA在各训练折内部拟合；没有发现先全量拟合这些预处理的迁移行为。
- 调参与Best模型评价共用TSS折，不是嵌套CV；选择偏差仍在，不能称完全无偏泛化估计。
- 2888行中首483行无OOF；覆盖行483–2887共2405，开发1924行、验证最后481行（原始位置2407–2887）。
- 最后481标签不用于融合权重/元模型拟合，但可能用于上游超参数开发，不能称严格外部测试集。
- 全OOF同池权重搜索MSE约0.125956与最终融合验证0.176594分属不同口径，不能替换。
- Fig6旧CSV按绝对误差排序后重置索引；逐行原始样本号未保存，UNKNOWN。新函数保留row_id不等于补回历史缺失证据。
- SHAP只解释Best XGB，不解释Weighted Blend、方向性或因果；本轮只核验完整聚合CSV与Top15一致。
- 无标签测试预测不能计算真实性能指标。不作显著性推断，不把KFold较好数值当作更合理划分的证明。

## 6. 环境、版本和跨机器能力

| 项目 | environment.yml声明 | 当前实际运行 | 历史可确认线索 |
|---|---|---|---|
| Python | 3.11 | 3.9.13 | Notebook元数据3.11.16 |
| NumPy | 2.4.6 | 1.24.4 | 基线实际版本UNKNOWN |
| pandas | 3.0.5 | 2.0.3 | 基线实际版本UNKNOWN |
| SciPy | 未显式固定 | 1.10.1 | UNKNOWN |
| scikit-learn | 1.9.0 | 1.6.1 | 冻结Ridge模型字节含_sklearn_version=1.9.0 |
| XGBoost | 3.2.0 | 2.1.4 | 冻结Best模型内部版本数组[3,2,0] |
| LightGBM | 4.7.0 | 4.6.0 | 原基线实际版本UNKNOWN |
| SHAP | 0.51.0 | 0.49.1 | 原解释运行版本UNKNOWN |
| joblib | 1.5.3 | 1.5.3 | 声明相同不足以证明历史环境全同 |

模型文件内部证据通过字节只读检查获得，不反序列化拟合模型。它支持保存阶段版本信息，不能证明每个更早CV单元都在同一环境运行。当前电脑已验证部分数值复现；没有进行跨机器环境创建、全模型严格复现或完整训练链复现。声明环境是否可安装本轮未测试。

根README有数据尺寸、指标和边界说明，但缺少完整环境创建/激活命令、数据合法获得渠道及放置步骤、dry-run/测试命令、8阶段及禁用状态、差异报告导航。scripts/README提供部分操作说明；src/README仍以早期4模块为主，落后于源码；skill/README把普通流程文档称为Skill，缺少标准Skill入口和触发验证。未来GitHub归档前做小范围文档同步，本轮不修改。

## 7. 冻结保护与来源审计

- 从登记文件解析并逐文件重算89个SHA256：89一致、0不一致。
- Notebook SHA256：807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be，与登记一致。
- SHAP Top15与完整重要性来源一致；Fig6的481行与历史误差CSV一致，残差和四指标核验通过。
- 两份最终预测CSV均1925行，最终prediction与三列文件weighted_prediction一致。float64重建融合最大差8.107757576425456e-8，float32 XGB乘法项重建后8.881784197001252e-16；不能把前者静默算成严格一致，也不能据此声称原dtype已被直接记录。
- 第27步8份导出CSV当前仍与原来源逐字节相同，manifest提供各图/表映射、列顺序、行数与来源SHA256。
- 当前安全边界主要是程序约定与路径校验，不是文件系统只读ACL。旧Notebook和绘图脚本依然能覆盖冻结目录；本轮没有执行它们。

## 8. 发现问题及最小修复建议（本轮未修改）

| 严重程度 | 位置 | 已确认问题/限制 | 最小后续建议 |
|---|---|---|---|
| 中，真实融合前处理 | src/validation.py:run_ridge_stage | 没有统一try/except failure.json；metadata保持started，completion另行标记。tree阶段metadata写入也在try之前 | 保持已有产物不变，未来把全部阶段体纳入统一失败记录，明确完成标记优先级 |
| 中，归档前处理 | scripts/export_paper_results.py:export | 记录并验证复制字节，但不强制来源哈希等于89文件登记；源被改变仍可能导出PASS | 导出前强制比对登记哈希，报告“副本完整性”和“冻结来源身份”两个状态 |
| 中，核验工具完善 | scripts/verify_frozen_results.py:verify | 没有强制登记项数量89和唯一性；部分Schema使用assert，python -O可取消检查 | 用显式异常替代assert；校验条目数量、去重及路径；本轮独立确认真实89项 |
| 中，安全集成未验 | tests/test_foundation.py:test_symlink_escape；src/runtime.py | WinError1314跳过真实链接测试；路径先检查后创建不是对抗恶意并发链接替换的完整保证 | 在有权限环境补真实symlink/junction测试；正式多用户执行前评估竞态保护，不扩大当前安全宣称 |
| 中，数据接口完善 | src/diagnostics.py:error_analysis | row_ids查重/NaN但不拒绝Inf或非整数，不能单靠它保证原始行号合法 | 要求有限非负整数，必要时限定原数据长度范围 |
| 中，合成保存完善 | src/final_prediction.py:save_synthetic_prediction | 不强制models同时含ridge/xgboost；不检查frame权重公式；binary写入未复用统一链接检查 | 加模型键集合/预测公式校验，集中安全二进制写入；真实阶段继续禁用 |
| 中，使用文档 | README、src/README、scripts/README | 根文档缺工程上手步骤；scripts通用dry-run描述高于后三阶段实际检查深度 | 增加简短运行路径、能力矩阵和差异链接；明确后三阶段仅协议/路径预检 |
| 低，配置可用性 | configs/experiment.yaml；load_config | 实际仅json.loads；合法JSON式YAML可用，普通YAML语法不支持 | 明确JSON子集约束，或后续单独授权支持真正YAML解析 |
| 低，测试质量 | tests/test_xgboost_experiment.py:test_search_and_fixed_outputs_separate | 仅检查源码字符串 | 改成临时合成输出结构/独立模型调用断言 |
| 低，运行元数据 | 多stage模块 | 缺统一CLI命令、源代码/输入hash和时间记录；部分比较报告表格被多余空行分隔 | 后续新运行用统一metadata schema；旧记录保留，不补造历史字段 |
| 已知研究限制 | XGB/RF/GBDT归档；Fig6/融合 | 数值差异、原索引丢失和独立性边界 | 保留证据，不调参追旧值；需要新实验时另行授权 |

没有发现把冻结指标作为训练输出的明确代码错误；不能据此宣称工程零缺陷。上述问题不阻止只修改英文论文LaTeX，但不宜对外宣称生产级安全或端到端完全复现。

## 9. Git状态与归档建议

进入本轮前已存在：Notebook未提交611行新增（无删除）；results/paper_result_manifest.md、scripts/README.md、src/data_utils.py、src/models.py的修改，以及第20–27步新增configs/tests/runtime/各stage/协议和冻结清单等。它们不是本轮新增修改。本轮只新增docs/PYTHON_ENGINEERING_ACCEPTANCE.md。

staging为未跟踪目录，包含6次历史运行及报告，不能把其中数值差异记录清理掉后宣称全通过。建议未来有选择地归档可读报告、配置、索引、均值和差异文件，不盲目git add整个staging；保留原目录直至有明确归档决定。

当前已忽略：data/raw、scripts/src/tests的__pycache__、paper/acm_mm/main.txt等；这些不应误提交。本轮没有删除或清理它们。原数据不随Git提供时，应补合法数据取得说明。冻结模型/论文/图表继续保持原文件及登记哈希。未来提交前人工审阅Notebook差异、检查数据授权、区分声明环境与实际运行环境，不改历史产物制造一致。

## 10. 交付结论

**PARTIAL PASS**：具备配置驱动CLI、隔离输出、必要合成测试、部分严格复现和可追溯论文导出；真实融合、SHAP和最终预测尚未重新执行，且有明确禁用和记录。不能宣称跨机器安装成功、全模型严格复现或完整训练工程已经全部验收。

可以进入第29步英文论文LaTeX整改，前提是其范围为排版/文字维护、保持冻结实验事实及SHAP/融合/验证边界，不借整改替换成当前不同版本的新指标。本轮未修改或编译任何论文。工程中等问题留作单独授权的小范围修复任务。
