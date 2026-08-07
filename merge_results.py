import pandas as pd

# Define pairs to merge: {output_file: (file_a, file_b)}
MERGE_PAIRS = {
    "rrt_results_maze1_final.csv": ("rrt_results_maze1.csv", "rrt_results_maze1_0.9rr.csv"),
    "rrt_results_maze2_final.csv": ("rrt_results_maze2.csv", "rrt_results_maze2_0.9rr.csv"),
    "rrt_results_maze3_final.csv": ("rrt_results_maze3.csv", "rrt_results_maze3_0.9rr.csv"),
}


def merge_csv_files():
    for output, (file_a, file_b) in MERGE_PAIRS.items():
        df_a = pd.read_csv(file_a)
        df_b = pd.read_csv(file_b)
        print(f"  {file_a}: {len(df_a)} rows")
        print(f"  {file_b}: {len(df_b)} rows")

        merged = pd.concat([df_a, df_b], ignore_index=True)
        merged.to_csv(output, index=False)
        print(f"  -> Merged into {output}: {len(merged)} rows\n")


if __name__ == "__main__":
    merge_csv_files()
