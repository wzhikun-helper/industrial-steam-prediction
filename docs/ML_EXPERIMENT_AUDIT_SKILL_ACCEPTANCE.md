# 第32步：ml-experiment-audit创建、发现与真实调用验收

日期：2026-10-24（Asia/Shanghai）。**发现/真实调用测试PASS；整体PARTIAL PASS**。不是仅检查SKILL.md是否存在：已调用本机skills/list，并完成5个独立Codex模型会话。真实Windows链接集成测试仍因权限跳过，不能写成全面安全认证。

## 1. 当前环境与发现依据

- `codex --version`：codex-cli 0.145.0；实际app-server初始化userAgent为Codex Desktop/0.145.0。Windows Get-AppxPackage版本查询被拒，不能把上述CLI/server版本等同于额外验证了已安装Store包版本。
- 未发现<workspace>及两个项目根的AGENTS.md；仓库内文件扫描亦未发现额外AGENTS.md。没有新建AGENTS来强制选择这个Skill。
- 已完整读取本机skill-creator及openai-docs指令、skill-creator的openai_yaml.md；用其quick_validate.py实测通过。没有安装依赖。
- 原skill/steam_prediction_skill_v2_final.md完整读取：是历史完整训练流程文档，无标准frontmatter，不处于可发现技能目录，不能当成已注册Skill；原文件保留。其“重跑”“输出results”等操作未迁入默认执行行为。
- 已读Step20保护清单和来源登记、Step21–28工程配置/安全模块/协议/验收报告、Step29–31排版与科学措辞记录。新Skill将它们作为可选项目证据路径，不复制大型训练实现。

