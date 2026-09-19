"""
Compute two DIFFERENT range statistics per maze, using only the
coarse-sweep factorial grid (step sizes 0.3-0.8), so the paper can
report them without conflating them:

  1. Individual-cell range:
     min and max success rate across all individual (step_size, random_rate)
     cells. This is the widest, most granular range (e.g. Maze 1 "62% to 87%").

  2. Column-mean range (per step-size):
     for each step size, average the success rate across all random_rate
     values (i.e. collapse each "column" of the heatmap to one number),
     then report the min and max of those column means. This is the
     narrower range that supports a statement like "the column means vary
     only between ~75% and ~82%."

Reporting both, clearly labeled, removes the inconsistency where a
column-mean claim was paired with individual-cell numbers.
"""

import pandas as pd

CSV_FILES = {
    "Maze 1 Original": "rrt_results_maze1_postfix.csv",
    "Maze 2 Original": "rrt_results_maze2_postfix.csv",
    "Maze 3 Original": "rrt_results_maze3_postfix.csv",
    "Maze 1 Tol 0.2" : "rrt_results_maze1_tol0.2.csv",
    "Maze 1 Tol 0.3" : "rrt_results_maze1_tol0.3.csv",
    "Maze 2 Tol 0.2" : "rrt_results_maze2_tol0.2.csv",
    "Maze 2 Tol 0.3" : "rrt_results_maze2_tol0.3.csv",
    "Maze 3 Tol 0.2" : "rrt_results_maze3_tol0.2.csv",
    "Maze 3 Tol 0.3" : "rrt_results_maze3_tol0.3.csv",
}

COARSE_STEPS = [0.3, 0.4, 0.45, 0.48, 0.5, 0.52, 0.55, 0.6, 0.7, 0.8]
TOL = 1e-9


def is_coarse_step(value):
    return any(abs(value - s) < TOL for s in COARSE_STEPS)


def analyze(path, maze_name):
    df = pd.read_csv(path)
    df["success"] = df["path_found"].astype(bool).astype(int)

    # coarse grid only
    coarse = df[df["step_size"].apply(is_coarse_step)].copy()

    # --- 1. Individual-cell success rates ---
    cell_rates = (
        coarse.groupby(["step_size", "random_rate"])["success"]
        .mean()
        .reset_index(name="cell_rate")
    )
    cell_min = cell_rates["cell_rate"].min()
    cell_max = cell_rates["cell_rate"].max()

    # --- 2. Column means (average over random_rate, per step size) ---
    col_means = (
        coarse.groupby("step_size")["success"]
        .mean()
        .reset_index(name="column_mean")
        .sort_values("step_size")
    )
    col_min = col_means["column_mean"].min()
    col_max = col_means["column_mean"].max()

    # --- 3. Row means (average over step_size, per random rate) ---
    row_means = (
        coarse.groupby("random_rate")["success"]
        .mean()
        .reset_index(name="row_mean")
        .sort_values("random_rate")
    )
    row_min = row_means["row_mean"].min()
    row_max = row_means["row_mean"].max()

    overall_mean = coarse["success"].mean()

    print(f"\n{'='*60}")
    print(f"{maze_name}")
    print(f"{'='*60}")
    print(f"  Overall mean success rate:      {overall_mean*100:.1f}%")
    print(f"  Individual-cell range:          {cell_min*100:.0f}% to {cell_max*100:.0f}%")
    print(f"  Column-mean range (per step):   {col_min*100:.0f}% to {col_max*100:.0f}%")
    print(f"  Row-mean range (per rr):        {row_min*100:.0f}% to {row_max*100:.0f}%")
    print(f"\n  Per-step-size column means:")
    for _, row in col_means.iterrows():
        print(f"    step {row['step_size']:.2f}:  {row['column_mean']*100:.1f}%")
    print(f"\n  Per-random-rate row means:")
    for _, row in row_means.iterrows():
        print(f"    rr {row['random_rate']:.1f}:    {row['row_mean']*100:.1f}%")

    return {
        "maze": maze_name,
        "overall_mean": overall_mean,
        "cell_range": (cell_min, cell_max),
        "col_range": (col_min, col_max),
        "row_range": (row_min, row_max),
    }


def main():
    results = []
    for maze_name, path in CSV_FILES.items():
        try:
            results.append(analyze(path, maze_name))
        except FileNotFoundError:
            print(f"\n  Skipping {maze_name}: file not found at '{path}'")

    if results:
        print(f"\n{'='*60}")
        print("SUMMARY (use these in the paper)")
        print(f"{'='*60}")
        for r in results:
            print(f"  {r['maze']}: "
                  f"mean {r['overall_mean']*100:.1f}%  |  "
                  f"cell range {r['cell_range'][0]*100:.0f}-{r['cell_range'][1]*100:.0f}%  |  "
                  f"column-mean range {r['col_range'][0]*100:.0f}-{r['col_range'][1]*100:.0f}%")


if __name__ == "__main__":
    main()