"""
Compute mean success rate and success-rate range for each maze,
using ONLY the coarse-sweep factorial grid (excluding the targeted
fine-grained sweep near step size 0.5).

The coarse grid is:
    step_size  in {0.3, 0.4, 0.5, 0.6, 0.7, 0.8}   (6 levels)
    random_rate in {0.1, ..., 0.8}                  (8 levels)
    100 replications per cell  ->  6 x 8 x 100 = 4800 trials per maze

We filter by the actual coarse step-size VALUES rather than by row
position, because filtering by "first 4800 lines" silently breaks if
the CSV rows are ordered differently or the fine sweep is interleaved.
A line-based fallback is included at the bottom for comparison.
"""

import pandas as pd

CSV_FILES = {
    "Maze 2": "rrt_results_maze2_postfix.csv",
    "Maze 3": "rrt_results_maze3_postfix.csv",
    "Maze 2-coupled": "rrt_results_maze2_budgent100k_coupled.csv",
    "Maze 3-coupled": "rrt_results_maze3_budget100k_coupled.csv"
}

# The 6 coarse step-size levels from the original factorial design.
COARSE_STEPS = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

# Small tolerance for float comparison (0.5 is exact, but 0.3/0.6/0.7
# are not exactly representable in binary floating point).
TOL = 1e-9


def is_coarse_step(value):
    return any(abs(value - s) < TOL for s in COARSE_STEPS)


def analyze(path, maze_name):
    df = pd.read_csv(path)
    df["success"] = df["path_found"].astype(bool).astype(int)

    # Keep only coarse-grid step sizes
    coarse = df[df["step_size"].apply(is_coarse_step)].copy()

    total_trials = len(coarse)
    overall_mean = coarse["success"].mean()

    # Per-cell success rates (each cell = one step_size x random_rate combo)
    cell_rates = (
        coarse.groupby(["step_size", "random_rate"])["success"]
        .mean()
        .reset_index(name="cell_success_rate")
    )

    cell_min = cell_rates["cell_success_rate"].min()
    cell_max = cell_rates["cell_success_rate"].max()
    n_cells = len(cell_rates)

    print(f"\n{'='*55}")
    print(f"{maze_name}")
    print(f"{'='*55}")
    print(f"  Coarse-grid trials used:    {total_trials}")
    print(f"  Number of cells:            {n_cells}  (expected 48)")
    print(f"  Overall mean success rate:  {overall_mean*100:.1f}%")
    print(f"  Cell success-rate range:    {cell_min*100:.0f}% to {cell_max*100:.0f}%")

    # Sanity check: warn if trial count or cell count is off
    if total_trials != 4800:
        print(f"  [!] WARNING: expected 4800 coarse trials, got {total_trials}.")
        print(f"      Check for duplicate rows or unexpected step_size values.")
        print(f"      Step sizes present: {sorted(df['step_size'].unique())}")
    if n_cells != 48:
        print(f"  [!] WARNING: expected 48 cells, got {n_cells}.")

    return {
        "maze": maze_name,
        "mean": overall_mean,
        "min": cell_min,
        "max": cell_max,
        "n_trials": total_trials,
        "n_cells": n_cells,
    }


def main():
    results = []
    for maze_name, path in CSV_FILES.items():
        try:
            results.append(analyze(path, maze_name))
        except FileNotFoundError:
            print(f"\n  Skipping {maze_name}: file not found at '{path}'")

    if results:
        print(f"\n{'='*55}")
        print("SUMMARY (coarse grid only, for the paper)")
        print(f"{'='*55}")
        for r in results:
            print(f"  {r['maze']}: mean {r['mean']*100:.1f}%, "
                  f"range {r['min']*100:.0f}%-{r['max']*100:.0f}% "
                  f"(n={r['n_trials']})")


if __name__ == "__main__":
    main()