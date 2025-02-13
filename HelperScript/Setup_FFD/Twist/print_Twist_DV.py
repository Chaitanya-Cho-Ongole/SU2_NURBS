import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

def plot_xy_zy_planes_with_spline(csv_file, num_points):
    """
    Reads a CSV file and plots the points in two subplots with fitted spline curves:
    1. X-Y plane (X as vertical, Y as horizontal)
    2. Z-Y plane (Z as vertical, Y as horizontal)
    
    Parameters:
    - csv_file (str): Path to the CSV file containing X, Y, Z coordinates.
    - num_points (int): Number of uniformly spaced points to sample from the fitted curve.
    
    Returns:
    - sampled_points (list of tuples): List of (X, Y, Z) coordinates of the sampled points.
    """
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Extract X, Y, Z columns
    x = np.array(df["X"])
    y = np.array(df["Y"])
    z = np.array(df["Z"])

    # Sort data by Y for proper spline fitting
    sorted_indices = np.argsort(y)
    y_sorted = y[sorted_indices]
    x_sorted = x[sorted_indices]
    z_sorted = z[sorted_indices]

    # Fit smooth splines using cubic interpolation
    x_spline = make_interp_spline(y_sorted, x_sorted, k=3)
    z_spline = make_interp_spline(y_sorted, z_sorted, k=3)

    # Generate fine Y values for smooth curve plotting
    y_fine = np.linspace(y_sorted.min(), y_sorted.max(), 300)
    x_fine = x_spline(y_fine)
    z_fine = z_spline(y_fine)

    # Select num_points uniformly spaced points along the fitted curve
    y_sampled = np.linspace(y_sorted.min(), y_sorted.max(), num_points)
    x_sampled = x_spline(y_sampled)
    z_sampled = z_spline(y_sampled)

    sampled_points = list(zip(x_sampled, y_sampled, z_sampled))

    # Create subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=300)

    # Plot X-Y plane
    axes[0].scatter(y, x, color='b', label='Points', alpha=0.6)
    axes[0].plot(y_fine, x_fine, 'r-', label='Fitted Curve', linewidth=2)
    axes[0].scatter(y_sampled, x_sampled, color='g', marker='o', label='Sampled Points', zorder=3)
    axes[0].set_xlabel("Y (horizontal axis)")
    axes[0].set_ylabel("X (vertical axis)")
    axes[0].invert_yaxis()  # Flip X-axis (which is the vertical axis in this plot)
    axes[0].axhline(0, color='black', linewidth=0.5)
    axes[0].axvline(0, color='black', linewidth=0.5)
    axes[0].legend()
    axes[0].set_title("X-Y Plane with Spline")

    # Plot Z-Y plane
    axes[1].scatter(y, z, color='b', label='Points', alpha=0.6)
    axes[1].plot(y_fine, z_fine, 'r-', label='Fitted Curve', linewidth=2)
    axes[1].scatter(y_sampled, z_sampled, color='g', marker='o', label='Sampled Points', zorder=3)
    axes[1].set_xlabel("Y (horizontal axis)")
    axes[1].set_ylabel("Z (vertical axis)")
    axes[1].axhline(0, color='black', linewidth=0.5)
    axes[1].axvline(0, color='black', linewidth=0.5)
    axes[1].legend()
    axes[1].set_title("Z-Y Plane with Spline")

    # Adjust layout and show plot
    plt.tight_layout()
    #plt.show()
    
    return sampled_points

def print_sampled_points_explicit(sampled_points):
    """
    Prints the sampled points in a specific format, explicitly handling the last sampled point.
    
    Parameters:
    - sampled_points (list of tuples): List of (X, Y, Z) coordinates of the sampled points.
    """
    if len(sampled_points) < 2:
        print("Not enough points to format output.")
        return
    
    output_series = []
    for i in range(len(sampled_points)):
        if i < len(sampled_points) - 1:
            next_point = sampled_points[i + 1]  # Normal case: use the next point
        else:
            next_point = sampled_points[i]  # Last point: use itself
        
        output_series.append(
            f"( 15, 1.0 | wing | WING, {i}, {sampled_points[0][0]}, {sampled_points[0][1]}, {sampled_points[0][2]}, "
            f"{next_point[0]}, {next_point[1]}, {next_point[2]} );"
        )
    
    print("\n")
    print(" ".join(output_series))
    print("\n")

# Run the explicit last-point handling function on the sampled points



# Example usage:
sampled_points = plot_xy_zy_planes_with_spline("QuarterChordCoords.csv", num_points=5)

print_sampled_points_explicit(sampled_points)

