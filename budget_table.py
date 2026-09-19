"""
budget_table.py

Compute mean success rate at the small step sizes (0.3, 0.4) under the
original 10k cap vs the 100k cap, per maze, for the budget-confound table.
Prints paste-ready LaTeX rows.
"""

import pandas as pd

# label -> (10k file, 100k file)
PAIRS = {
    "Maze 2": ("rrt_results_maze2_postfix.csv",
               "rrt_results_maze2_budget100k_coupled.csv"),
    "Maze 3": ("rrt_results_maze3_postfix.csv",
               "rrt_results_maze3_budget100k_coupled.csv"),
}

STEPS = [0.3, 0.4]
TOL = 1e-9


def mean_success(path, step):
    df = pd.read_csv(path)
    df["success"] = df["path_found"].astype(str).str.strip().str.lower().isin(["true", "1"]).astype(int)
    sub = df[(df["step_size"] - step).abs() < TOL]
    return sub["success"].mean() * 100, len(sub)


def main():
    rows = []
    for maze, (f10k, f100k) in PAIRS.items():
        for step in STEPS:
            try:
                m10, n10 = mean_success(f10k, step)
                m100, n100 = mean_success(f100k, step)
            except FileNotFoundError as e:
                print(f"  !! missing file for {maze} step {step}: {e}")
                continue
            delta = m100 - m10
            print(f"{maze}, step {step}: "
                  f"10k={m10:.1f}% (n={n10}), 100k={m100:.1f}% (n={n100}), "
                  f"delta={delta:+.1f}")
            rows.append((maze, step, m10, m100, delta))

    print("\n--- LaTeX rows (paste into tab:budget) ---")
    for maze, step, m10, m100, delta in rows:
        print(f"{maze} & {step:.1f} & {m10:.1f} & {m100:.1f} & ${delta:+.1f}$ \\\\")


if __name__ == "__main__":
    main()