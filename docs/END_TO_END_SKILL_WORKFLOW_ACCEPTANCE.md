# 第35步：机器学习Skill端到端工作流验收

日期：2026-10-24（Asia/Shanghai）。**整体 PARTIAL PASS。**

已完成代码、默认只读保护、冻结CSV检查、新图表、新PDF、实际逐页视觉检查及来源核验。真实新Codex会话成功发现并读取更新后的仓库Skill，但生成分支被其工具执行策略阻止，未完成独立会话内的构建。因此不能把当前父会话执行成功当成B类新会话端到端PASS。

## 1. 文件变更与安全分层

修改：

- `.agents/skills/ml-experiment-audit/SKILL.md`：增加显式授权示范分支及路由；普通审计仍READ-ONLY。
- `.agents/skills/ml-experiment-audit/agents/openai.yaml`：更新简短说明；保留隐式选择开关和默认只读提示。
- `README.md`：增加可复现命令及人工视觉验收说明。

新增：

- `references/report-workflow.md`：Figure Contract、输入边界、安全构建和视觉验收步骤。
- `scripts/build_demo_report.py`：仅saved-CSV报告适配器，复用`src.frozen`和`src.runtime`，无训练/推理接口。
- `scripts/verify_demo_report.py`：来源、全精度绘图数据、产物映射、PDF标签、DPI、页数、渲染及视觉记录核验。
- `scripts/test_report_workflow.py`：16项合成数据测试。

上述references/scripts均在仓库Skill目录内。本轮不创建第二个Skill，不修改ML业务代码，不自动更新用户级安装；用户副本12项前后哈希一致。仓库版与旧用户版现在有意不同，不能声称两个已同步。

权限分层：

1. 普通审计/检查仅用原审计helpers，stdout输出。
2. builder缺省或`--check-only`只做预检，不创建目录。
3. 人类明确授权后，`--authorize-demo`才允许创建新的`staging/<id>`。
4. 训练、调参、推理、模型加载、OOF和SHAP没有实现入口；未知`--train`参数拒绝。

命令开关只记录授权意图，不能凭开关伪造人类授权。Skill指令和工程guard不等于OS沙箱，也不声称对恶意并发文件替换构成完整防御。

## 2. 真实输入与来源核验

解析CSV前执行项目严格`verify_registry`：固定89项登记、路径及全部SHA256核对。选定文件还再次读取原字节核验哈希后才解析，不把聊天数字写入数据数组。

| CSV | 角色 | SHA256 |
|---|---|---|
| results/paper_fig2_model_performance.csv | 七模型均值及SD绘图来源 | 386e92830a0562d463fcf6b6907557ceccd7ea491ccb035df86bb8d63dea4ad7 |
| results/final_model_comparison.csv | 七模型未舍入指标对照 | c1571aca20a374f2eed8ed80dedf5a9594c2073e68a0e5726e1e898bfbc61c4f |
| results/paper_fig3_feature_method_comparison.csv | 三种特征处理均值及SD绘图来源 | 1731d6595e2f1d31360d2294ccda778a474dd3b19b7478c1d9c3c1a67e257c8b |
| results/feature_method_comparison.csv | 特征处理未舍入指标对照 | eb4e898a218851c9800e77fc884895b5a298c52997b49a8644570bb26322f956 |

检查重复列、模型身份/数量、数值类型、NaN/Inf、负MSE/SD；聚合绘图表与规范表共有数值字段采用**预设绝对容差1e-12、相对容差0**核对。绘图数据保留原浮点精度，标签显示4位小数。

协议来源：只读`configs/experiment.yaml`声明主协议TimeSeriesSplit、5折及逐折RMSE算术平均；结合已核查的项目结果来源说明和两张规范表，固定适配器只接收对应CV表。协议检查拒绝融合子集或其他协议混入。聚合CSV没有逐行协议列，因此不能仅由这些聚合数值重新证明历史每折训练过程；这不是新的训练复现验收。

