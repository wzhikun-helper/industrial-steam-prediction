# ACM MM English manuscript

This directory contains the anonymous ACM Multimedia 2026 main-track working draft.

## Official format verified on 2026-08-31

- ACM MM 2026 requires the traditional double-column ACM article template and explicitly recommends `\documentclass[sigconf, screen, review, anonymous]{acmart}` for submission review.
- Main Technical Program papers may use 6--8 content pages plus at most 2 reference-only pages.
- Review is double blind. Author names, identifying acknowledgments, and identity-revealing links must be absent.
- The main submission PDF may not contain an appendix. Supplementary material is submitted separately (50 MB limit).
- Concepts and keywords are required. Figures include meaningful `\Description{}` accessibility text.
- Camera-ready metadata, rights text, DOI, ISBN, conference fields, and real authors must be inserted only from the acceptance/TAPS instructions.

Official sources:

- [ACM MM 2026 Author Instructions](https://2026.acmmm.org/site/author-instructions.html)
- [ACM MM 2026 Call for Technical Papers](https://2026.acmmm.org/site/cfp-guidelines.html)
- [ACM article templates](https://www.acm.org/publications/proceedings-template)

## Files and build

- `main.tex`: anonymous review manuscript
- `references.bib`: 28 verified records drawn from `../literature_pool.md`
- Figures are referenced directly from `../../figures/paper/`; no frozen figure is copied or modified.

Build from this directory:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

If MiKTeX's wrapper reports a local logging-permission error after producing output, inspect `main.log`, `main.blg`, and `main.pdf` rather than relying only on the wrapper exit code.

## Scientific invariants

- Main comparison: five-fold TimeSeriesSplit.
- Fusion comparison: separate 481-sample validation set; it is not directly comparable to the cross-validation table.
- Search-stage blend performance is excluded from final fusion claims; only the independent validation result is reported.
- Weighted Blend improves over Best Ridge by only about 0.19% on the independent fusion set.
- SHAP explains Best XGBoost only, not Weighted Blend or the complete fusion system.
- Fold SD is not a confidence interval; the manuscript makes no significance inference.

## Before submission

- Confirm that the intended ACM MM 2026 track remains the Main Technical Program and recheck the live instructions immediately before upload.
- Confirm the paper has 6--8 content pages and no more than 2 reference-only pages.
- Keep the submission anonymous and remove PDF metadata that could identify authors.
- Add final author, affiliation, rights, DOI, ISBN, and conference metadata only for camera-ready production.
- Verify that all external assets and any supplementary files are anonymized.
