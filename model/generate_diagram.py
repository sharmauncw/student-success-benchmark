"""
Draw the star-schema data-model diagram (navy/teal/gold theme).

Run:  python model/generate_diagram.py
Output: model/star-schema.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, TEAL, GOLD = "#0A2A4A", "#0E7C7B", "#D9A441"
BG = "#FFFFFF"

FACT = ("fact_student_outcomes", [
    "cohort_year (FK)", "residency_key (FK)", "student_type_key (FK)",
    "pell_key (FK)", "race_key (FK)",
    "cohort_n", "retained_1yr_n",
    "grad_4yr_n", "grad_6yr_n", "avg_debt_usd",
])

DIMS = [
    ("dim_cohort", ["cohort_year (PK)", "cohort_label", "cohort_size"]),
    ("dim_residency", ["residency_key (PK)", "residency"]),
    ("dim_student_type", ["student_type_key (PK)", "student_type"]),
    ("dim_pell_status", ["pell_key (PK)", "pell_status"]),
    ("dim_race_ethnicity", ["race_key (PK)", "race_ethnicity"]),
]
BENCH = ("peer_benchmark", ["cohort_year (FK)", "benchmark_retention",
                            "benchmark_grad_4yr", "benchmark_grad_6yr",
                            "benchmark_debt"])


def draw_box(ax, xy, w, h, title, cols, header_color, body="#F4F7F9"):
    x, y = xy
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                         facecolor=body, edgecolor=header_color, linewidth=2.2)
    ax.add_patch(box)
    hh = 0.42
    head = FancyBboxPatch((x, y + h - hh), w, hh,
                          boxstyle="round,pad=0.02,rounding_size=0.08",
                          facecolor=header_color, edgecolor=header_color,
                          linewidth=0)
    ax.add_patch(head)
    # square off the bottom corners of the header
    ax.add_patch(plt.Rectangle((x, y + h - hh), w, 0.10,
                               facecolor=header_color, edgecolor="none"))
    ax.text(x + w / 2, y + h - hh / 2, title, ha="center", va="center",
            fontsize=11, weight="bold", color="white", family="sans-serif")
    for i, c in enumerate(cols):
        ax.text(x + 0.18, y + h - hh - 0.28 - i * 0.30, c,
                ha="left", va="center", fontsize=8.5, color=NAVY)


def main():
    fig, ax = plt.subplots(figsize=(14, 10.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10.5)
    ax.axis("off")

    ax.text(7, 10.05, "Star schema — student_success model",
            ha="center", fontsize=17, weight="bold", color=NAVY)
    ax.text(7, 9.68, "synthetic demo data  •  one-to-many from each dimension to the fact",
            ha="center", fontsize=10, color="#5A6B7B")

    # fact: center
    fx, fy, fw, fh = 5.15, 3.10, 3.7, 3.60
    draw_box(ax, (fx, fy), fw, fh, FACT[0], FACT[1], GOLD)

    # dims around it
    positions = [
        ((1.05, 6.90), DIMS[0]),   # top-left: dim_cohort
        ((9.25, 6.90), DIMS[1]),   # top-right: dim_residency
        ((1.05, 0.60), DIMS[2]),   # bottom-left: dim_student_type
        ((9.25, 0.60), DIMS[3]),   # bottom-right: dim_pell_status
        ((5.15, 0.60), DIMS[4]),   # bottom-center: dim_race_ethnicity
        ((5.15, 7.30), BENCH),     # top-center: peer_benchmark
    ]
    for (bx, by), (title, cols) in positions:
        w = 3.7
        h = 0.42 + 0.30 * len(cols) + 0.18
        hc = TEAL if title != BENCH[0] else NAVY
        draw_box(ax, (bx, by), w, h, title, cols, hc)

    # relationship lines: dim -> fact (1 to many)
    rels = [
        ((4.75, 7.65), (5.15, 6.20)),   # dim_cohort -> fact
        ((9.25, 7.65), (8.85, 6.20)),   # dim_residency -> fact
        ((4.75, 1.35), (5.15, 3.60)),   # dim_student_type -> fact
        ((9.25, 1.35), (8.85, 3.60)),   # dim_pell_status -> fact
        ((7.00, 1.80), (7.00, 3.10)),   # dim_race_ethnicity -> fact
        ((7.00, 7.30), (7.00, 6.70)),   # peer_benchmark -> fact
    ]
    for (x1, y1), (x2, y2) in rels:
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     color="#7A8A99", linewidth=1.6,
                                     mutation_scale=14, shrinkA=2, shrinkB=4))
    ax.text(4.55, 7.05, "1 ── ∞", ha="center", fontsize=8, color="#7A8A99",
            style="italic", bbox=dict(facecolor="white", edgecolor="none",
                                      pad=1.5))

    out = Path(__file__).resolve().parent / "star-schema.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    print(f"Wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
    assert out.stat().st_size > 10_000, "diagram PNG looks empty"


if __name__ == "__main__":
    main()
