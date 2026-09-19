"""
Directional consistency of the step-size effect.

For each maze and family, counts how many peak-vs-neighbor comparisons
had the peak (step 0.5) success rate GREATER than the neighbor's,
regardless of statistical significance. This measures how consistently
the peak "leans higher" than its neighbors.

Input: significance_all_families.csv (produced by significance_test.py),
which already contains one row per (family, maze, random_rate, neighbor)
comparison with peak_success_rate and neighbor_success_rate columns.
"""

import pandas as pd

INPUT = "significance_all_families.csv"


def main():
    df = pd.read_csv(INPUT)

    # A comparison is a "directional win" if the peak beat its neighbor.
    df["peak_wins"] = df["peak_success_rate"] > df["neighbor_success_rate"]

    # Count wins and total comparisons per family and maze.
    summary = (df.groupby(["family", "maze"])
                 .agg(wins=("peak_wins", "sum"),
                      total=("peak_wins", "count"))
                 .reset_index())

    # Pretty print as a wins/total table, families as columns.
    summary["cell"] = summary["wins"].astype(str) + " / " + summary["total"].astype(str)
    pivot = summary.pivot(index="maze", columns="family", values="cell")

    print("Directional consistency (peak > neighbor), wins / total:\n")
    print(pivot.to_string())

    # Also print raw counts so you can drop them straight into LaTeX.
    print("\nRaw counts per (maze, family):")
    for _, row in summary.iterrows():
        print(f"  {row['maze']:8s} | {row['family']:10s} : "
              f"{row['wins']}/{row['total']}")

    summary.to_csv("directional_consistency.csv", index=False)
    print("\nSaved to directional_consistency.csv")


if __name__ == "__main__":
    main()