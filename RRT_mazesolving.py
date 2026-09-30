import random
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import csv
from datetime import datetime
import os
from testmazes import obstacles as MAZES
import pandas as pd

class Obstacle:
    def __init__(self, obstacle=None):
        self.obstacle = obstacle

    def default(self):
        if self.obstacle is None:
            # Format: [((x1, y1), (x2, y2)), ...]
            # Assumed Map Size: 10x10 area
            self.obstacle =[
        # --- Outer Boundary (entry: bottom-left, exit: top-right) ---
        ((0, 0), (10, 0)),
        ((0, 1), (0, 10)),
        ((0, 10), (10, 10)),
        ((10, 0), (10, 9)),
 
        # --- Internal Walls — horizontal ---
        ((2, 1), (3, 1)), ((5, 1), (8, 1)), ((1, 2), (3, 2)),
        ((6, 2), (7, 2)), ((8, 2), (9, 2)), ((2, 3), (4, 3)),
        ((5, 3), (6, 3)), ((7, 3), (8, 3)), ((4, 4), (5, 4)),
        ((6, 4), (7, 4)), ((8, 4), (10, 4)), ((5, 5), (6, 5)),
        ((7, 5), (8, 5)), ((1, 6), (3, 6)), ((4, 6), (5, 6)),
        ((6, 6), (7, 6)), ((8, 6), (9, 6)), ((2, 7), (4, 7)),
        ((9, 7), (10, 7)), ((1, 8), (3, 8)), ((6, 8), (7, 8)),
        ((3, 9), (5, 9)), ((7, 9), (9, 9)),
 
        # --- Internal Walls — vertical ---
        ((1, 2), (1, 4)), ((1, 6), (1, 7)), ((2, 3), (2, 5)),
        ((2, 9), (2, 10)), ((3, 4), (3, 5)), ((3, 7), (3, 8)),
        ((4, 2), (4, 3)), ((4, 8), (4, 9)), ((5, 1), (5, 4)),
        ((5, 5), (5, 7)), ((6, 3), (6, 4)), ((6, 6), (6, 7)),
        ((6, 8), (6, 9)), ((7, 4), (7, 5)), ((7, 7), (7, 9)),
        ((8, 1), (8, 2)), ((8, 3), (8, 4)), ((8, 6), (8, 7)),
        ((9, 2), (9, 3)), ((9, 4), (9, 5)), ((9, 7), (9, 9)),
    ]

        return self.obstacle

# Initialize obstacles global for default param usage
obs = Obstacle()
obs.default()  

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.cost = 0

