# 中文论文独立排版副本：构建说明

本目录不是冻结原稿。原稿在../zju_zh，禁止在那里编译或用本目录文件替换原稿。references.bib是原稿的逐字节副本；图像只读引用../../figures/paper/。

当前源码为ctexart+fontspec+unicode-math，应使用XeLaTeX。要求预先安装宋体、Times New Roman及STIX Two Math，不能未经检查替换字体。第33步移除源码绝对路径：build.ps1从系统Fonts目录或STEAM_PAPER_FONT_DIR检查原字体文件，生成被Git忽略的local_font_paths.tex；数学字体通过TeX文件搜索解析。没有下载或安装字体。缺失时明确失败。

在本目录执行PowerShell `./build.ps1`。它按XeLaTeX→BibTeX→XeLaTeX→XeLaTeX构建，并将四次退出码写入build_status.json，完整控制台输出写入build_*.txt。--disable-installer禁止自动安装依赖。

最终渲染命令（render_delivery目录已建立）：

```text
pdftoppm -r 110 -png main.pdf render_delivery/page
```

第30步历史验收渲染在render_delivery，第31步在step31_render_final；第33步最终验收记录见../../docs/FINAL_PROJECT_ACCEPTANCE.md。逐页PNG/并排图只保留本机、不随Git提交；克隆后可在新的本地目录重新渲染，不依赖作者的旧渲染目录。

render_final和render_accepted包含中间迭代，均不是最终验收图。不要根据它们判断最终页数/字号/空白。最终PDF为main.pdf，共7页。模板PDF文本提取证据存于template_evidence；旧DOC没有完整转换，不宣称模板全项合规。

排版和参考文献诊断见../../docs/CHINESE_LATEX_LAYOUT_REVIEW.md；逐页结论见PAGE_COMPARISON.md。MiKTeX全局日志权限/更新检查提示保留，但不等同编译失败；本次四步退出码均0，没有安装、升级或修改系统配置。
