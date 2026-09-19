"""
Logistic regression for the step-size effect.

Tests H12: does the step-size effect differ across mazes (the maze x step
interaction)? This is the global, principled test that replaces the
fragile pairwise comparisons.

Outcome: success (binary, path_found).
Predictors: maze, step_size, random_rate, and their interactions.

Fits TWO specifications:
  1. CATEGORICAL step size  -> makes no shape assumption, captures the peak
  2. QUADRATIC step size    -> single 'is there a peak' term (step^2)

Reports coefficients, p-values, confidence intervals, and a
likelihood-ratio test for the maze x step interaction (the H12 test).
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from scipy import stats

# ── STAGE 1: LOAD & COMBINE DATA ───────────────────────
# Fit the COUPLED (original) data as the primary model.
COUPLED_FILES = {
    "maze1": "rrt_results_maze1_tol0.3.csv",
    "maze2": "rrt_results_maze2_tol0.3.csv",
    "maze3": "rrt_results_maze3_tol0.3.csv",
}

# Optionally drop random_rate = 1.0 (the pure-undirected cliff) so the
# random_rate term is not misspecified. Set to True to exclude it.
DROP_RR_1 = True


def load_and_combine(files):
    frames = []
    for maze, path in files.items():
        df = pd.read_csv(path)
        df["success"] = df["path_found"].astype(bool).astype(int)
        df["maze"] = maze
        frames.append(df[["success", "maze", "step_size", "random_rate"]])
    data = pd.concat(frames, ignore_index=True)
    if DROP_RR_1:
        data = data[data["random_rate"] < 1.0 - 1e-9].copy()
    return data


def main():
    data = load_and_combine(COUPLED_FILES)
    print(f"Loaded {len(data)} trials across mazes: {sorted(data['maze'].unique())}")
    print(f"Step sizes: {sorted(data['step_size'].unique())}")
    print(f"Random rates: {sorted(data['random_rate'].unique())}")
    print(f"Overall success rate: {data['success'].mean():.3f}\n")

    # ── STAGE 2: FIT THE CATEGORICAL MODEL (primary) ───
    print("="*70)
    print("MODEL 1: CATEGORICAL step size (no shape assumption)")
    print("="*70)
    cat_full = smf.logit(
        "success ~ C(maze) * C(step_size) + C(maze) * C(random_rate)",
        data=data).fit(disp=False)
    print(cat_full.summary())

    # ── STAGE 3: LIKELIHOOD-RATIO TEST for maze x step ──
    # Fit a REDUCED model WITHOUT the maze x step interaction, then compare.
    # If dropping the interaction significantly worsens fit, the interaction
    # matters -> step-size sensitivity differs across mazes -> supports H12.
    cat_reduced = smf.logit(
        "success ~ C(maze) + C(step_size) + C(maze) * C(random_rate)",
        data=data).fit(disp=False)

    lr_stat = 2 * (cat_full.llf - cat_reduced.llf)
    df_diff = cat_full.df_model - cat_reduced.df_model
    p_value = stats.chi2.sf(lr_stat, df_diff)
    print("\n" + "="*70)
    print("LIKELIHOOD-RATIO TEST: maze x step-size interaction (H12)")
    print("="*70)
    print(f"  LR statistic = {lr_stat:.3f}")
    print(f"  df           = {int(df_diff)}")
    print(f"  p-value      = {p_value:.6f}")
    print(f"  -> {'SIGNIFICANT' if p_value < 0.05 else 'not significant'}: "
          f"step-size effect {'differs' if p_value < 0.05 else 'does not clearly differ'} across mazes")

    # ── STAGE 4: QUADRATIC MODEL (clean single peak term) ──
    print("\n" + "="*70)
    print("MODEL 2: QUADRATIC step size (step + step^2)")
    print("="*70)
    quad_full = smf.logit(
        "success ~ C(maze) * (step_size + I(step_size**2)) "
        "+ C(maze) * C(random_rate)",
        data=data).fit(disp=False)
    print(quad_full.summary())

    # LR test for the quadratic interaction (does CURVATURE differ by maze?)
    quad_reduced = smf.logit(
        "success ~ C(maze) * step_size + I(step_size**2) "
        "+ C(maze) * C(random_rate)",
        data=data).fit(disp=False)
    lr2 = 2 * (quad_full.llf - quad_reduced.llf)
    df2 = quad_full.df_model - quad_reduced.df_model
    p2 = stats.chi2.sf(lr2, df2)
    print("\n" + "="*70)
    print("LR TEST: maze x step^2 interaction (does the PEAK differ by maze?)")
    print("="*70)
    print(f"  LR statistic = {lr2:.3f}, df = {int(df2)}, p = {p2:.6f}")
    print(f"  -> {'SIGNIFICANT' if p2 < 0.05 else 'not significant'}")

    # ── STAGE 5: PREDICTED PROBABILITIES (the figure/table) ──
    print("\n" + "="*70)
    print("PREDICTED SUCCESS PROBABILITY by (maze, step size)")
    print("  (averaged over random rate, from the categorical model)")
    print("="*70)
    steps = sorted(data["step_size"].unique())
    rates = sorted(data["random_rate"].unique())
    rows = []
    for maze in sorted(data["maze"].unique()):
        for step in steps:
            grid = pd.DataFrame({
                "maze": maze, "step_size": step, "random_rate": rates})
            pred = cat_full.predict(grid).mean()
            rows.append({"maze": maze, "step_size": step, "pred_success": pred})
    pred_df = pd.DataFrame(rows)
    pivot = pred_df.pivot(index="maze", columns="step_size", values="pred_success")
    print((pivot * 100).round(1).to_string())

    pred_df.to_csv("logistic_predicted_probabilities_tol0.3.csv", index=False)
    print("\nPredicted probabilities saved to logistic_predicted_probabilities.csv")


if __name__ == "__main__":
    main()