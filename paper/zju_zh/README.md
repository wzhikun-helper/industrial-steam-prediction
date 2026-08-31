# 《浙江大学学报（工学版）》中文论文 LaTeX 初稿

本目录是项目中文论文的可编译初稿。它按照已核对的期刊页面参数近似实现 A4、双栏、正文总宽约 164 mm、栏间距约 7.5 mm 的版式，但**不是期刊官方 LaTeX 模板**。

## 编译环境

- 引擎：XeLaTeX
- 参考文献：BibTeX + `natbib`
- 中文字体：SimSun（宋体）
- 英文与数字：Times New Roman
- 数学字体：STIX Two Math
- 已验证环境：Windows + MiKTeX

在本目录执行：

```powershell
xelatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

## 数据与图表来源

- 图题和图注唯一来源：`../figure_captions.md`
- 表题、表注及正式数值来源：`../table_captions.md`
- 冻结结果口径：`../../results/paper_result_manifest.md`
- 图1--图6直接引用：`../../figures/paper/*_zh.pdf`
- 结果数值核对自 `../../results/` 下的冻结 CSV；本工程不重新运行 notebook，也不修改 CSV。

项目中未找到任务所列的 `../table_style_spec.md`。当前表格依据任务中明确规则排版：`booktabs` 三线表、无竖线、仅加粗当前协议下的最佳数值、不使用颜色或显著性星号，且表1与表4保持分离。

参考文献采用 `unsrt` 顺序编码样式，是对《浙江大学学报（工学版）》著录格式的 LaTeX 近似实现。投稿前仍需按期刊正式要求复核作者缩写、文献类型标识、中文文献双语著录及 DOI 的最终呈现方式；文献事实来源统一记录在 `../literature_pool.md`。

## 尚待完成

- 作者、单位、邮编、通信作者及邮箱均为占位符。
- 基金项目与致谢信息待补充。
- 投稿前需根据期刊最终 Word/排版要求复核页眉、收稿日期、中图分类号、基金脚注和参考文献著录格式。
- 无标签测试集不报告性能；SHAP 仅解释 Best XGBoost；融合结论仅引用独立融合验证集。
