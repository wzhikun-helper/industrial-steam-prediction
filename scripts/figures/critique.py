"""Mechanical quality gate aligned with the documented icarus-figures checks."""

import re
import sys
from pathlib import Path


CHECKS = (
    ("R1", r"read_csv\s*\(", "reads figure data from a CSV path"),
    ("S1", r"paper_style\s*\(", "uses the shared publication style"),
    ("U1", r"xerr\s*=|yerr\s*=|fill_between\s*\(|UNCERTAINTY_AVAILABLE\s*=\s*False", "draws uncertainty or explicitly records that it is unavailable"),
    ("U2", r"standard deviations|1 SD|SIGNIFICANCE_INFERENCE\s*=\s*False", "defines uncertainty or prohibits unsupported inference"),
    ("N1", r"five TimeSeriesSplit[\s\S]{0,80}folds|VALIDATION_CONTEXT\s*=|MODEL_CONTEXT\s*=", "states the validation or model context"),
    ("E1", r"save\s*\([^\n]+formats=\(\"pdf\", \"svg\", \"png\"\)", "exports PDF, SVG, and PNG"),
    ("E2", r"dpi=300", "exports PNG at 300 dpi"),
    ("C1", r"marker = \"D\" if tuned else \"o\"|marker=\"D\"|SINGLE_SERIES\s*=\s*True", "uses redundant encoding or declares a single data series"),
)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python critique.py <figure_script.py>")
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    failures = []
    for code, pattern, message in CHECKS:
        if re.search(pattern, text, flags=re.MULTILINE):
            print(f"PASS {code}: {message}")
        else:
            failures.append((code, message))
            print(f"FAIL {code}: {message}")

    banned = {
        "G1": (r"\bjet\b|rainbow", "no rainbow colormap"),
        "G2": (r"projection\s*=\s*[\"']3d", "no decorative 3D"),
        "G3": (r"confidence interval|95% CI", "does not relabel SD as a confidence interval"),
        "G4": (r"weighted_blending_summary\.csv", "does not use the prohibited blending summary"),
        "G5": (r"inset_axes|brokenaxes|broken_axis", "uses no inset or broken axis"),
    }
    for code, (pattern, message) in banned.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            failures.append((code, message))
            print(f"FAIL {code}: {message}")
        else:
            print(f"PASS {code}: {message}")

    print("\nJudgment prompts:")
    print("[ ] Depth: the visual encoding makes the stated comparison readable without the caption.")
    print("[ ] Elegance: one panel carries one comparison claim without decorative ink.")
    if re.search(r"UNCERTAINTY_AVAILABLE\s*=\s*False", text):
        print("[ ] Unimpeachable: unavailable uncertainty is not invented, no significance is implied, and markers survive grayscale.")
    else:
        print("[ ] Unimpeachable: uncertainty is defined, validation N/context is stated, and markers survive grayscale.")
    print("[ ] Visible gap: typography and spacing remain legible at the declared physical width.")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
