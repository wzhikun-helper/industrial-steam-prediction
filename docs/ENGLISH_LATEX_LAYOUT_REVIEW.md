# English LaTeX layout review — Step29

Review date: 2026-10-23, Asia/Shanghai. Overall **PARTIAL PASS**: requested layout improvements pass visual review; inherited font/bibliography/template warnings and scientific wording limitations remain explicitly recorded.

## Scope and frozen protection

Original source/PDF/bibliography in paper/acm_mm remain frozen. Revision lives exclusively in paper/acm_mm_layout_revision. The Chinese paper, all result CSVs/models and figures/paper were neither modified nor rebuilt. No training, prediction, SHAP, Notebook execution, dependency installation or Git write operation occurred.

## Original diagnosis and LaTeX causes

Original:7 letter-size pages, acmart v2.19, documentclass[sigconf,screen,review,anonymous], pdfLaTeX. Six figures:four single-column and two figure* (Fig3/Fig6); three single-column tables, zero table*. Original figures1–6 occur on pages2,3,4,4,5,6; references span pages6–7. Figure widths are columnwidth or textwidth. No H floats or explicit clearpage/newpage exist.

The page5 left column contains Fig5 and a small amount of Discussion, while its right column is largely empty. Fig6 is a figure*[!t] placed in source after the SHAP explanatory paragraphs. It enters the two-column top-float queue late. A FloatBarrier partway through Discussion prevents later text from flowing past pending floats, leaving page5 underfilled while Fig6 is deferred to page6. This mechanism matches both source inspection and the observed before/after layout.

Pages3–4 are dense with floats. Their content is not deleted; changing float source scheduling allows Fig5 to share page4 with its SHAP discussion and frees page5 for diagnostics and Discussion. The final bibliography previously spilled to a partially filled page7.

## Actual revision

Only layout scheduling commands changed:

1. Move the unchanged Fig5 and Fig6 environment blocks together immediately before subsection Global SHAP Importance, retaining Fig5-before-Fig6 source numbering. This schedules the tall single-column figure and next-page double-column figure earlier without renumbering their scientific identities.
2. Remove the single FloatBarrier in Discussion. Ordinary two-column floating now permits Discussion to flow naturally instead of stopping at the pending wide figure.
3. Add balance immediately before the CJK bibliography block, so last-page balancing is requested in time rather than only after reaching the second column. This removes the late-balance warning and equalizes column endings on page6.

No font-size, line-spacing, margins, figure scaling, caption content, table entries, bibliography style or documentclass changes. No negative vspace, H floats, manual page breaks, added paragraphs or deleted scientific content. Figure3 and6 remain full textwidth; original aspect ratios and frozen image bytes are preserved. Preamble float-fraction values are inherited unchanged. placeins stays loaded but no FloatBarrier is active.

An early intermediate moved Fig6 ahead of Fig5 and changed their automatic numbers; that iteration was rejected. Final aux and visual inspection confirm Fig5 remains SHAP and Fig6 remains diagnostics. Intermediate render_revision/ and earlier build artifacts are not the accepted version; render_final/ and regenerated compare_page_*.png are authoritative.

## Final page-by-page visual acceptance

Every original page1–7 and final page1–6 was rendered and visually inspected. Text extraction and aux labels were used only as supplementary checks.

| Page | Original | Final revision | Visual judgement |
|---|---|---|---|
| 1 | Title/abstract/Introduction | Same content and layout | Title, typography, two-column text and review line numbers intact |
| 2 | Related Work, data/method, Fig1 | Same layout | Fig1 and equations readable; no clipping |
| 3 | Fig2, Tables1/2, experiment text | Same overall layout | Dense but readable; no table overflow; captions remain attached |
| 4 | Fig3 at top, Fig4/Table3 left, SHAP/diagnostics text right | Fig3 at top, Fig4/Table3 left; Fig5 right with SHAP discussion | Still intentionally figure-dense, but relevant text and Fig5 now share a page; no overlap |
| 5 | Fig5 left; mostly empty right column | Fig6 full width at top; diagnostics and Discussion fill both columns | Major blank area eliminated; identity/residual panels and histogram clear; diagnostics on same page |
| 6 | Fig6 top, Discussion/Conclusion and start of references | Conclusion then all28 references with balanced endings | No last-figure/bibliography collision; reference glyphs and DOI lines readable |
| 7 | Remaining references, large lower blank | No seventh page | Natural pagination reduction; no deleted material |