官方依据：[Build skills](https://learn.chatgpt.com/docs/build-skills)（由https://developers.openai.com/codex/skills/跳转，2026-10-24实际打开）。文档支持仓库的`.agents/skills`（从cwd向仓库根查找）、用户的`~/.agents/skills`、渐进加载及隐式调用；同名条目不合并，可能同时显示。文档说自动检测，必要时重启，但不能以该描述代替本机测试。

本机用户既有个人Skill还在`~/.codex/skills`；不将历史路径假定为唯一规则。新Skill放项目标准目录，并经授权安装完全相同副本到`~/.agents/skills/ml-experiment-audit/`供跨仓库使用，没有改全局config。两仓库Git根不同，父级<workspace>共享目录不是可假定的共同仓库作用域，所以没有用父目录凑共享发现。

## 2. 完整Skill目录树

```text
.agents/skills/ml-experiment-audit/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── frozen-protection.md
│   ├── regression.md
│   ├── classification.md
│   ├── paper-artifacts.md
│   ├── project-sources.md
│   ├── steam.audit.json
│   └── har.audit.json
└── scripts/
    ├── check_project.py
    ├── check_hashes.py
    └── test_checks.py
```

共12文件；用户级安装具有相同结构，12/12字节相同。本地仓库版用于版本管理，用户版用于共享；工业蒸汽选择器出现repo/user两个同名项是已记录的作用域重复，不是合并或两次执行。未来更新需核对/显式同步，不在每次审计自动改全局文件。

## 3. 元数据与触发边界

```yaml
name: ml-experiment-audit
description: Read-only audit of machine-learning experiment validation protocols, preprocessing leakage, regression or classification metric definitions, saved-result provenance, and frozen artifacts. Use for ML experiment reproducibility or validation/source audits, including industrial regression and participant-split HAR; not for ordinary prose polishing, general Git queries, or implementing/training models.
```

agents/openai.yaml明确`allow_implicit_invocation: true`，有display_name、short_description及提及`$ml-experiment-audit`的default_prompt。默认READ-ONLY；普通审计不授权训练、推理、SHAP/OOF、拟合scaler、保存模型、论文编译/覆盖、删除、安装或Git写操作，不读取私有原始数据，不反序列化模型。报告默认stdout。真实输出必须另行明确授权并使用项目既有runtime guard和新目录，不能绕过src/runtime.py。

主流程检查Schema证据、划分/拟合范围、真实模型调用和版本、任务指标、结果来源、图表/PDF流水线及冻结保护。回归/分类规则分别加载，不硬编码蒸汽指标为通用正确答案。纸面聚合SHAP不能伪造逐样本分布；PDF审计也不自动授权编译或绘图。

## 4. 脚本和离线测试

check_project.py接受project-root与audit JSON：任务指标类型验证、所需文件存在性、可选split CSV元数据的表头/重复ID/人员重叠，未来输出路径只验证不创建。报告明确机械检查不等于完成原始Schema、泄漏与语义审计，默认返回PARTIAL PASS而不是冒充全链路成功。不得调用训练或覆盖参数，未知参数退出2。

check_hashes.py只流式SHA256：支持Markdown路径/哈希表、JSON平面映射或显式JSON键；拒绝空清单、错误digest、重复路径、路径穿越、私有raw路径及链接/junction。只哈希模型字节，不加载权重对象。标准库即可运行；Skill不依赖新重型库。

实测命令（项目根运行）：

```text
python -B .agents/skills/ml-experiment-audit/scripts/test_checks.py
python -B ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/ml-experiment-audit
```

结果20项：19通过、0失败、1跳过。覆盖元数据、非法配置/缺文件、回归分类指标混用拒绝、哈希相同/不同/缺失/坏清单、非法输出/空的已有目录/穿越、默认不训练不写出、CLI训练/覆盖参数拒绝，以及人员重叠检查。跳过为真实符号链接创建WinError1314；不声称完成真实Windows链接逃逸集成验证。真实路径guard代码检查和其他路径拒绝不取代这项集成测试。

日志：staging/skill_step32_acceptance_20261024/offline_tests.txt、official_validation.txt、acceptance.json。两个项目机械profile成功，均不读取原始数据；完整审计语义由下面真实会话验证。

## 5. 真实发现证据

docs/step32_discovery.py使用安装的Codex app-server stdio：initialize→skills/list(forceReload=true，两个cwd)→model/list，不模拟响应。

原始证据：staging/skill_step32_discovery_drained_20261024/discovery.json（另存initialize.json、skills.json及stderr）。实际结果：

| cwd | name | scope | enabled |
|---|---|---|---|
| industrial-steam-prediction | ml-experiment-audit | repo | true |
| industrial-steam-prediction | ml-experiment-audit | user | true |
| wifi-csi-har | ml-experiment-audit | user | true |

这证明本机CLI/server发现；没有声称已人工点选当前桌面会话的UI菜单，也没有把本对话起始静态技能目录当成自动刷新证据。

## 6. 独立模型会话触发证据

docs/step32_skill_validation.py通过新`codex exec --ephemeral --sandbox read-only --json -C <project>`会话运行，未用本对话续写或单元测试伪造触发。每例保存request.json、events.jsonl、stderr.txt和probe_result.json。acceptance.json额外从item.completed且exit_code=0的事件提取成功SKILL读取，避免把尝试命令或started事件当成执行成功。

| 用例 | 提示是否指定Skill | 独立session ID | 退出码/Skill读取 | 验收 |
|---|---|---|---|---|
| A 显式蒸汽审计 | 是，$ml-experiment-audit | 01a16b78-0dbc-7900-a535-630300b52e4e | 0，成功读repo SKILL.md | PASS |
| B 自然语言蒸汽审计 | 否 | 01a16b78-a093-75e2-a12e-6f1339c40faf | 0，自行选择并读repo SKILL.md | PASS |
| C HAR跨项目审计 | 否 | 01a16b78-a080-7170-a6a0-d4b88c6003a9 | 0，自行选择并读user SKILL.md | PASS |
| D 普通会议通知润色 | 否 | 01a16b78-a073-7dd1-b7ad-c1541d607b93 | 0，无本Skill读取 | PASS |
| E Git分支/最新提交查询 | 否 | 01a16b78-a092-7ee3-a44e-c85ad7428875 | 0，无本Skill读取 | PASS |

B原提示为“请审计当前机器学习项目的验证协议、预处理泄漏风险、评价指标定义与已保存实验结果的来源，说明哪些结论可以复现、哪些尚不能确认”，追加只读/不读raw/不重算性能的安全限制，但未给Skill名、Skill路径或推荐答案。实际会话先宣告使用ml-experiment-audit，再成功读取5536字符Skill输出及分流规则。C同样不给名称或路径，工作目录是另一独立仓库。

完整提示和审计回答见acceptance目录对应`*_audit_response.md`及各probe目录request.json；不能用报告里Skill自称已加载替代tool事件。本次同时具备成功读取事件和工具执行/回答证据。

证据目录对应：

- A：staging/skill_step32_explicit_supported_20261024
- B：staging/skill_step32_natural_20261024
- C：staging/skill_step32_har_20261024
- D：staging/skill_step32_negative_prose_20261024
- E：staging/skill_step32_negative_git_20261024

## 7. 是否真正遵循，而非只读文件

A审阅旧verify_frozen_results.py后指出它会重算诊断指标，超出本轮授权，实际没有运行它，改为执行Skill纯SHA256脚本。它核实TSS/KFold、折内Pipeline、逐折RMSE均值、最终融合CSV与搜索分数区别，并保留481集合非外部测试及原始行ID缺失边界。这是具体安全决策证据。

B自行读取回归规则，追踪src/models.py、validation.py、evaluation.py及已有迁移档案，区分Ridge/LightGBM已复现、其他树的数值差异与真实融合/SHAP未重跑；没有为了审计重做CV。

C自行读取用户级Skill、classification.md及来源规则；读取split元数据核实P1–P5训练1400、P6验证280、P7–P8测试560，样本ID无重复和人员不交叉；没有打开私有MAT/CSV。核对Accuracy与7类无权Macro-F1、zero_division=0、矩阵行真列预测，读取既有指标而非重算。核对epoch016的checkpoint哈希、train-only normalizer及split哈希；发现当前入口与历史脚本哈希差异后核对公开脱敏映射及*_before.py归档，没有误判成训练成果被修改。47项前后匹配、Git干净。没有运行CNN、evaluate推理或fit_normalizer。

两个负面用例正常完成各自任务，无本Skill读取，不依靠提示“禁止使用该Skill”规避误触发。样本量有限，只能证明这两种负例和本次正例，不能保证所有未来提示都自动正确路由。

## 8. 遇到的真实阻碍与修复

1. 最初受当前外层沙箱限制，CLI无法初始化.codex状态DB/in-process client；exit1、无session。保留skill_step32_explicit_20261024日志，不算触发成功。
2. 获授权允许CLI初始化后，默认配置gpt-6.1-sol被当前CLI账户后端以model_not_found/400拒绝，session 01a16b75-ef1f-7971-8daf-6cd2c652d98d没有工具调用；不算成功。
3. app-server初次查询未排空stderr造成skills/list超时；增加并发诊断读取后真实API成功，失败目录保留不覆盖。
4. model/list实际返回默认gpt-5.6-sol可用；五个成功probe仅以--model gpt-5.6-sol临时指定，未改全局模型/配置，也不声称原默认模型问题已解决。被测会话仍是read-only sandbox，未用dangerously-bypass选项。
5. 最初probe结果已写入UTF-8 JSON，但控制台打印包含R²等字符触发GBK UnicodeEncodeError，部分外层runner/suite返回1。原始Codex进程exit0、events/JSON均完整；修复报告打印为ASCII转义、仅从completed事件收集命令后，最终聚合直接读取原始证据，不把wrapper报错当模型成功或模型失败。未为此重跑训练或改历史日志。

因此测试环境仍有默认模型配置和控制台编码限制，报告均披露；成功结论依赖本次明确的CLI测试配置，而非“所有Codex环境即装即用”。

## 9. 冻结与Git保护

- 工业蒸汽：89/89 SHA256匹配，无缺失/变动；Notebook SHA256仍为807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be。
- 两份原始论文和两份layout_revision目录在触发测试前额外快照150文件，结束150/150一致；没有编译或覆盖任何PDF/CSV/模型。
- HAR：指定历史47项47/47匹配；工作树仍干净；HEAD保持9e4447a（完整值见acceptance.json）。未创建HAR仓库技能副本或改仓库文件，跨项目通过用户级共享实现。
- 工业蒸汽HEAD保持508c8e1，既有Notebook和工程未提交变更保留；新增.agents/技能、docs验证工具/本报告和staging日志。没有add/commit/push/reset。

## 10. 结论与使用

发现、显式、自然语言、跨项目和两个负面触发样例均有真实证据，能力验收PASS。整体PARTIAL PASS保留真实Windows符号链接集成未验证、有限提示覆盖、现有CLI默认模型不可用及宿主权限要求。Skill指令不是OS访问控制，生产使用仍需只读沙箱、人工授权和项目runtime guard。

后续在任一项目可显式请求“请使用$ml-experiment-audit只读审计验证协议和结果来源”；自然语言审计已在本机新会话实测触发，但不能保证所有现有桌面会话动态刷新。不得自动转入训练、Git提交或最终发布。
