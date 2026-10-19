"""
Generate synthetic (demo) data for the Student Success & Value Benchmark repo.

ALL DATA IS FICTIONAL. It is shaped to look like the kind of first-year
retention / graduation-rate reporting an institutional-research office does,
but every number here is made up for demonstration purposes.

Run:  python data/generate_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
rng = np.random.default_rng(20261018)

# ---------------------------------------------------------------- cohorts
COHORTS = list(range(2017, 2025))  # Fall 2017 .. Fall 2024
COHORT_SIZE = {y: int(rng.integers(2650, 2950)) for y in COHORTS}

# ------------------------------------------------------------------ dims
RESIDENCY = {"IN": "In-State", "OUT": "Out-of-State"}
RESIDENCY_W = {"IN": 0.82, "OUT": 0.18}
RESIDENCY_D = {"IN": 0.0, "OUT": -3.0}          # retention deltas, pp
RESIDENCY_DEBT_D = {"IN": 0, "OUT": 4200}

STYPE = {"FT": "First-Time", "TR": "Transfer"}
STYPE_W = {"FT": 0.76, "TR": 0.24}
STYPE_D = {"FT": 0.0, "TR": -6.5}
STYPE_DEBT_D = {"FT": 0, "TR": 900}

PELL = {"P": "Pell Recipient", "N": "Non-Pell"}
PELL_W = {"P": 0.32, "N": 0.68}
PELL_D = {"P": -4.5, "N": 0.0}
PELL_DEBT_D = {"P": -1200, "N": 0}

RACE = {
    "WHT": "White",
    "HIS": "Hispanic/Latino",
    "BLK": "Black or African American",
    "ASN": "Asian",
    "TWO": "Two or More Races",
    "NRA": "Nonresident Alien",
    "UNK": "Unknown",
}
RACE_W = {"WHT": 0.66, "HIS": 0.10, "BLK": 0.09, "ASN": 0.05,
          "TWO": 0.04, "NRA": 0.035, "UNK": 0.025}
RACE_D = {"WHT": 0.0, "HIS": -3.0, "BLK": -5.0, "ASN": 2.0,
          "TWO": -1.5, "NRA": 1.0, "UNK": -1.0}
RACE_DEBT_D = {"WHT": 0, "HIS": -300, "BLK": -200, "ASN": -400,
               "TWO": 0, "NRA": 2500, "UNK": 0}

# Center the deltas so the weighted average cell equals the target rate.
def _centered(cell_delta):
    mean = (sum(RESIDENCY_W[k] * RESIDENCY_D[k] for k in RESIDENCY)
            + sum(STYPE_W[k] * STYPE_D[k] for k in STYPE)
            + sum(PELL_W[k] * PELL_D[k] for k in PELL)
            + sum(RACE_W[k] * RACE_D[k] for k in RACE))
    return cell_delta - mean

def _centered_debt(cell_delta):
    mean = (sum(RESIDENCY_W[k] * RESIDENCY_DEBT_D[k] for k in RESIDENCY)
            + sum(STYPE_W[k] * STYPE_DEBT_D[k] for k in STYPE)
            + sum(PELL_W[k] * PELL_DEBT_D[k] for k in PELL)
            + sum(RACE_W[k] * RACE_DEBT_D[k] for k in RACE))
    return cell_delta - mean

# ------------------------------------------------- headline target rates
# (synthetic, but shaped like a real upward IR trend)
TARGET_RET = {2017: 81.9, 2018: 82.4, 2019: 82.9, 2020: 83.3,
              2021: 82.6, 2022: 85.0, 2023: 88.2, 2024: 88.0}
TARGET_G4 = {2017: 52.5, 2018: 55.3, 2019: 58.1, 2020: 59.8, 2021: 61.8}
TARGET_G6 = {2017: 65.4, 2018: 68.1, 2019: 71.6}
TARGET_DEBT = {2017: 8120, 2018: 8280, 2019: 8410, 2020: 8530,
               2021: 8660, 2022: 8790, 2023: 8860, 2024: 8930}

# ------------------------------------------------------- synthetic system
# "peer system" benchmark values (fictional "system average" style)
BENCH_RET = {2017: 81.2, 2018: 81.9, 2019: 83.1, 2020: 84.0,
             2021: 82.8, 2022: 84.7, 2023: 85.0, 2024: 85.9}
BENCH_G4 = {2017: 45.2, 2018: 47.0, 2019: 49.3, 2020: 50.7, 2021: 55.4}
BENCH_G6 = {2017: 63.0, 2018: 65.7, 2019: 68.2}
BENCH_DEBT = {2017: 11800, 2018: 12150, 2019: 12400, 2020: 12680,
              2021: 12950, 2022: 13180, 2023: 13310, 2024: 13450}


def build_fact():
    rows = []
    for year in COHORTS:
        n_total = COHORT_SIZE[year]
        cells = []
        for rk in RESIDENCY:
            for sk in STYPE:
                for pk in PELL:
                    for ck in RACE:
                        w = RESIDENCY_W[rk] * STYPE_W[sk] * PELL_W[pk] * RACE_W[ck]
                        d = (_centered(RESIDENCY_D[rk] + STYPE_D[sk]
                                       + PELL_D[pk] + RACE_D[ck]))
                        dd = (_centered_debt(RESIDENCY_DEBT_D[rk]
                                             + STYPE_DEBT_D[sk]
                                             + PELL_DEBT_D[pk]
                                             + RACE_DEBT_D[ck]))
                        cells.append((rk, sk, pk, ck, w, d, dd))
        # allocate headcounts so they sum exactly to cohort size
        raw = [n_total * w for *_, w, _, _ in cells]
        counts = [int(x) for x in raw]
        remainder = n_total - sum(counts)
        order = sorted(range(len(cells)),
                       key=lambda i: raw[i] - counts[i], reverse=True)
        for i in order[:remainder]:
            counts[i] += 1

        for (rk, sk, pk, ck, w, d, dd), n in zip(cells, counts):
            p_ret = np.clip(TARGET_RET[year] + d, 5, 99) / 100
            p_g4 = np.clip(TARGET_G4[year] + d * 1.15, 5, 99) / 100 \
                if year in TARGET_G4 else None
            p_g6 = np.clip(TARGET_G6[year] + d * 0.90, 5, 99) / 100 \
                if year in TARGET_G6 else None
            debt = TARGET_DEBT[year] + dd + rng.normal(0, 150)
            rows.append({
                "cohort_year": year,
                "residency_key": rk,
                "student_type_key": sk,
                "pell_key": pk,
                "race_key": ck,
                "cohort_n": n,
                "retained_1yr_n": int(round(n * p_ret)),
                "grad_4yr_n": int(round(n * p_g4)) if p_g4 else None,
                "grad_6yr_n": int(round(n * p_g6)) if p_g6 else None,
                "avg_debt_usd": int(round(debt / 10) * 10),
            })
    return pd.DataFrame(rows)


def build_peer_institutions():
    names = [
        "Demo University",
        "Bluewater State University", "Sandhills Regional University",
        "Capeview University", "Longleaf State University",
        "Azalea Coast University", "Magnolia Bay University",
        "Cypress Point University", "Seabrook State University",
        "Palmetto Shores University", "Driftwood University",
        "Lighthouse Point University", "Marshland State University",
        "Coral Bay University", "Dunewood University",
        "Estuary State University", "Gullwing University",
        "Tidewater Regional University", "Sawgrass University",
        "Beacon Isle University",
    ]
    peers = []
    peers.append({"institution": "Demo University",
                  "completion_rate": 77.9, "avg_net_price": 15180,
                  "is_demo": True})
    for name in names[1:]:
        price = float(rng.integers(6000, 40000))
        # completion tends to fall as price rises, with noise
        comp = 92 - price * 0.0011 + rng.normal(0, 6)
        comp = float(np.clip(round(comp, 1), 38, 89))
        peers.append({"institution": name, "completion_rate": comp,
                      "avg_net_price": int(price), "is_demo": False})
    df = pd.DataFrame(peers).sort_values("avg_net_price").reset_index(drop=True)
    return df


def main():
    fact = build_fact()
    fact.to_csv(DATA_DIR / "fact_student_outcomes.csv", index=False)

    pd.DataFrame([{"cohort_year": y, "cohort_label": f"Fall {y}",
                   "cohort_size": COHORT_SIZE[y]} for y in COHORTS]
                 ).to_csv(DATA_DIR / "dim_cohort.csv", index=False)
    pd.DataFrame([{"residency_key": k, "residency": v}
                  for k, v in RESIDENCY.items()]
                 ).to_csv(DATA_DIR / "dim_residency.csv", index=False)
    pd.DataFrame([{"student_type_key": k, "student_type": v}
                  for k, v in STYPE.items()]
                 ).to_csv(DATA_DIR / "dim_student_type.csv", index=False)
    pd.DataFrame([{"pell_key": k, "pell_status": v} for k, v in PELL.items()]
                 ).to_csv(DATA_DIR / "dim_pell_status.csv", index=False)
    pd.DataFrame([{"race_key": k, "race_ethnicity": v} for k, v in RACE.items()]
                 ).to_csv(DATA_DIR / "dim_race_ethnicity.csv", index=False)

    pd.DataFrame([{
        "cohort_year": y,
        "benchmark_retention": BENCH_RET[y],
        "benchmark_grad_4yr": BENCH_G4.get(y),
        "benchmark_grad_6yr": BENCH_G6.get(y),
        "benchmark_debt": BENCH_DEBT[y],
    } for y in COHORTS]).to_csv(DATA_DIR / "peer_benchmark.csv", index=False)

    build_peer_institutions().to_csv(
        DATA_DIR / "peer_institutions.csv", index=False)

    # sanity print
    agg = fact.groupby("cohort_year").agg(
        n=("cohort_n", "sum"), ret=("retained_1yr_n", "sum"))
    agg["retention_pct"] = (agg.ret / agg.n * 100).round(1)
    print(agg[["n", "retention_pct"]].to_string())
    print(f"\nWrote {len(fact)} fact rows to {DATA_DIR}")


if __name__ == "__main__":
    main()