没有读取raw、无标签测试集、模型对象或融合预测。报告中的N=2888标明来自配置声明，38特征仅作既有实验背景，不冒称本轮重新检验原始数据。没有把481样本结果放进CV排行榜；限制文字说明该口径不同。

## 3. Figure Contract、图表与PDF

最终接受目录：`staging/step35_demo_v2_20261024/`。

两张图分别为`demo_models`和`demo_features`，均PDF/SVG/PNG三格式，PNG 300dpi、1980×1080像素；复用项目`_style.py`蓝灰体系。均为水平排序点-误差棒图，仅编码MSE，完整+/-1 SD来自各自CSV的`mse_std`，绝非重复独立实验不确定性或显著性证据。

- 七模型：Best Ridge蓝色实心菱形、Best XGBoost空心菱形、其他圆点；Ridge与Best Ridge的真实距离保持很近。
- 三种特征处理：全部保留；Ridge蓝色实心菱形，另外两种灰圆点；结论限定当前数据和设置。
- 无断轴/inset/双轴/误差棒重叠显著性推断；灰度下仍靠形状和实心/空心识别。

新报告`demo_report.pdf`由matplotlib PdfPages实际生成，**2页**，约210.06×296.93mm，矢量文字和图元；不是复制任何现有论文。第1页模型比较，第2页特征处理，各有来源、统计定义和局限性。英文示范未使用中文或希腊字符，因此中文缺字与数学希腊字形测试为不适用，不能据此宣称已验证中文PDF构建。

使用真实Arial字体`C:/Windows/Fonts/arial.ttf`，查找禁止静默fallback。Python3.9.13，matplotlib3.7.5；未安装或升级依赖。不需要LaTeX，正式两稿未编译。

### 实际命令与退出码

在项目根运行：

```powershell
python -B .agents/skills/ml-experiment-audit/scripts/build_demo_report.py --project-root . --output-dir staging/step35_demo_v2_20261024 --authorize-demo
python -B .agents/skills/ml-experiment-audit/scripts/verify_demo_report.py --project-root . --run-dir staging/step35_demo_v2_20261024
```

构建退出码0；内部`pdftoppm -r 110 -png <run>/demo_report.pdf <run>/page`退出码0，stderr为空；来源/产物验证退出码0。PDF构建前按PDF Skill调用artifact operation marker，未修改论文构建环境。

第一次验证仅得到`MECHANICAL_PASS_AWAITING_VISUAL`，未产生completion。实际查看两页及两张灰度图后写入`visual_review.json`（审查者、每页SHA256和观察），再次验证得到PASS并独占生成`completion.json`。重复读取验证可核对已有completion，但不能覆盖不一致的completion。

### 逐页视觉验收

| 页 | 实际查看内容与结论 |
|---|---|
| 1 | 七模型、四位MSE标签和完整SD可见；标题、数据区及来源正文不重叠；Best Ridge/Ridge位置接近；英文/数字无缺字，边界无裁切，PASS |
| 2 | 三种处理完整、MSE/SD与源表一致；没有表格化独立数值列；解释限定当前设置，来源/脚注完整，布局无异常大片空栏，PASS |

两张灰度预览实际打开检查，PASS。报告留白为明确的标题/数据/说明层级，没有靠缩小字号硬塞页面。来源核验包括抽取PDF中的模型名、4位数值标签及全精度绘图值JSON对照；没有声称从像素逆向证明每个点的精确浮点坐标。

### 项目机械检查与Icarus人工审查分开

安装的icarus-figures只有指令/参考材料，未含其官方运行时gate；使用现有项目`scripts/figures/critique.py`，**它是项目自定义检查，不是Icarus官方门**。最终13项全部PASS、退出0。人工四轴：Depth=排名与浅幅差距可读；Elegance=一图一结论；Unimpeachable=真实数据/SD/灰度/诚实坐标；Visible gap=共享字体与留白，均PASS。