Final figure positions:Fig1 p2; Fig2 p3; Fig3 p4; Fig4 p4; Fig5 p4; Fig6 p5. Tables1/2 p3; Table3 p4. Two equations remain on p2 with original numbering. References all on p6 after Conclusion. Fig3 is still cited on p3 and appears at next page top; this is a normal residual one-page float offset, not claimed eliminated. Page4 remains dense. Page6 has ordinary end-of-document lower white space after balanced references, rather than page5's blocked empty column.

## Compilation and warnings

Engine: installed MiKTeX-pdfTeX 1.40.29, acmart2026/06/27 v2.19. BibTeX + ACM-Reference-Format.bst. Full four-command build is provided in revision/build.ps1; build_status.json and build_*.txt preserve actual exit codes/logs. Package auto-installer is disabled; no updates performed.

Final main.log: undefined citations0; undefined references0; overfull boxes0; missing character warnings0. Four underfull vbox reports remain (badness10000/4072/10000/3746) in page-output handling. Visual review did not show corresponding overlap, cutoff or an isolated blank column. These warnings are reported, not hidden by margin/font manipulation.

Font warnings: C70/gbsn/m/it is unavailable and CJK falls back to the available default shape; a summary font-substitution warning remains. This affects italic styling for Chinese journal names in references, not missing characters. No replacement of references or global font shrinking was used. A future bibliography-font task can explicitly choose an appropriate supported CJK shape. Body uses acmart Libertine/Biolinum/math fonts; frozen figure labels retain their original embedded fonts.

BibTeX reports six missing publisher/address fields across chen2016xgboost, ke2017lightgbm and lundberg2017shap. These pre-existing metadata gaps are not silently invented or edited. All28 bib entries are cited and have28 generated bibcite entries; reference keys and bibliography bytes match the original. The ACM reference-format block warning remains because the inherited source sets printacmref=false. The late balance warning was removed by the layout change.

MiKTeX writes a global logging-permission warning and update-check advisory to stderr. Compilation still exits0 and creates the expected PDF; global logging permissions were not changed. A preliminary invocation from the wrong directory failed to find main.tex and generated only a log, subsequently relocated into the revision directory; it is not counted as a successful build.

## Scientific content and source equality

Automated normalized-source checks confirm: remove figure environments and the layout-only FloatBarrier/balance commands, then remaining source is identical ignoring whitespace; all six figure blocks are byte-text equivalent ignoring line endings/order; the multiset of numeric tokens is identical; bibliography bytes are identical. All3 table environments, abstract, title, formulas, scientific prose and citation commands are unchanged. This specifically preserves0.130369,0.176594,0.176921,0.19%,481 and the historical results; no current XGBoost2.1.4 recomputation is inserted.

Scientific wording issue recorded, not rewritten: the original repeatedly says independent validation without explicitly stating that upstream hyperparameter development may have used those labels. The known481-sample set is independent of fusion-weight/meta-fit, not a strict external test. Both versions retain the existing text, and neither should be treated as newly resolving that limitation. Search-stage0.125956 remains excluded from final claims; SHAP remains Best XGBoost only; unlabeled test data receive no error metrics. Consider a separately authorized narrow scientific clarification before submission.

## Template evidence and limits

The official ACM MM2026 Author Instructions page, checked2026-10-23, recommends traditional double-column acmart and explicitly gives [sigconf,screen,review,anonymous]. It also requires concepts and keywords. These elements are preserved. Source:https://2026.acmmm.org/site/author-instructions.html . The general ACM template page returned403 in this check; local installed acmart.cls and ACM-Reference-Format.bst were inspected. No local sample-sigconf.tex was found by kpsewhich.

Moving float source blocks, removing a blocking barrier and applying timely balance are project layout choices, not claimed ACM mandates. Review line numbers and anonymous authors are preserved. Screen options, conference metadata, rights/reference block, CJK processing and final production/TAPS compatibility still require track-specific submission checks. This report does not certify conference scope, originality, metadata eligibility or camera-ready compliance. No claim about meeting a minimum content-page rule is added from the old README; consult the current actual track instructions.

## Protection result and conclusion

All89 registered frozen files match their SHA256. Notebook remains807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be. Original English files, Chinese paper and figures are intact. New source/PDF/bibliography/build products/renders remain in paper/acm_mm_layout_revision; only this report is added under docs. Git changes from prior engineering steps are preserved, not staged or committed.

Layout objectives pass:7→6 pages, Fig5 p5→p4, Fig6 p6→p5, no page5 empty column, all figures/tables/references intact. Overall PARTIAL PASS retains the inherited font/BibTeX/reference-block and scientific-wording items above for final submission review. No Chinese-paper revision is performed.
