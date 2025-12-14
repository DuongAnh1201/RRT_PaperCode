import matplotlib.pyplot as plt
import numpy as np

class Obstacle:
    def __init__(self, obstacle=None):
        self.obstacle = obstacle

    def default(self):
        if self.obstacle is None:
            # Format: [((x1, y1), (x2, y2)), ...]
            # Assumed Map Size: 10x10 area
            self.obstacle = [
    # --- Outer Boundary (with entry top-left and exit bottom-right) ---
    ((0, 0), (0, 10)),
    ((1, 10), (10, 10)),
    ((10, 10), (10, 1)),
    ((10, 0), (0, 0)),

    # --- Internal Walls (your original structure) ---
    ((1, 9), (4, 9)),
    ((4, 9), (4, 6)),
    ((4, 7), (6, 7)),
    ((6, 9), (9, 9)),
    ((8, 10), (8, 9.2)),

    ((1.5, 8), (3.5, 8)),
    ((1.5, 8), (1.5, 6.5)),
    ((3.5, 8), (3.5, 7)),
    ((1.5, 6.5), (2.5, 6.5)),

    ((5, 10), (5, 8.2)),
    ((6.5, 8), (6.5, 6)),
    ((7.5, 8.5), (7.5, 7.5)),
    ((9, 8), (9, 6.2)),

    ((0.8, 6), (3.2, 6)),
    ((3.2, 6), (3.2, 4)),
    ((3.2, 4), (6.8, 4)),
    ((6.8, 4), (6.8, 2)),
    ((2, 4), (2, 6.5)),

    ((2.8, 5.2), (2.8, 3.2)),
    ((4.8, 6.2), (4.8, 5)),
    ((5.8, 6.2), (5.8, 4.4)),
    ((7.2, 5.5), (7.2, 3.8)),

    ((0.5, 4.5), (2.5, 4.5)),
    ((1, 3.2), (2.2, 3.2)),
    ((1.2, 2.5), (1.2, 4 )),

    ((1.8, 3.2), (1.8, 1.8)),
    ((1.8, 1.8), (4.2, 1.8)),
    ((4.2, 1.8), (4.2, 3.6)),
    ((4.2, 3.6), (6.2, 3.6)),
    ((6.2, 3.6), (6.2, 2.4)),
    ((6.2, 2.4), (8.2, 2.4)),

    ((0.8, 2.2), (0.8, 0.8)),
    ((0.8, 2.2), (2.2, 2.2)),
    ((2.2, 2.2), (2.2, 0.8)),
    ((2.2, 0.8), (4.6, 0.8)),

    ((5.6, 1.6), (8.0, 1.6)),
    ((8.0, 1.6), (8.0, 3.2)),
    ((8.0, 3.2), (9.2, 3.2)),
    ((7.2, 0.8), (7.2, 2.0)),
    ((9.2, 4.2), (9.2, 6.2)),
    ((7.8, 5.2), (9.2, 5.2)),

    ((3.8, 2.8), (5.0, 2.8)),
    ((4.6, 4.8), (5.6, 4.8)),
    ((2.8, 7.2), (4.6, 7.2)),

    ((6.8, 7.8), (6.8, 7.0)),
    ((3.0, 0.8), (3.0, 1.8)),
    ((8.8, 0.8), (8.8, 1.4)),

    # ------------------------------------------------------
    # -------- ADDED OBSTACLES (Free-space difficulty) -----
    # ------------------------------------------------------

    # Top-left free region fillers
    ((0.8, 9.5), (2.2, 9.5)),
    ((2.2, 9.5), (2.2, 8.8)),
    ((0.8, 8.7), (1.8, 8.7)),

    # Mid-top open area (add navigation traps)
    ((5.5, 9.3), (7.2, 9.3)),
    ((7.2, 9.3), (7.2, 8.4)),
    ((5.6, 8.5), (6.4, 8.5)),

    # Upper-middle large empty zone
    ((2.0, 7.5), (2.0, 6.8)),
    ((2.0, 7.5), (3.0, 7.5)),
    ((3.0, 7.5), (3.0, 6.8)),
    ((6.0, 7.5), (6.0, 6.8)),
    ((6.0, 7.5), (7.0, 7.5)),

    # Center-top right open region
    ((7.8, 7.8), (9.0, 7.8)),
    ((8.4, 7.8), (8.4, 6.9)),

    # Middle slightly-empty corridor
    ((5.0, 5.5), (6.4, 5.5)),
    ((6.4, 5.5), (6.4, 4.9)),
    ((3.6, 5.0), (4.0, 5.0)),
    ((4.0, 5.0), (4.0, 4.4)),

    # Middle-right vertical chambers
    ((7.8, 4.6), (7.8, 3.4)),
    ((8.4, 4.6), (8.4, 3.9)),

    # Lower-middle small open space
    ((5.0, 3.0), (6.5, 3.0)),
    ((6.5, 3.0), (6.5, 2.6)),

    # Lower-left open area extra traps
    ((1.0, 2.0), (1.0, 1.2)),
    ((1.0, 1.2), (1.8, 1.2)),
    ((3.0, 1.4), (4.0, 1.4)),

    # Lower-right
    ((7.4, 1.0), (8.6, 1.0)),
    ((8.6, 1.0), (8.6, 1.8)),
    ((6.8, 2.1), (7.6, 2.1)),
]


        return self.obstacle