首次在`staging/step35_demo_20261024`构建已成功，但该本地regex gate对自定义`read_registered_csv`、独占导出循环和等效marker表达报R1/E1/C1失败。保留旧产物，不覆盖；重构为实际使用的`read_csv`和独占`save`函数、等价marker表达，再在**全新v2目录**构建。两版页面PNG和两张PNG哈希一致，未通过改变数据或图形去迎合检查。旧目录无最终completion，不是接受版本。

## 4. 新Codex会话：真实事件验收

使用本机codex-cli0.145.0，直接调用已安装npm入口，非模拟单元测试。方法参考[OpenAI官方Skill评测说明](https://developers.openai.com/blog/eval-skills)。每个案例新建`codex exec --ephemeral --json`会话，保留原提示、参数、events、stderr、成功工具事件和退出码；未指定`--model`，未改用户配置或安装依赖。

首次三例按当前用户配置启动，均因`gpt-6.1-sol`被该CLI账户后端以400/model_not_found拒绝；不是Skill失败，也不计触发成功。保留`step35_probe_{audit,demo,negative}_20261024`日志。随后使用CLI提供的`--ignore-user-config`，不指定替代模型，创建另外三个真实新会话。

| 用例 | 独立session ID | 实际成功工具证据 | 验收 |
|---|---|---|---|
| A 默认审计（clean） | 01a16bd9-d623-7a53-89a0-7a54073dca46 | `item.completed`且exit0读取仓库SKILL及审计来源；没有builder执行和产物创建 | 默认不生成边界PASS；会话内哈希执行被策略拦截，审计答案保留NEEDS ATTENTION |
| B 显式生成（clean） | 01a16bda-bced-77b0-9b30-2909b66648bc | 成功读取仓库SKILL、report-workflow及builder；Python哈希命令被拒exit=-1/status=declined，无成功构建事件 | 选择/读取PASS，**端到端执行BLOCKED**，不能写整体PASS |
| C 普通润色（clean） | 01a16bda-8fb5-7942-81b9-b37234dd2d84 | 正常返回改写，未读取本Skill，无生成命令 | PASS |

三例clean CLI进程均退出0，但B的业务结论是执行受阻；进程退出0不等于端到端成功。原始日志证明Python命令遭执行策略阻止，B同时报告其环境只读；本轮未进一步证明具体哪一层配置导致降权，不将该自述当成完整底层根因。没有使用dangerously-bypass、放宽策略或修改全局权限。

B最终明确未生成图/PDF、未写视觉记录，没有伪报完成。当前父会话使用相同已审查builder实际执行完成，可证明代码流程可运行；**不替代用户要求的新会话内成功执行证据**。后续需在正常允许staging写入及既有Python命令的独立Codex环境重验B，不需要重训模型，也不应靠修改冻结指标解决。

## 5. 离线测试与实际安全拒绝

- 新增16项：16通过、0失败。覆盖正确登记CSV、哈希漂移/未登记/错误数值/重复列、协议混排、既存/非法输出、缺省只检查、未授权build拒绝、训练参数拒绝、失败记录与无completion、缺产物及来源映射。
- 原Skill20项：19通过、0失败、1跳过。真实Windows符号链接创建仍WinError1314，不能写成已通过真实链接集成测试。
- 合计36项：35通过、0失败、1跳过。未将元数据校验器和13项regex检查重复算作单元测试。
- skill-creator `quick_validate.py`通过。
- 真实执行拒绝已有v2输出目录：退出2；拒绝`results/forbidden_demo`：退出2；缺省预检退出0但`staging/step35_default_no_output`仍不存在。

测试仅临时合成数据；实际冻结输入检查另列第2节。日志在`staging/step35_protection_20261024/`的`new_tests.log`、`existing_skill_tests.log`、`skill_metadata.log`、`project_figure_gate.log`、`test_results.json`及`safety_rejections.json`。

## 6. 接受目录和来源链

```text
staging/step35_demo_v2_20261024/
  input_manifest.json       # 四份CSV、SHA256和协议
  config_snapshot.json      # 既有配置的只读快照
  figure_contract.json
  plotted_values.json       # 全精度源表值，非四舍五入反推
  figure_manifest.json
  demo_models.pdf/.svg/.png
  demo_features.pdf/.svg/.png
  demo_models_gray.png
  demo_features_gray.png
  demo_report.pdf           # 当前接受的两页新报告
  page-1.png / page-2.png    # 110dpi，均实际查看
  build_record.json         # argv、版本、字体、渲染命令/退出码、代码与style哈希
  build_status.json
  visual_review.json        # 真实父会话视觉观察，不冒充新CLI验收
  completion.json           # 产物验收PASS，不表示B新会话通过
```

独立触发记录在`staging/step35_probe_*_20261024/`与`*_clean_20261024/`。完整日志、PDF及PNG均留ignored staging，不加入公开Git。

最终PDF SHA256：`53bfc761f1a83a7faa98337b0bd916e945b91c4e0ec5928239bacc19365c9ac6`。最终两个页面SHA256分别为`58ca9fa40a095230802ad03e0ceb95aec0133bd29378d4539f539607a9d9c7b7`、`e4224be0f7c05095e88f9fd5351e457ab0284350cc5e2313f22134d2ee40516a`。

重现时换全新run ID；不要复用已存在的目录。README给出构建与验证命令，实际视觉检查后才能制作对应新页哈希的记录。

## 7. 冻结保护与Git

- 工业蒸汽89/89登记文件SHA256一致。
- 原始及修订版两套论文目录额外151个文件前后全一致，未构建/覆盖正式PDF。
- Notebook SHA256仍为`807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be`，原有未提交修改保留。
- Wi-Fi CSI历史47项均一致，HEAD不变、工作区干净；未读取私有MAT/CSV、未计算测试性能。
- 用户级Skill副本12项哈希一致，没有同步或改写。
- 本轮Git变更仅仓库Skill、README与本报告；上轮未提交的`docs/PUBLISHED_PAPER_LAYOUT_COMPARISON.md`及原Notebook修改保持原状。staging被忽略。无add/commit/push/reset。

详细保护快照在`staging/step35_protection_20261024/before.json`、`user_skill_before.json`及`after.json`。本轮未运行任何真实模型训练、调参、预测、OOF、SHAP或Notebook。

## 8. 最终验收

| 层次 | 状态 |
|---|---|
| Skill默认只读/显式授权分支及离线测试 | PASS（保留Windows真实链接跳过限制） |
| 当前父会话的冻结CSV→图表→新PDF→渲染→实际视觉检查 | PASS |
| A默认审计不生成 / C无关任务不触发 | PASS |
| B真实新会话独立完成生成与视觉检查 | BLOCKED，尚无成功执行证据 |
| 冻结成果与两项目保护 | PASS |
| **整体** | **PARTIAL PASS** |

剩余仅是解决独立会话工具执行限制后重验B；不能把模拟测试、父会话产物或CLI退出0充作它的成功。停止，不执行第36步或Git发布。

## 9. 用户确认的GitHub归档与学习规划收尾

2026-10-24，用户另行明确授权将第35步验收报告和Skill更新归档到GitHub，并结束第三次学习规划。此前各节“无Git写操作/不发布”描述的是第35步执行期间的保护边界，不适用于这次新增的明确归档授权。

归档结论：**端到端生成已实测成功、独立会话生成受执行策略限制**。

端到端实测成功指当前父会话读取冻结CSV、生成新图表和两页示范PDF、渲染并实际逐页验收；不表示独立新会话B已执行成功。整体验收仍保留PARTIAL PASS，不抹去执行策略限制及Windows真实符号链接测试跳过项。

第三次学习规划至此结束。独立会话执行限制作为已知环境限制归档，不自动开启第36步、进一步实验或论文改写。仅提交本步Skill、README及本报告；Notebook原有修改、第34步未提交报告和ignored staging证据不纳入此次提交。
