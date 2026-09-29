# Heading Intersection and Step-Size Effect in Goal-Biased RRT

Code and data for the paper *"Heading Intersection and Step-Size Effect in Goal-Biased RRT"* (Nguyen et al., submitted to IEEE Access).

The study runs a factorial experiment on goal-biased RRT in three 2D mazes and tests two things:

1. **Obstruction placement:** Maze 1 and Maze 2 have nearly identical wall length and structure. Maze 1 has four obstructions along the start-to-goal line; Maze 2 has the same four plus a fifth wall at y = 8 that closes the gap Maze 1 leaves open. Mean success falls from 77.8% (Maze 1) to 24.7% (Maze 2). Maze 3 matches Maze 2's obstruction count (five) with different positions and reaches 51.3%.
2. **Step-size peak:** success peaks locally near step size 0.5 in both obstructed mazes (2 and 3) and not in Maze 1. The peak persists when the goal tolerance is fixed independently of step size.

---

## Planner

`RRT_mazesolving.py` implements a standard holonomic RRT (LaValle, 1998):

- **Map:** 10 × 10, walls as line segments. Start (0, 0.5), goal (10, 9.5) in all mazes.
- **Sampling:** with probability `random_rate` a random point is sampled; otherwise the goal is used as the sample. Goal bias = 1 − `random_rate`. `random_rate = 1.0` is pure (unbiased) RRT.
- **Extension:** steer from the nearest node toward the sample by `step_size`; reject if the segment intersects a wall.
- **Success:** a new node lies within the goal tolerance of the goal and has a collision-free segment to it.
  - **Coupled criterion** (main sweep): tolerance = step size (τ = δ).
  - **Fixed criterion** (decoupling experiment): τ = 0.2 or τ = 0.3. The `goal_tolerance` column records the value used.
- **Budget:** 10,000 iterations per run (100,000 in the budget test).

Maze wall definitions are in the `Obstacle.default()` method. Set the walls and the output filename in the `__main__` block before running each maze.

---

## Experiments and data files

Every `rrt_results_*.csv` has **one row per run**. Main columns: `path_found` (success), `iterations`, `nodes_in_tree`, `path_length`, `step_size`, `random_rate`, `goal_tolerance` (fixed-tolerance and later runs only).

| Experiment | Files | Mazes | Step sizes | Random rates | Runs / cell | Criterion |
|---|---|---|---|---|---|---|
| Main sweep | `rrt_results_maze{1,2,3}_postfix.csv` | 1, 2, 3 | 0.3, 0.4, 0.45, 0.48, 0.5, 0.52, 0.55, 0.6, 0.7, 0.8 | 0.1–1.0 | 100 | Coupled |
| Fixed tolerance | `rrt_results_maze{1,2,3}_tol0.2.csv`, `..._tol0.3.csv` | 1, 2, 3 | 0.4–0.6 (fine sweep) | 0.1–1.0 | 100 | τ = 0.2 / 0.3 |
| n = 1000 validation | `rrt_results_maze{2,3}_power_n1000_coupled.csv` | 2, 3 | 0.4, 0.5, 0.6 | 0.1–1.0 | 1000 | Coupled |
| Budget test | `rrt_results_maze{2,3}_budget100k_coupled.csv` | 2, 3 | 0.3, 0.4 | 0.1–1.0 | 100 | Coupled, 100k cap |

Main sweep: 10 step sizes × 10 random rates × 100 runs = 10,000 runs per maze.

`rrt_results.csv`, `rrt_results_maze1.csv`, and `rrt_results_maze2.csv` are earlier runs, superseded by the `_postfix` files and **not used in the paper**.

---

## Analysis scripts

| Script | Produces | Paper |
|---|---|---|
| `logistic_model.py` | Interaction likelihood-ratio tests; `logistic_predicted_probabilities_*.csv` | Logistic table, predicted-probability table |
| `contrast_result.py` | `contrast_results.csv` (peak contrast + bootstrap CI) | Contrast table |
| `budget_table.py` | 10k vs 100k success rates | Budget table |
| `directional_consistency.py` | `directional_consistency.csv` | Directional-consistency table |
| `mean_iterations.py` | Iterations to solution, successful runs | Budget discussion |
| `compute_means.py`, `mean_columns.py`, `analyze_results.py` | Per-maze means and ranges | Descriptive statistics |

`logistic_model.py` fits one dataset per run: edit the file paths and the output filename (`_original`, `_tol0.2`, `_tol0.3`) at the top.

---

## Statistical settings

| Setting | Value |
|---|---|
| Logistic model | `success ~ C(maze)*C(step_size) + C(maze)*C(random_rate)` |
| Random rates in logistic model and contrast | rr = 1.0 excluded (`DROP_RR_1 = True`); 9 rates |
| Random rates in sign test | All 10 |
| Peak contrast | C = p(0.5) − ½[p(0.4) + p(0.6)], from model predictions averaged over random rate |
| Contrast CI | Run-level percentile bootstrap, B = 2000, seed = 0 |
| Sign test | Win = p(0.5) strictly above both p(0.4) and p(0.6) at a random rate (ties = non-wins); one-sided exact binomial vs. 1/3 |
| Sign-test data | Coupled Mazes 2 and 3: n = 1000 files; all other rows: n = 100 |
| Multiple comparisons (sign test) | Bonferroni over 9 tests, α = 0.0056 |
| Pairwise tests | Two-proportion z-test, peak (0.5) vs. each neighbor (0.4, 0.6), per random rate; Bonferroni and Benjamini–Hochberg within each family (coupled, τ = 0.2, τ = 0.3; 60 tests each) |

**Randomness:** simulation runs do not set a fixed seed, so re-running the planner gives statistically equivalent but not identical results. All analyses in the paper are computed from the CSV files in this repository.

---

## Setup

Python ≥ 3.12.

```bash
pip install numpy pandas matplotlib scipy statsmodels
```

Run an analysis from the repository root, e.g.:

```bash
python contrast_result.py
```

---

## Citation

```
D. A. Nguyen et al., "Heading Intersection and Step-Size Effect in Goal-Biased RRT,"
submitted to IEEE Access, 2026.
```