def visualize_maze(obstacles, map_size=10, title="Maze Visualization", 
                   show_start_goal=False, start_pos=None, goal_pos=None,
                   figsize=(10, 10), save_path=None):
    """
    Visualize the maze with obstacles.
    
    Args:
        obstacles: List of obstacle line segments in format [((x1, y1), (x2, y2)), ...]
                  or an Obstacle object
        map_size: Size of the map (default: 10)
        title: Title of the plot
        show_start_goal: Whether to show start and goal positions
        start_pos: Tuple (x, y) of start position
        goal_pos: Tuple (x, y) of goal position
        figsize: Figure size (width, height)
        save_path: Path to save the figure (optional)
    """
    # Handle Obstacle object or list
    if hasattr(obstacles, 'obstacle'):
        obstacle_list = obstacles.obstacle
    else:
        obstacle_list = obstacles
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw obstacles
    if obstacle_list:
        for obstacle in obstacle_list:
            point1, point2 = obstacle
            x1, y1 = point1
            x2, y2 = point2
            ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2.5, label='Obstacles' if obstacle == obstacle_list[0] else '')
    
    # Draw start and goal if provided
    if show_start_goal:
        if start_pos:
            ax.scatter(start_pos[0], start_pos[1], c='green', s=300, 
                      marker='o', edgecolors='darkgreen', linewidths=2, 
                      zorder=5, label='Start')
        if goal_pos:
            ax.scatter(goal_pos[0], goal_pos[1], c='red', s=300, 
                      marker='*', edgecolors='darkred', linewidths=2, 
                      zorder=5, label='Goal')
    
    # Set plot properties
    ax.set_xlim(-0.5, map_size + 0.5)
    ax.set_ylim(-0.5, map_size + 0.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Add legend if start/goal are shown
    if show_start_goal and (start_pos or goal_pos):
        ax.legend(loc='upper right', fontsize=10)
    
    # Add info text
    info_text = f"Map Size: {map_size}x{map_size}\n"
    info_text += f"Number of Obstacles: {len(obstacle_list) if obstacle_list else 0}"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Maze visualization saved to {save_path}")
    
    return fig, ax


def visualize_maze_with_path(obstacles, path=None, map_size=10, 
                             title="Maze with Path", start_pos=None, 
                             goal_pos=None, figsize=(10, 10), save_path=None):
    """
    Visualize the maze with obstacles and optional path.
    
    Args:
        obstacles: List of obstacle line segments or Obstacle object
        path: List of path points in format [[x1, y1], [x2, y2], ...] (optional)
        map_size: Size of the map
        title: Title of the plot
        start_pos: Tuple (x, y) of start position
        goal_pos: Tuple (x, y) of goal position
        figsize: Figure size
        save_path: Path to save the figure (optional)
    """
    # Handle Obstacle object or list
    if hasattr(obstacles, 'obstacle'):
        obstacle_list = obstacles.obstacle
    else:
        obstacle_list = obstacles
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw obstacles
    if obstacle_list:
        for obstacle in obstacle_list:
            point1, point2 = obstacle
            x1, y1 = point1
            x2, y2 = point2
            ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2.5, 
                   label='Obstacles' if obstacle == obstacle_list[0] else '')
    
    # Draw path if provided
    if path and len(path) > 0:
        path_x = [point[0] for point in path]
        path_y = [point[1] for point in path]
        ax.plot(path_x, path_y, 'r-', linewidth=3, zorder=4, label='Path')
        ax.scatter(path_x, path_y, c='red', s=30, zorder=5, 
                  edgecolors='darkred', linewidths=1, alpha=0.7)
    
    # Draw start and goal
    if start_pos:
        ax.scatter(start_pos[0], start_pos[1], c='green', s=300, 
                  marker='o', edgecolors='darkgreen', linewidths=2, 
                  zorder=6, label='Start')
    if goal_pos:
        ax.scatter(goal_pos[0], goal_pos[1], c='red', s=300, 
                  marker='*', edgecolors='darkred', linewidths=2, 
                  zorder=6, label='Goal')
    
    # Set plot properties
    ax.set_xlim(-0.5, map_size + 0.5)
    ax.set_ylim(-0.5, map_size + 0.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Maze visualization saved to {save_path}")
    
    return fig, ax


# Example usage
if __name__ == "__main__":
    # Create obstacles
    obstacles = Obstacle()
    obstacles.default()
    
    # Visualize just the maze
    print("Visualizing maze...")
    fig1, ax1 = visualize_maze(obstacles, map_size=10, 
                               title="Maze Layout",
                               show_start_goal=True,
                               start_pos=(0.5, 9.5),
                               goal_pos=(10, 0))
    plt.show()
    
    # Example with a sample path
    sample_path = [
        [0.5, 9.5], [0.5, 8.0], [1.0, 7.0], [2.0, 6.0],
        [3.0, 5.0], [4.0, 4.0], [5.0, 3.0], [6.0, 2.0],
        [7.0, 1.0], [8.0, 0.5], [9.0, 0.2], [10, 0]
    ]
    
    print("\nVisualizing maze with path...")
    fig2, ax2 = visualize_maze_with_path(obstacles, path=sample_path,
                                         map_size=10,
                                         title="Maze with Sample Path",
                                         start_pos=(0.5, 9.5),
                                         goal_pos=(10, 0))
    plt.show()

