import numpy as np
import matplotlib.pyplot as plt



# Refactored code to align axes such that:
# - X is along the x-axis
# - Y is along the spanwise axis
# - Z is the vertical axis
# - The plane is normal to the Y-axis (0,1,0)

# Define a new normal vector (pointing along +Y)
normal_y = np.array([0, 1, 0])  # Normal along Y-axis (spanwise normal plane)

# Define a new plane at Y = 2 (parallel to the XZ plane)
plane_y = 2

# Define new line segment points
P0_y = np.array([1, 0, 1])  # Start point of the segment (before the plane)
P1_y = np.array([4, 5, 3])  # End point of the segment (after the plane)

# Compute intersection with the new plane (Y = plane_y)
t_y = (plane_y - P0_y[1]) / (P1_y[1] - P0_y[1])

# Compute intersection point
intersection_y = P0_y + t_y * (P1_y - P0_y)

# Plot setup for the normal plane along Y
fig = plt.figure(figsize=(8, 6), dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Plot the plane (XZ plane at Y = plane_y)
X, Z = np.meshgrid(np.linspace(0, 5, 10), np.linspace(0, 5, 10))
Y = np.full_like(X, plane_y)
ax.plot_surface(X, Y, Z, color='cyan', alpha=0.3, edgecolor='gray')

# Plot the line segment
ax.plot([P0_y[0], P1_y[0]], [P0_y[1], P1_y[1]], [P0_y[2], P1_y[2]], 'r-', linewidth=2, label="Line Segment")

# Plot the normal vector
ax.quiver(intersection_y[0], intersection_y[1], intersection_y[2],
          normal_y[0], normal_y[1], normal_y[2],
          color='blue', length=1.5, normalize=True, label="Plane Normal")

# Mark points
ax.scatter(*P0_y, color='red', s=100, label="P0 (Start)")
ax.scatter(*P1_y, color='green', s=100, label="P1 (End)")
ax.scatter(*intersection_y, color='purple', s=100, label="Intersection")

# Labels and title
ax.set_xlabel("X-axis (Chordwise)")
ax.set_ylabel("Y-axis (Spanwise)")
ax.set_zlabel("Z-axis (Vertical)")
ax.set_title("Plane-Line Intersection in the Normal Spanwise Plane (Y)")

ax.legend()
plt.show()
