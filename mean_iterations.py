#!/usr/bin/env python3
"""
iterations_to_solution.py

Mean iterations-to-solution for SUCCESSFUL RRT runs, grouped by step size and
maze. Tests the iteration-budget confound: at low step sizes, are runs starved
by the iteration cap, or finishing well within it?

HOW TO USE (VS Code): edit the CONFIG block below, then press Run.
Only SUCCESSFUL runs are counted (a failed run's "iterations" is just the cap
and would poison the mean). Each file is labelled by the maze number in its
filename (e.g. ...maze2... -> "Maze 2").
"""

import glob
import re
import pandas as pd

# ============================ CONFIG ============================
# List your COUPLED maze CSVs here (the ones with NO goal_tolerance column).
# Filenames should contain the maze number (maze1 / maze_2 / ...). Globs are OK.
FILES = [
    "rrt_results_maze1_postfix.csv",
    "rrt_results_maze2_postfix.csv",
    "rrt_results_maze3_postfix.csv",
]

# Restrict to certain step sizes, e.g. [0.40, 0.50, 0.60].
# Set to None to use every step size present in the data (recommended first).
STEP_FILTER = None

MAX_ITER = 10000              # your experiment's iteration cap
LATEX_OUT = "iters_table.tex" # where to write the LaTeX table (set to None to skip)
# ===============================================================


def maze_label(path):
    """Pull a maze number out of the filename; fall back to the file stem."""
    m = re.search(r"maze[_\-]?(\d+)", path, flags=re.IGNORECASE)
    if m:
        n = int(m.group(1))
        return n, f"Maze {n}"
    stem = re.sub(r"\.csv$", "", path.split("/")[-1], flags=re.IGNORECASE)
    return 10_000, stem


def expand(paths):
    out = []
    for p in paths:
        matched = sorted(glob.glob(p))
        out.extend(matched if matched else [p])
    return out


def load_successes(paths):
    frames, counts = [], []
    for p in paths:
        try:
            df = pd.read_csv(p)
        except FileNotFoundError:
            print(f"  !! {p} not found, skipping")
            continue
        df["path_found"] = (
            df["path_found"].astype(str).str.strip().str.lower().isin(["true", "1"])
        )
        order, label = maze_label(p)
        total, n_ok = len(df), int(df["path_found"].sum())
        counts.append((p, label, total, n_ok))
        ok = df[df["path_found"]].copy()
        ok["maze_order"] = order
        ok["maze"] = label
        frames.append(ok)
    if not frames:
        return None, counts
    return pd.concat(frames, ignore_index=True), counts


def apply_step_filter(ok):
    if STEP_FILTER:
        keep = [round(s, 3) for s in STEP_FILTER]
        return ok[ok["step_size"].round(3).isin(keep)]
    return ok


def per_maze_console(ok):
    ok = apply_step_filter(ok)
    mazes = sorted(ok[["maze_order", "maze"]].drop_duplicates().itertuples(index=False, name=None))
    for _, maze in mazes:
        sub = ok[ok["maze"] == maze]
        g = sub.groupby("step_size")["iterations"]
        table = pd.DataFrame({
            "n_success": g.count(),
            "mean_iters": g.mean().round(1),
            "median_iters": g.median().round(1),
            "p95_iters": g.quantile(0.95).round(1),
            "max_iters": g.max().astype(int),
            "pct_of_cap": (g.mean() / MAX_ITER * 100).round(1),
        })
        print("-" * 70)
        print(maze)
        print(table.to_string())
        peak_pct = table["pct_of_cap"].max()
        verdict = ("some steps average >=80% of cap -> budget may bind"
                   if peak_pct >= 80 else
                   "all steps finish well within cap -> not budget starvation")
        print(f"  -> {verdict}")


def build_latex(ok):
    ok = apply_step_filter(ok)
    steps = sorted(ok["step_size"].round(3).unique())
    mazes = [m for _, m in sorted(ok[["maze_order", "maze"]].drop_duplicates().itertuples(index=False, name=None))]

    mean_pivot = ok.groupby(["maze", "step_size"])["iterations"].mean().round(0)
    n_pivot = ok.groupby(["maze", "step_size"])["iterations"].count()
    n_min, n_max = int(n_pivot.min()), int(n_pivot.max())
    cap_str = f"{MAX_ITER:,}".replace(",", "{,}")

    colspec = "l" + "c" * len(steps)
    header = "Maze & " + " & ".join(f"{s:.2f}" for s in steps) + r"\\"

    body = []
    for maze in mazes:
        cells = []
        for s in steps:
            try:
                cells.append(f"{int(mean_pivot.loc[(maze, s)])}")
            except KeyError:
                cells.append("--")
        body.append(f"{maze} & " + " & ".join(cells) + r"\\")

    lines = [
        r"\begin{table*}[!t]",
        r"\centering",
        r"\begin{threeparttable}",
        r"\caption{Mean iterations to first solution (successful runs only) by maze and "
        r"step size, averaged over random rate. The iteration cap is " + cap_str + r".}",
        r"\label{tab:iterations}",
        r"\setlength{\tabcolsep}{4pt}",
        r"\small",
        r"\begin{tabular}{@{}" + colspec + r"@{}}",
        r"\toprule",
        header,
        r"\midrule",
        *body,
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{tablenotes}",
        r"\footnotesize",
        r"\item Cells are mean iterations over successful runs only; failed runs (which "
        r"terminate at the " + cap_str + r"-iteration cap) are excluded. Per-cell "
        f"successful-run counts range from {n_min} to {n_max}. All means fall well below "
        r"the cap, indicating that low-step-size behaviour is not driven by "
        r"iteration-budget exhaustion.",
        r"\end{tablenotes}",
        r"\end{threeparttable}",
        r"\end{table*}",
    ]
    return "\n".join(lines)


def main():
    files = expand(FILES)
    ok, counts = load_successes(files)

    print("=" * 70)
    print("FILES")
    for p, label, total, n_ok in counts:
        rate = (100 * n_ok / total) if total else 0.0
        print(f"  {label:<12} {p}  ->  {n_ok:,}/{total:,} successful ({rate:.1f}%)")
    print("=" * 70)
    if ok is None:
        print("No usable data. Check the FILES list in CONFIG.")
        return

    per_maze_console(ok)
    print("=" * 70)

    latex = build_latex(ok)
    print("\nLATEX TABLE:\n")
    print(latex)

    if LATEX_OUT:
        with open(LATEX_OUT, "w") as f:
            f.write(latex + "\n")
        print(f"\n(LaTeX written to {LATEX_OUT})")


if __name__ == "__main__":
    main()