# 课程交付目录整理与安全验收

日期：2026-10-24。范围仅为整理、离线测试和隔离论文构建，不是新实验。提交身份以Git历史为准，避免把待提交文档里的自指SHA当作发布证明。

## 盘点与清理

整理前：`main`，HEAD `97e0e2ebe90eeeaed147a23b38bfeb97a3653323`，215个跟踪文件；Notebook有原有未提交修改，第34步报告尚未跟踪。远程为`https://github.com/wzhikun-helper/industrial-steam-prediction.git`。

已在仓库外本地备份目录`course-delivery-backup-20261024/industrial-steam-prediction/`保存HEAD、status、最近提交、remote、完整ls-files、未跟踪清单、目录树、大小、逐文件基线和清理候选。它与本仓库同级，不随Git公开，不改动其他Fresh Clone或private-backups目录。

候选逐项记录见[CLEANUP_CANDIDATES.csv](CLEANUP_CANDIDATES.csv)：包含路径、字节数、跟踪状态、引用来源、决定、理由、保护级别及缓存SHA256。

| 处理 | 数量/大小 | 理由 |
|---|---:|---|
| 删除已备份缓存文件 | 22个，90,760字节 | 仅scripts/src/tests中的未跟踪`__pycache__/*.pyc`；无文本入口引用，非冻结或唯一来源；复制后哈希一致才逐项删除 |
| 保留原稿与修订稿 | 4个paper目录 | 原稿有冻结身份，修订稿是当前交付与排版学习证据；不改名、不搬迁、不原地编译 |
| 保留staging及页面/日志 | 整理前50,425,477字节 | 含运行、失败触发、第三方论文和视觉对照的唯一证据，不能仅凭可重新生成判断可删 |
| 保留历史Skill及草稿图 | 原路径 | 教学/演进及历史来源价值；本轮没有证明可以删除 |

删除文件均可由仓库外`deleted_files/`恢复，CSV保留原SHA256。未执行`git clean`、reset或强推。没有删除任何跟踪文件。

## 整理前后目录树

```text
整理前                              整理后（原路径保留）
.agents/skills/ml-experiment-audit/  同左；Skill及触发记录不改
configs/ src/ scripts/ tests/       同左；去除22个字节码缓存
notebooks/                          同左；未提交Notebook不纳入归档
results/ models/ figures/           同左；冻结结果、正式图和历史图保留
paper/                              同左
  acm_mm/ zju_zh/                     冻结原稿（历史对照）
  acm_mm_layout_revision/             当前英文交付稿，6页
  zju_zh_layout_revision/             当前中文交付稿，7页
  zju_template/                      官方资料，保留原位
docs/                               原报告全部保留，并增加：
                                      README.md / COURSE_DELIVERY_CLEANUP.md
                                      CLEANUP_CANDIDATES.csv / ml_workflow_demo.pdf
                                      第34步报告纳入公开归档
skill/                              历史学习文档，保留
staging/                            本地证据，Git忽略
```

盘点大小（不含`.git`及私有原始数据）：paper约39.27 MB，figures约3.26 MB，models约0.28 MB，Notebook约1.35 MB；仅缓存减少90,760字节，新增文档与示范副本单独归档，不以总容量下降冒充质量提升。data/raw未遍历或读取。

## 正式入口及公开边界

根README和[文档索引](README.md)指向两份最终修订稿、排版学习总结、第34步出版论文对照、工程化说明、Skill及第35步验收。冻结历史论文仍是事实来源，不因“revision”或重复PDF而删除。

`ml_workflow_demo.pdf`是`staging/step35_demo_v2_20261024/demo_report.pdf`的原字节副本，2页、57,655字节，SHA256：`53bfc761f1a83a7faa98337b0bd916e945b91c4e0ec5928239bacc19365c9ac6`。没有重新绘图或训练，公开的是本项目示范报告而非第三方论文全文。

**端到端生成已实测成功、独立会话生成受执行策略限制**；第35步仍保留PARTIAL PASS边界。用户级Skill安装副本没有同步。原始数据、Notebook未提交修改、staging日志/完整渲染、第三方全文仅本地保留；没有新增公开私有数据。

## 清理后验收

| 检查 | 结果 |
|---|---|
| Python离线测试 | 57项：56通过，1跳过，0失败 |
| Skill审计测试 | 20项：19通过，1跳过，0失败 |
| Skill示范工作流测试 | 16通过，0失败 |
| 官方Skill结构校验 | `quick_validate.py`：Skill is valid |
| 八阶段CLI check-only及help | 全部通过；不训练、不读原始数组、不创建目标实验目录 |
| 导出dry-run及89项严格哈希 | PASS；冻结89/89一致 |
| Notebook工作副本 | SHA256保持`807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be`；原修改保留，不提交 |
| 论文构建 | 仓库外复制源码/参考文献/图，pdfLaTeX及XeLaTeX各4个命令全部退出0，禁用自动安装 |
| 页数及内容 | 英文6→6页，中文7→7页；规范化文本及数字序列相同；六张图和原表/文献保留 |
| 页面检查 | 全部原版与隔离构建页已渲染对照，无新增漂移/裁切；中文末页原有留白不在本轮修改 |
| 编译诊断 | undefined、overfull hbox、缺字均0；既有underfull vbox英文3、中文6及字体替代警告保留 |
| 来源保护 | 原稿、修订稿、图表、代码、测试、学习笔记与Skill相对基线均未发生非授权变化 |

两项跳过均为Windows真实符号链接权限1314，不报告为真实链接集成测试通过。MiKTeX全局日志权限提示未阻止构建；既有CJK斜体、STIX粗体替代、中文fixltx2e提示和BibTeX缺出版字段仍为投稿前已知限制，不伪称正式投稿全规范通过。

验收详细命令日志在本地`staging/course_delivery_check_20261024/`；隔离构建、页面对照和原始盘点在仓库外备份目录。本轮未执行任何真实训练、调参、推理、OOF、SHAP或Notebook。

结论：**本轮整理与保护检查PASS（明确保留上述跳过和既有研究/投稿限制）**。不确定冗余保留，不能据此声称所有历史中间材料均已清除。推送前须确认仅显式列出的交付文档被暂存；Notebook不得提交。
