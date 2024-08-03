import numpy as np

# A sandbox script to define an FFD box and rotate it about an arbitrary center of rotation and around a unit vector
# using Rodrigues rotation formula

# Basic steps involved:  1) Translate the vertices so that center of rotation becomes the origin
#                        2) Perform the rotation around a unit vector (For example Y axis ) 
#                        3) Translate the vertices back to their original position relative to the specified center


def ffd_box(vertices):

    # Define the faces of the parallelepiped (using vertex indices)
    faces = [
        [0, 1, 2, 3],  # Lower surface
        [4, 5, 6, 7],  # Upper surface
        [0, 1, 5, 4],  # Side 1
        [1, 2, 6, 5],  # Side 2
        [2, 3, 7, 6],  # Side 3
        [3, 0, 4, 7]   # Side 4
    ]
    return faces
#end

def write_ffd_box(faces, vertices, filename):
    # Write the data to a .dat file in Tecplot ASCII format
    with open(filename, 'w') as f:
        # Header
        f.write("TITLE = \"Parallelepiped Geometry\"\n")
        f.write("VARIABLES = \"X\", \"Y\", \"Z\"\n")
        f.write(f"ZONE N={len(vertices)}, E={len(faces)}, DATAPACKING=POINT, ZONETYPE=FEQUADRILATERAL\n")
    
        # Write vertices
        for vertex in vertices:
            f.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")
    
        # Write faces (connectivity, using 1-based indexing for Tecplot)
        for face in faces:
            f.write(f"{face[0]+1} {face[1]+1} {face[2]+1} {face[3]+1}\n")

    print(f"Parallelepiped data has been written to {filename}.")
#end

def rotate_vertices(vertices, axis, theta_degrees, center):
    """Rotate vertices around an arbitrary axis vector by an angle theta (in radians)."""
    # Ensure the axis is a unit vector
    axis = axis / np.linalg.norm(axis)

    print("Rotation axis: ", axis)
    
    # Calculate rotation matrix using Rodrigues' rotation formula
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])

    # Translate vertices so that center of rotation becomes the origin.
    translated_vertices = vertices - center

    theta =np.radians(theta_degrees)
    
    R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)
    
    # Rotate all vertices
    rotated_translated_vertices = np.dot(translated_vertices, R.T)

    # Translate vertices back to the original position
    rotated_vertices = rotated_translated_vertices + center
    return rotated_vertices


# Define the vertices of the parallelepiped in counter-clockwise order starting from the lower surface

vertices = np.array([
    [31.804632, 2.4010531, 1.7035031],  # Lower root LE
    [36.487515,2.4010531,1.7035031],  # Lower root TE
    [36.487515,8.9127998,1.7035031],  # Lower tip TE
    [31.804632,8.9127998,1.7035031],  # Lower tip LE
    [31.804632,2.4010531,6.7657257],  # Upper root LE
    [36.487515,2.4010531,6.7657257],  # Upper root TE
    [36.487515,8.9127998,6.7657257],  # Upper tip TE
    [31.806432,8.9127998,6.7657257]   # Upper tip LE
], dtype=np.float32)

# Generate the FFD box
faces = ffd_box(vertices)

# Write the original FFD box
write_ffd_box(faces, vertices, 'ffd_box_0.dat')


# Rotate the vertices by an angle theta around the Y-axis

theta = 10
rotation_vector = np.array([0.241299747, 0.767418197, 0.594007])  # Rotate around the Y-axis

center_of_rotation = np.array([35.210,2.886, 2.082])  # Center of rotation



# Rotate the vertices
rotated_vertices = rotate_vertices(vertices, rotation_vector, theta, center_of_rotation)

# Write the rotated FFD box
write_ffd_box(faces, rotated_vertices, 'ffd_box_rotated.dat')
