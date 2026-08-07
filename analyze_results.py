import pandas as pd
import glob


def analyze_file(filepath):
    data = pd.read_csv(filepath)

    total_runs = len(data)
    total_successes = data["path_found"].sum()
    success_rate = total_successes / total_runs * 100

    print(f"=== {filepath} ===")
    print(f"Total runs:          {total_runs}")
    print(f"Total successes:     {total_successes}")
    print(f"Overall success rate: {success_rate:.1f}%")

    print("\nSuccess rate by step size:")
    step_rates = data.groupby("step_size")["path_found"].mean() * 100
    print("step_size")
    for step, rate in step_rates.items():
        print(f"{step}    {rate:.1f}%")

    print("\nSuccess rate by random rate:")
    rand_rates = data.groupby("random_rate")["path_found"].mean() * 100
    print("random_rate")
    for rand, rate in rand_rates.items():
        print(f"{rand}    {rate:.1f}%")

    successful = data[data["path_found"] == True]
    print("\nAmong successful runs:")
    print(f"  Mean iterations:   {successful['iterations'].mean():.0f}")
    print(f"  Mean path length:  {successful['path_length'].mean():.2f}")
    print(f"  Mean path nodes:   {successful['path_nodes'].mean():.0f}")
    print()


def analyze_rrt_results():
    csv_files = sorted(glob.glob("rrt_results_*.csv"))

    if not csv_files:
        print("No CSV files found matching 'rrt_results_*.csv'")
        return

    for f in csv_files:
        analyze_file(f)


if __name__ == "__main__":
    analyze_rrt_results()