class RRT:
    def __init__(self, start, goal, map_size, obstacle=obs, iter=500, step_size=1, random_rate = 0.1):
        self._start = start
        self._goal = goal
        self._map_size = map_size
        self._obstacle = obstacle
        self._node_list = [self._start]
        self._goal_reached = False
        self._path = None
        self._max_iter = iter
        self.step_size = step_size
        self._obstacle_lines = self.obs_to_line()
        self._random_rate = random_rate
        self._iterations_used = 0
        self._rejected_nodes = []
    
    def random_node(self):
        """Generate a random node in the map."""
        if random.random() <= self._random_rate:
            rand_node = Node(random.randint(0, self._map_size), random.randint(0, self._map_size))
        else:
            rand_node = Node(self._goal.x, self._goal.y)
        return rand_node

    def nearest_node(self, node_list, rand_node):
        """Find the nearest node in the tree to the random node"""
        distances = [np.linalg.norm([node.x - rand_node.x, node.y - rand_node.y]) for node in node_list]
        nearest_node = node_list[np.argmin(distances)]
        return nearest_node
    
    def plan(self, goal_tolerance=None):
        """Main RRT planning loop"""
        for i in range(self._max_iter):
            rand_node = self.random_node()
            nearest_node = self.nearest_node(self._node_list, rand_node)
            new_node = self.steer(nearest_node, rand_node)

            if self.is_collision_free(nearest_node, new_node):
                new_node.parent = nearest_node
                self._node_list.append(new_node)

                if self.reached_goal(new_node, goal_tolerance):
                    self._path = self.generate_final_path(new_node)
                    self._goal_reached = True
                    self._iterations_used = i + 1
                    return
            else:
                self._rejected_nodes.append(new_node)
        self._iterations_used = self._max_iter
    
    def steer(self, from_node, to_node):
        """Steer from one node to another, step-by-step."""
        dist = math.hypot(to_node.x - from_node.x, to_node.y - from_node.y)

        if dist < self.step_size:
            # If target is close, just go there!
            new_x = to_node.x
            new_y = to_node.y
            cost_increment = dist
        else:
            # If target is far, Step forward by step_size
            theta = math.atan2(to_node.y - from_node.y, to_node.x - from_node.x)
            new_x = from_node.x + self.step_size * math.cos(theta)
            new_y = from_node.y + self.step_size * math.sin(theta)
            cost_increment = self.step_size
        
        new_node = Node(new_x, new_y)
        new_node.cost = from_node.cost + cost_increment
        return new_node

    def obs_to_line(self):
        """Convert obstacle line segments to line equations (a, b) where y = ax + b.
        Vertical lines are marked as (inf, x_intercept)."""
        res = []
        obstacles = self._obstacle.obstacle if hasattr(self._obstacle, 'obstacle') else self._obstacle
        
        for (m, n) in obstacles:
            m_x, m_y = m
            n_x, n_y = n
            
            # Vertical line
            if m_x == n_x:
                res.append((float('inf'), m_x))   # a = inf, b = x-intercept
            else:
                a = (m_y - n_y) / (m_x - n_x)
                b = m_y - m_x * a
                res.append((a, b))
        
        return res

    def is_intersection(self, seg_a, seg_b, node):
        """Check if point `node` lies within the bounding box of segment endpoints seg_a and seg_b.
        Accepts seg_a and seg_b as either tuples (x, y) or Node objects."""
        # Handle both tuple and Node formats
        if isinstance(seg_a, tuple):
            x_a, y_a = seg_a
        else:
            x_a, y_a = seg_a.x, seg_a.y
        
        if isinstance(seg_b, tuple):
            x_b, y_b = seg_b
        else:
            x_b, y_b = seg_b.x, seg_b.y
        
        x = node.x
        y = node.y
        
        # Check if point is within the bounds (with small epsilon for float errors)
        return (
            min(x_a, x_b) - 1e-6 <= x <= max(x_a, x_b) + 1e-6 and
            min(y_a, y_b) - 1e-6 <= y <= max(y_a, y_b) + 1e-6
        )

    def is_collision_free(self, from_node, to_node):
        """Check if the path segment from from_node to to_node intersects any obstacle line segment."""
        obstacles = self._obstacle.obstacle if hasattr(self._obstacle, 'obstacle') else self._obstacle
        if not obstacles:
            return True

        res = self._obstacle_lines

        # Path line equation
        if abs(from_node.x - to_node.x) < 1e-6:
            a = float('inf')  # vertical line
            b = from_node.x
        else:
            a = (from_node.y - to_node.y) / (from_node.x - to_node.x)
            b = from_node.y - from_node.x * a

        # Check against every obstacle
        for i in range(len(obstacles)):
            (m, n) = obstacles[i]
            m_x, m_y = m
            n_x, n_y = n
            a_i, b_i = res[i]

            intersect_node = None

            # -------- CASE 1: BOTH LINES VERTICAL --------
            if a == float('inf') and a_i == float('inf'):
                if abs(b - b_i) < 1e-6:  # same x = constant line
                    # Check y-range overlap
                    if not (max(from_node.y, to_node.y) < min(m_y, n_y) or
                            min(from_node.y, to_node.y) > max(m_y, n_y)):
                        return False
                continue

            # -------- CASE 2: PATH VERTICAL, OBSTACLE NON-VERTICAL --------
            elif a == float('inf') and a_i != float('inf'):
                x = b
                y = a_i * x + b_i
                intersect_node = Node(x, y)

            # -------- CASE 3: OBSTACLE VERTICAL, PATH NON-VERTICAL --------
            elif a_i == float('inf') and a != float('inf'):
                x = b_i
                y = a * x + b
                intersect_node = Node(x, y)

            # -------- CASE 4: BOTH NON-VERTICAL --------
            else:
                if abs(a - a_i) < 1e-6:
                    # Parallel lines
                    continue
                else:
                    # Compute true intersection point
                    x = (b_i - b) / (a - a_i)
                    y = a * x + b
                    intersect_node = Node(x, y)

            # [FIXED LOGIC] If we found an intersection point, we must check if it lies 
            # on BOTH the path segment AND the obstacle segment.
            if intersect_node:
                on_path = self.is_intersection(from_node, to_node, intersect_node)
                on_obstacle = self.is_intersection(m, n, intersect_node)
                
                if on_path and on_obstacle:
                    return False

        return True
    
    def reached_goal(self, node, goal_tolerance=None):
        """Check if the node has reached the goal."""
        if goal_tolerance is None:
            goal_tolerance = self.step_size
        dist = math.hypot(node.x - self._goal.x, node.y - self._goal.y)
        return dist <= goal_tolerance and self.is_collision_free(node, self._goal)

    def generate_final_path(self, goal_node):
        """Generate the final path from the start to the goal."""
        path = []
        node = goal_node
        while node is not None:
            path.append([node.x, node.y])
            node = node.parent
        return path[::-1]  # Reverse the path
    
    def get_path_length(self):
        """Calculate the total path length if path exists."""
        if self._path is None or len(self._path) < 2:
            return 0.0
        total_length = 0.0
        for i in range(len(self._path) - 1):
            dx = self._path[i+1][0] - self._path[i][0]
            dy = self._path[i+1][1] - self._path[i][1]
            total_length += math.hypot(dx, dy)
        return total_length
    
    def save_run_data(self, filename="rrt_results.csv", start_pos=None, goal_pos=None, goal_tolerance=None):
        """
        Save the current run's data to a CSV file.

        Args:
            filename: Name of the CSV file to save to (default: "rrt_results.csv")
            start_pos: Tuple (x, y) of start position (optional, will use self._start if not provided)
            goal_pos: Tuple (x, y) of goal position (optional, will use self._goal if not provided)
            goal_tolerance: Goal tolerance used for this run
        """
        # Get positions
        if start_pos is None:
            start_pos = (self._start.x, self._start.y)
        if goal_pos is None:
            goal_pos = (self._goal.x, self._goal.y)
        if goal_tolerance is None:
            goal_tolerance = self.step_size

        # Calculate path length
        path_length = self.get_path_length() if self._goal_reached else 0.0

        # Generate unique key for linking CSV and image
        unique_key = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds

        # Prepare data
        data = {
            'run_key': unique_key,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'path_found': self._goal_reached,
            'iterations': self._iterations_used,
            'nodes_in_tree': len(self._node_list),
            'path_length': path_length,
            'path_nodes': len(self._path) if self._path else 0,
            'step_size': self.step_size,
            'random_rate': self._random_rate,
            'goal_tolerance': goal_tolerance,
            'start_x': start_pos[0],
            'start_y': start_pos[1],
            'goal_x': goal_pos[0],
            'goal_y': goal_pos[1],
            'map_size': self._map_size,
            'image_filename': f"rrt_{unique_key}.png"
        }

        # Check if file exists to determine if we need headers
        file_exists = os.path.isfile(filename)

        # Write to CSV
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ['run_key', 'timestamp', 'path_found', 'iterations', 'nodes_in_tree',
                         'path_length', 'path_nodes', 'step_size', 'random_rate', 'goal_tolerance',
                         'start_x', 'start_y', 'goal_x', 'goal_y', 'map_size', 'image_filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            # Write data row
            writer.writerow(data)

        print(f"✓ Run data saved to {filename} (Key: {unique_key})")
        return data
    
    def save_figure(self, fig, image_filename, folder="rrt_results_maze3_postfix"):
        """
        Save the matplotlib figure to a folder.
        
        Args:
            fig: Matplotlib figure object
            image_filename: Name of the image file
            folder: Folder name to save images (default: "rrt_images")
        """
        # Create folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✓ Created folder: {folder}")
        
        # Full path for the image
        image_path = os.path.join(folder, image_filename)
        
        # Save the figure
        fig.savefig(image_path, dpi=150, bbox_inches='tight')
        print(f"✓ Chart saved to {image_path}")
        return image_path
    
    def visualize(self, title="RRT Path Planning", show_tree=True, show_path=True,
                  figsize=(10, 10), save_image=False, image_filename=None, image_folder="rrt_images"):
        """
        Visualize the RRT tree, obstacles, start, goal, and path.
        
        Args:
            title: Title of the plot
            show_tree: Whether to show the RRT tree
            show_path: Whether to show the final path
            figsize: Figure size (width, height)
            save_image: Whether to save the image
            image_filename: Name of the image file (if None, will be generated)
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get obstacles
        obstacles = self._obstacle.obstacle if hasattr(self._obstacle, 'obstacle') else self._obstacle
        
        # Draw obstacles
        if obstacles:
            for obstacle in obstacles:
                point1, point2 = obstacle
                x1, y1 = point1
                x2, y2 = point2
                ax.plot([x1, x2], [y1, y2], 'k-', linewidth=3, label='Obstacles' if obstacle == obstacles[0] else '')
        
        # Draw rejected (collision-blocked) nodes
        if self._rejected_nodes:
            rej_x = [node.x for node in self._rejected_nodes]
            rej_y = [node.y for node in self._rejected_nodes]
            ax.scatter(rej_x, rej_y, c='orange', s=8, alpha=0.4,
                      edgecolors='none', zorder=1, label='Rejected Nodes')

        # Draw RRT tree
        if show_tree and self._node_list:
            for node in self._node_list[1:]:
                if node.parent is not None:
                    ax.plot([node.parent.x, node.x], [node.parent.y, node.y], 
                           'lightblue', linewidth=0.5, alpha=0.6, zorder=1)
            
            node_x = [node.x for node in self._node_list]
            node_y = [node.y for node in self._node_list]
            ax.scatter(node_x, node_y, c='lightblue', s=20, alpha=0.6, 
                      edgecolors='blue', linewidths=0.5, zorder=2, label='RRT Nodes')
        
        # Draw final path if found
        if show_path and self._path is not None:
            path_x = [point[0] for point in self._path]
            path_y = [point[1] for point in self._path]
            ax.plot(path_x, path_y, 'r-', linewidth=3, zorder=5, label='Final Path')
            ax.scatter(path_x, path_y, c='red', s=50, zorder=6, edgecolors='darkred', linewidths=1.5)
        
        # Draw start node
        ax.scatter(self._start.x, self._start.y, c='green', s=200, 
                  marker='o', edgecolors='darkgreen', linewidths=2, 
                  zorder=7, label='Start')
        
        # Draw goal node
        ax.scatter(self._goal.x, self._goal.y, c='red', s=200, 
                  marker='*', edgecolors='darkred', linewidths=2, 
                  zorder=7, label='Goal')
        
        # Set plot properties
        ax.set_xlim(-1, self._map_size + 1)
        ax.set_ylim(-1, self._map_size + 1)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=10)
        
        # Add info text
        info_text = f"Iterations: {self._iterations_used}\n"
        info_text += f"Nodes (tree): {len(self._node_list)}\n"
        info_text += f"Nodes (rejected): {len(self._rejected_nodes)}\n"
        info_text += f"Goal Reached: {'Yes' if self._goal_reached else 'No'}"
        if self._path is not None:
            path_length = sum(math.hypot(self._path[i+1][0] - self._path[i][0], 
                                       self._path[i+1][1] - self._path[i][1]) 
                            for i in range(len(self._path)-1))
            info_text += f"\nPath Length: {path_length:.2f}"
        
        # [FIXED SYNTAX] Removed invalid type hinting syntax for bbox dict
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # Save image if requested
        if save_image:
            if image_filename is None:
                image_filename = f"rrt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}.png"
            self.save_figure(fig, image_filename, folder=image_folder)
        
        return fig, ax
    
    # def visualize_animation(self, step=10, title="RRT Path Planning Animation", figsize=(10, 10), random_rate= 0.5):
    #     """
    #     Visualize the RRT tree growth step by step.
    #     """
    #     fig, ax = plt.subplots(figsize=figsize)
        
    #     obstacles = self._obstacle.obstacle if hasattr(self._obstacle, 'obstacle') else self._obstacle
        
    #     if obstacles:
    #         for obstacle in obstacles:
    #             point1, point2 = obstacle
    #             x1, y1 = point1
    #             x2, y2 = point2
    #             ax.plot([x1, x2], [y1, y2], 'k-', linewidth=3)
        
    #     previous_node_count = 1
        
    #     ax.scatter(self._start.x, self._start.y, c='green', s=200, 
    #               marker='o', edgecolors='darkgreen', linewidths=2, zorder=7, label='Start')
    #     ax.scatter(self._goal.x, self._goal.y, c='red', s=200, 
    #               marker='*', edgecolors='darkred', linewidths=2, zorder=7, label='Goal')
        
    #     for i in range(self._max_iter):
    #         rand_node = self.random_node(random_rate)
    #         nearest_node = self.nearest_node(self._node_list, rand_node)
    #         new_node = self.steer(nearest_node, rand_node)

    #         if new_node and self.is_collision_free(nearest_node, new_node):
    #             new_node.parent = nearest_node
    #             self._node_list.append(new_node)
                
    #             ax.plot([nearest_node.x, new_node.x], [nearest_node.y, new_node.y], 
    #                    'lightblue', linewidth=0.5, alpha=0.6, zorder=1)
    #             ax.scatter(new_node.x, new_node.y, c='lightblue', s=20, alpha=0.6, 
    #                       edgecolors='blue', linewidths=0.5, zorder=2)
                
    #             if len(self._node_list) - previous_node_count >= step:
    #                 ax.set_title(f"{title} - Iteration {i+1}, Nodes: {len(self._node_list)}", 
    #                            fontsize=14, fontweight='bold')
    #                 plt.pause(0.01)
    #                 previous_node_count = len(self._node_list)
            
    #         if new_node and self.reached_goal(new_node):
    #             self._path = self.generate_final_path(new_node)
    #             self._goal_reached = True
                
    #             path_x = [point[0] for point in self._path]
    #             path_y = [point[1] for point in self._path]
    #             ax.plot(path_x, path_y, 'r-', linewidth=3, zorder=5, label='Final Path')
    #             ax.scatter(path_x, path_y, c='red', s=50, zorder=6, edgecolors='darkred', linewidths=1.5)
                
    #             ax.set_title(f"{title} - Goal Reached! Iteration {i+1}", 
    #                        fontsize=14, fontweight='bold', color='green')
    #             plt.pause(0.1)
    #             break
        
    #     ax.set_xlim(-1, self._map_size + 1)
    #     ax.set_ylim(-1, self._map_size + 1)
    #     ax.set_aspect('equal')
    #     ax.grid(True, alpha=0.3, linestyle='--')
    #     ax.set_xlabel('X', fontsize=12)
    #     ax.set_ylabel('Y', fontsize=12)
    #     ax.legend(loc='upper right', fontsize=10)
    #     plt.tight_layout()
    #     return fig, ax

# def visualize_rrt_example(random_rate):
#     """
#     Example function demonstrating how to use RRT with visualization.
#     """
#     obstacles = Obstacle()
#     obstacles.default()
    
#     start_node = Node(0.5, 9.5)
#     goal_node = Node(10, 0)
#     map_size = 10
    
#     rrt = RRT(start=start_node, 
#             goal=goal_node, 
#             map_size=map_size, 
#             obstacle=obstacles, 
#             iter=50000, 
#             step_size=0.3,
#             random_rate= 0.1)
    
#     print("Running RRT path planning...")
#     rrt.plan()
    
#     # Save run data (this generates a unique key and image filename)
#     data = rrt.save_run_data("rrt_results.csv", 
#                              start_pos=(start_node.x, start_node.y),
#                              goal_pos=(goal_node.x, goal_node.y))
    
#     # Get the image filename from the saved data
#     image_filename = data['image_filename']
    
#     if rrt._goal_reached:
#         print(f"✓ Goal reached! Path found with {len(rrt._path)} nodes.")
#         fig, ax = rrt.visualize(title="RRT Maze Solving - Final Result", 
#                                save_image=True, image_filename=image_filename)
#         plt.show()
#     else:
#         print("✗ Goal not reached. Showing current tree:")
#         fig, ax = rrt.visualize(title="RRT Maze Solving - No Path Found",
#                                save_image=True, image_filename=image_filename)
#         plt.show()
    
#     return rrt

def run_multiple_experiments(num_runs=3, start_pos=(0.5, 9.5), goal_pos=(10, 0),
                             map_size=10, max_iter=50000, step_size=0.3, random_rate=0.1,
                             goal_tolerance=None, obstacle_list=None,
                             visualize=False, save_file="rrt_results.csv",
                             image_folder="rrt_images"):
    """
    Run multiple RRT experiments and save all results.

    Args:
        num_runs: Number of experiments to run
        start_pos: Tuple (x, y) of start position
        goal_pos: Tuple (x, y) of goal position
        map_size: Size of the map
        max_iter: Maximum iterations per run
        step_size: Step size for RRT
        random_rate: Random sampling rate
        goal_tolerance: Tolerance for reaching the goal (default: step_size)
        obstacle_list: List of obstacle segments (default: built-in maze)
        visualize: Whether to show visualization (only shows last run)
        save_file: CSV file to save results to
        image_folder: Folder to save images to
    """
    if obstacle_list is not None:
        obstacles = Obstacle(obstacle_list)
        obstacles.default()
    else:
        obstacles = Obstacle()
        obstacles.default()

    results = []
    success_count = 0

    print(f"Running {num_runs} experiments...")
    print("-" * 60)

    for run_num in range(1, num_runs + 1):
        print(f"Run {run_num}/{num_runs}...", end=" ")

        start_node = Node(start_pos[0], start_pos[1])
        goal_node = Node(goal_pos[0], goal_pos[1])

        rrt = RRT(start=start_node,
                 goal=goal_node,
                 map_size=map_size,
                 obstacle=obstacles,
                 iter=max_iter,
                 step_size=step_size,
                 random_rate=random_rate)

        rrt.plan(goal_tolerance=goal_tolerance)

        # Save data (this generates a unique key and image filename)
        data = rrt.save_run_data(save_file, start_pos, goal_pos, goal_tolerance=goal_tolerance)
        results.append(data)

        # Get the image filename from the saved data
        image_filename = data['image_filename']

        if rrt._goal_reached:
            success_count += 1
            print(f"✓ Success (Path length: {data['path_length']:.2f}, Nodes: {data['nodes_in_tree']})")
        else:
            print(f"✗ Failed (Nodes: {data['nodes_in_tree']})")

        # Save image for this run
        if rrt._goal_reached:
            fig, ax = rrt.visualize(title=f"RRT Run {run_num} - Final Result",
                                   save_image=True, image_filename=image_filename,
                                   image_folder=image_folder)
        else:
            fig, ax = rrt.visualize(title=f"RRT Run {run_num} - No Path Found",
                                   save_image=True, image_filename=image_filename,
                                   image_folder=image_folder)

        # Close figure to free memory (only show if it's the last run and visualize=True)
        if visualize and run_num == num_runs:
            plt.show()
        else:
            plt.close(fig)

    # Print summary statistics
    print("-" * 60)
    print(f"Summary Statistics ({num_runs} runs):")
    print(f"  Success Rate: {success_count}/{num_runs} ({100*success_count/num_runs:.1f}%)")

    if success_count > 0:
        successful_runs = [r for r in results if r['path_found']]
        avg_path_length = sum(r['path_length'] for r in successful_runs) / len(successful_runs)
        avg_nodes = sum(r['nodes_in_tree'] for r in successful_runs) / len(successful_runs)
        avg_path_nodes = sum(r['path_nodes'] for r in successful_runs) / len(successful_runs)

        print(f"  Average Path Length: {avg_path_length:.2f}")
        print(f"  Average Nodes in Tree: {avg_nodes:.0f}")
        print(f"  Average Path Nodes: {avg_path_nodes:.0f}")

    avg_all_nodes = sum(r['nodes_in_tree'] for r in results) / len(results)
    print(f"  Average Nodes (all runs): {avg_all_nodes:.0f}")
    print(f"  Results saved to: {save_file}")

    return results


if __name__ == "__main__":
    # ─── Resume power runs for Maze 3 (n=1000, coupled) ───
    step_sizes = [0.4, 0.5, 0.6]
    random_rates = [r / 10 for r in range(1, 11)]
    TARGET_PER_CELL = 1000

    maze_idx = 3
    maze = MAZES[maze_idx - 1]          # MAZES is 0-indexed; Maze 3 is index 2
    csv_file = f"rrt_results_maze{maze_idx}_power_n1000_coupled.csv"
    img_folder = f"rrt_images_maze{maze_idx}_power_n1000"

    # Count how many runs already exist per (step_size, random_rate) cell
    done_counts = {}
    if os.path.isfile(csv_file):
        prev = pd.read_csv(csv_file)
        # round to avoid float-key mismatches (0.30000000000000004 etc.)
        prev["step_size"] = prev["step_size"].round(3)
        prev["random_rate"] = prev["random_rate"].round(3)
        done_counts = (prev.groupby(["step_size", "random_rate"])
                           .size().to_dict())

    print("=" * 60)
    print(f"Maze {maze_idx} | Resuming power runs (n={TARGET_PER_CELL}, coupled)")
    print(f"  CSV: {csv_file}")
    print("=" * 60)

    for step in step_sizes:
        for rr in random_rates:
            already = done_counts.get((round(step, 3), round(rr, 3)), 0)
            remaining = TARGET_PER_CELL - already

            if remaining <= 0:
                print(f"  step {step}, rr {rr}: {already}/{TARGET_PER_CELL} — complete, skipping")
                continue

            print(f"  step {step}, rr {rr}: {already}/{TARGET_PER_CELL} done, running {remaining} more")
            run_multiple_experiments(
                num_runs=remaining,          # only the shortfall
                start_pos=(0, 0.5),
                goal_pos=(10, 9.5),
                map_size=10,
                max_iter=10000,
                step_size=step,
                random_rate=rr,
                goal_tolerance=step,         # coupled
                obstacle_list=maze,
                visualize=False,
                save_file=csv_file,
                image_folder=img_folder,
            )