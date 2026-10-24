# Independent layout revision build

This is a non-frozen revision copy. Do not build inside ../acm_mm or replace its source/PDF/bibliography. Frozen figures are read from ../../figures/paper without modification. references.bib is a byte-identical local copy.

Use the installed pdfLaTeX engine, matching the original PDF's MiKTeX-pdfTeX producer. The source uses CJKutf8 and acmart; switching to XeLaTeX is not required for this project.

From this directory run PowerShell `./build.ps1`, or:

```text
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error main.tex
bibtex --disable-installer main
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error main.tex
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error main.tex
pdftoppm -r 110 -png main.pdf render_final/page
```

All build files and console logs remain here. --disable-installer prevents automatic package installation. No package update is performed. build_status.json records the four exit codes. MiKTeX's global log4cxx permission/update messages are environment diagnostics, not a reason to ignore compiler exit codes; current build exits zero.

Historical render_final belongs to Step29; step31_render_final belongs to Step31. See ../../docs/FINAL_PROJECT_ACCEPTANCE.md for the latest accepted build. Page PNGs, side-by-side comparisons and logs are local evidence, not clone prerequisites or published artifacts. Create a fresh local render directory before rendering. Frozen sources are never built in place.

Review and remaining warnings: ../../docs/ENGLISH_LATEX_LAYOUT_REVIEW.md. The local PDF is a reviewed layout draft, not a declaration of final ACM/TAPS submission compliance.
