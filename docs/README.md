# 文档导航

## 从哪里开始

- **了解项目**：[首页](../README.md)展示问题、实验协议和主要结果。
- **运行与复现**：[复现指南](REPRODUCIBILITY.md)集中说明环境、数据、八阶段CLI和安全边界。
- **阅读论文**：[中文PDF](../paper/zju_zh_layout_revision/main.pdf)与[英文PDF](../paper/acm_mm_layout_revision/main.pdf)为优先阅读版本，均保留可编辑源码。
- **核对证据**：[结果来源](../results/paper_result_manifest.md)与[工程验收](PYTHON_ENGINEERING_ACCEPTANCE.md)区分历史指标、协议迁移和数值复现。
- **本轮整改**：[第一轮报告](RESEARCH_REMEDIATION_R1.md) · [测试与环境证据](RESEARCH_REMEDIATION_R1_EVIDENCE.json) · [Notebook工作副本审查](NOTEBOOK_WORKTREE_REVIEW.md) · [投稿检查清单](SUBMISSION_CHECKLIST.md)。独立新环境创建目前BLOCKED，不等于完整重训复现。

## 研究与工程资料

1. [中文修订论文](../paper/zju_zh_layout_revision/main.pdf)与[英文修订论文](../paper/acm_mm_layout_revision/main.pdf)。原稿在`paper/zju_zh/`与`paper/acm_mm/`，保留冻结及修改对照身份。
2. [LaTeX排版学习总结](LATEX_LAYOUT_LEARNING_NOTES.md)、[真实已发表论文对照](PUBLISHED_PAPER_LAYOUT_COMPARISON.md)。第三方论文PDF与完整页面证据仅在本地，不公开全文。
3. [Python工程验收](PYTHON_ENGINEERING_ACCEPTANCE.md)、[运行说明](../scripts/README.md)、[安全迁移约定](../scripts/MIGRATION_SAFETY.md)。
4. [标准Skill](../.agents/skills/ml-experiment-audit/SKILL.md)、[真实发现与跨项目触发记录](ML_EXPERIMENT_AUDIT_SKILL_ACCEPTANCE.md)、[端到端验收](END_TO_END_SKILL_WORKFLOW_ACCEPTANCE.md)、[两页示范PDF](ml_workflow_demo.pdf)。
5. [最终项目验收及Fresh Clone记录](FINAL_PROJECT_ACCEPTANCE.md)、[本次目录清理与核验](COURSE_DELIVERY_CLEANUP.md)、[逐项清理候选表](CLEANUP_CANDIDATES.csv)。

## 排版与实验来源

- [英文排版诊断](ENGLISH_LATEX_LAYOUT_REVIEW.md)、[中文排版诊断](CHINESE_LATEX_LAYOUT_REVIEW.md)、[科学措辞校正](STEP31_SCIENTIFIC_WORDING_AND_ACCEPTANCE.md)。
- [冻结来源](../results/paper_result_manifest.md)、[89项冻结哈希](../results/frozen_artifacts_sha256.md)、[融合协议](../scripts/FUSION_PROTOCOL.md)。
- [图注事实源](../paper/figure_captions.md)、[表注事实源](../paper/table_captions.md)、[文献核验池](../paper/literature_pool.md)。
- [历史Skill流程](../skill/steam_prediction_skill_v2_final.md)是学习材料，不替代标准`SKILL.md`发现入口；不修改用户级安装副本。

端到端生成已实测成功、独立会话生成受执行策略限制。保留失败证据、跨版本数值差异及验证独立性边界，不将协议迁移等同于全部数值复现。原始数据、本地运行目录、渲染和完整日志不作为公开克隆的必需文件。
