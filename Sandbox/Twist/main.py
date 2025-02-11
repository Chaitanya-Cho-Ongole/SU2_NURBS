import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def compute_end_face_centroids(ffd_vertices):
    """
    Computes the centroids of the two end faces of an FFD box.
    The end faces are determined based on the minimum and maximum Y-values.

    Parameters:
    - ffd_vertices (numpy array): Array of shape (N, 3) containing the FFD box vertices.

    Returns:
    - centroid_min_y (numpy array): Centroid of the face with minimum Y.
    - centroid_max_y (numpy array): Centroid of the face with maximum Y.
    """
    min_y = np.min(ffd_vertices[:, 1])
    max_y = np.max(ffd_vertices[:, 1])

    # Extract vertices belonging to the two end faces
    min_y_face = np.array([v for v in ffd_vertices if np.isclose(v[1], min_y)])
    max_y_face = np.array([v for v in ffd_vertices if np.isclose(v[1], max_y)])

    # Compute centroids if the faces contain enough points
    centroid_min_y = np.mean(min_y_face, axis=0) if len(min_y_face) > 0 else None
    centroid_max_y = np.mean(max_y_face, axis=0) if len(max_y_face) > 0 else None

    return centroid_min_y, centroid_max_y

# Compute centroids for the given FFD vertices
#centroid_min_y, centroid_max_y = compute_end_face_centroids(ffd_vertices)

# Print the results
#print(f"Centroid of min Y face: {centroid_min_y}")
#print(f"Centroid of max Y face: {centroid_max_y}")



# Define the FFD box vertices
ffd_vertices = np.array([
    [24.5, 2.8818, 2.5],
    [37.5, 2.8818, 2.5],
    [48.1, 29.7, 5],
    [44.5, 29.7, 5],
    [24.5, 2.8818, 5.9150],
    [37.5, 2.8818, 5.9150],
    [48.1, 29.7, 7.5],
    [44.5, 29.7, 7.5]
])

# Define the faces of the FFD box
faces = [
    [ffd_vertices[i] for i in [0, 1, 5, 4]],  # Front face
    [ffd_vertices[i] for i in [1, 2, 6, 5]],  # Right face
    [ffd_vertices[i] for i in [2, 3, 7, 6]],  # Back face
    [ffd_vertices[i] for i in [3, 0, 4, 7]],  # Left face
    [ffd_vertices[i] for i in [4, 5, 6, 7]],  # Top face
    [ffd_vertices[i] for i in [0, 1, 2, 3]]   # Bottom face
]

# Define the Y-normal plane (parallel to X-Z at mean Y value)
y_plane_value = np.mean(ffd_vertices[:, 1])
plane_vertices = np.array([
    [min(ffd_vertices[:, 0]), y_plane_value, min(ffd_vertices[:, 2])],
    [max(ffd_vertices[:, 0]), y_plane_value, min(ffd_vertices[:, 2])],
    [max(ffd_vertices[:, 0]), y_plane_value, max(ffd_vertices[:, 2])],
    [min(ffd_vertices[:, 0]), y_plane_value, max(ffd_vertices[:, 2])]
])
plane_faces = [[plane_vertices[i] for i in [0, 1, 2, 3]]]

# Define an arbitrary plane through (24.5, 2.8818, 2.5), parallel to X-Z
arbitrary_plane_y = 2.8818
arbitrary_plane_vertices = np.array([
    [min(ffd_vertices[:, 0]), arbitrary_plane_y, min(ffd_vertices[:, 2])],
    [max(ffd_vertices[:, 0]), arbitrary_plane_y, min(ffd_vertices[:, 2])],
    [max(ffd_vertices[:, 0]), arbitrary_plane_y, max(ffd_vertices[:, 2])],
    [min(ffd_vertices[:, 0]), arbitrary_plane_y, max(ffd_vertices[:, 2])]
])
arbitrary_plane_faces = [[arbitrary_plane_vertices[i] for i in [0, 1, 2, 3]]]

new_point_1, new_point_2 = compute_end_face_centroids(ffd_vertices)

# Compute the intersection point (if any) with the arbitrary plane
t_intersection = (arbitrary_plane_y - new_point_2[1]) / (new_point_1[1] - new_point_2[1]) if (new_point_1[1] - new_point_2[1]) != 0 else None

if t_intersection is not None and 0 <= t_intersection <= 1:
    intersection_x = new_point_2[0] + t_intersection * (new_point_1[0] - new_point_2[0])
    intersection_z = new_point_2[2] + t_intersection * (new_point_1[2] - new_point_2[2])
    intersection_point = np.array([intersection_x, arbitrary_plane_y, intersection_z])
    print(f"Intersection Point: {intersection_point}")
else:
    intersection_point = None  # No intersection if t_intersection is None or outside [0,1]
    print("No intersection point since the segment is at y=0, below the arbitrary plane at y=2.8818.")

# Plot the FFD box, planes, and the corrected line segment
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Add the FFD box faces
ax.add_collection3d(Poly3DCollection(faces, facecolors='cyan', linewidths=1, edgecolors='k', alpha=0.5))

# Add the Y-normal plane
ax.add_collection3d(Poly3DCollection(plane_faces, facecolors='magenta', linewidths=1, edgecolors='k', alpha=0.3))

# Add the arbitrary plane
ax.add_collection3d(Poly3DCollection(arbitrary_plane_faces, facecolors='yellow', linewidths=1, edgecolors='k', alpha=0.3))

# Plot the corrected line segment (strictly along X at Y=0, Z=0)
ax.plot([new_point_1[0], new_point_2[0]],  # X-coordinates
        [new_point_1[1], new_point_2[1]],  # Y-coordinates (0 in this case)
        [new_point_1[2], new_point_2[2]],  # Z-coordinates (0 in this case)
        'r-', lw=2, label="Corrected Line Segment")

# Correctly plot the segment endpoints at y=0
ax.scatter([new_point_1[0], new_point_2[0]], 
           [new_point_1[1], new_point_2[1]], 
           [new_point_1[2], new_point_2[2]], 
           color='red', s=100, label="Segment Endpoints")

# Plot the intersection point if it exists
if intersection_point is not None:
    ax.scatter(intersection_point[0], intersection_point[1], intersection_point[2], 
               color='blue', s=150, edgecolors='k', label="Intersection Point")

# Set limits and labels, ensuring Y starts from 0
ax.set_xlim(min(ffd_vertices[:, 0]), max(ffd_vertices[:, 0]))
ax.set_ylim(0, max(ffd_vertices[:, 1]) + 5)  # Y-axis starts from 0
ax.set_zlim(min(ffd_vertices[:, 2]), max(ffd_vertices[:, 2]))
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_zlabel("Z-axis")
ax.set_title("FFD Box with Corrected Horizontal Line Segment at Y=0")

# Add legend
ax.legend()

# Show plot
plt.show()
