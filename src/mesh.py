import csv
import numpy as np


class Mesh:
    """ Contains information and functionality for a 3D mesh.

    Attributes:
        vertices (ndarray): 3 x V array, where V is the number of vertices.
        num_vertices (int): Number of vertices in the Mesh.
        faces (ndarray): F x 3 array, where F is the number of faces. Each row represents a face, containing the three
            indices for the three vertices that the face consists of.
        num_faces (int): Number of faces in the Mesh.
        edge_indices (ndarray): Array containing the set of unique edges in the mesh, where each edge is two indices,
            representing the index for the starting vertex and index for the ending vertex.

    """

    def __init__(self, vertices, faces):
        """ Initializes the Mesh by reading its information from a provided csv file.

        Args:
            vertices (ndarray): 3 x V array, where V is the number of vertices.
            faces (ndarray): F x 3 array, where F is the number of faces. Each row represents a face, containing the three
                indices for the three vertices that the face consists of.
        """
        self.vertices = vertices
        self.num_vertices = vertices.shape[1]
        self.faces = faces
        self.num_faces = faces.shape[0]
        self.edge_indices = self.compute_edge_indices()

    def compute_edge_indices(self):
        """ Finds the unique set of edges for the 3D mesh.

        Args:
            faces (ndarray): Faces of the Mesh, with shape (F x 3), where F = number of faces and
                each row contains three indices for the vertices that make up the face.

        Returns:
            List containing the set of unique edges for the mesh. Each edge consists of a Tuple that has the index for
                the starting vertex and index for the ending vertex for the edge.

        """
        assert self.faces.shape == (self.num_faces, 3), 'Faces must have dimensions F x 3'
        edge_indices = set()
        for face in self.faces:
            edge_indices.add((face[0], face[1]))
            edge_indices.add((face[0], face[2]))
            edge_indices.add((face[1], face[2]))
        return list(edge_indices)

    def rotate(self, R):
        """ Rotates the mesh according to provided rotation matrix.

        Args:
            R (ndarray): 3x3 rotation matrix that is orthogonal and determinant 1.

        """
        assert R.shape == (3, 3), 'The rotation matrix must have shape (3,3)'
        self.vertices = np.matmul(R, self.vertices)

    def rotate_about_x_and_y(self, degrees_about_x, degrees_about_y):
        """ Rotates the mesh about the x and y axes.

        The x-axis points to the right in the figure, and the y-axis points upwards. This uses a rotation
        matrix that is the matrix multiplication of a rotation matrix for rotation about the x-axis and a
        rotation matrix for rotation about the y-axis. The final rotation matrix was calculated symbolically by hand.

        Args:
            degrees_about_x (float): Degrees to rotate about the x-axis
            degrees_about_y (float): Degrees to rotate about the y-axis

        """
        radians_about_y, radians_about_x = np.deg2rad(degrees_about_y), np.deg2rad(degrees_about_x)
        s_y, c_y = np.sin(radians_about_y), np.cos(radians_about_y)
        s_x, c_x = np.sin(radians_about_x), np.cos(radians_about_x)

        R = np.array([[c_y, s_y * s_x, s_y * c_x],
                      [0, c_x, -s_x],
                      [-s_y, c_y * s_x, c_y * c_x]])

        self.rotate(R)

    def get_projected_edges(self):
        """ Get start and end positions for the Mesh's edges projected onto a 2D plane an infinite distance away.

        Returns:
            Tuple of two entries: (x, y), where x and y have shape 2 x E. Each column in x and y represents
                the x / y coordinates of the start and end of the edge.

                For example:

                    x = np.array([[1, 2, 3],
                                  [4, 5, 6]])
                    y = np.array([[7, 8, 9],
                                  [10, 11, 12]])
                    edges = (x, y)

                represents three edges, where the first edge goes from (1, 7) to (4, 8)

        """
        projected_vertices = self.project_vertices_onto_window()
        x, y = [], []
        for edge in self.edge_indices:
            x.append((projected_vertices[:, edge[0]][0], projected_vertices[:, edge[1]][0]))
            y.append((projected_vertices[:, edge[0]][1], projected_vertices[:, edge[1]][1]))
        return np.array(x).T, np.array(y).T

    def center_at_origin(self):
        """ Centers the mesh at the origin """
        center = self._get_center_repeated_matrix()
        self.vertices -= center

    def _get_center_repeated_matrix(self):
        """ Get a repeated matrix of the center coordinates.

        Returns:
            ndarray of shape (3 x V), where V = number of vertices. Each column in the matrix is the
            center of the mesh object.

        """
        center = self.get_center()
        center = np.repeat(center, self.num_vertices, axis=1)
        return center

    def get_center(self):
        """ Get the vector for the center of the mesh object.

        Returns:
            ndarray of shape (3, 1) representing the center of the mesh object.
        """

        center = np.expand_dims(np.mean(self.vertices, axis=1), axis=1)
        return center

    def get_furthest_vertex_distance(self):
        """ Get the furthest Euclidean distance of a vertex from the center of the mesh object.

        Returns:
            float for the furthest distance a vertex is from the center of the mesh object.
        """
        center = self._get_center_repeated_matrix()
        vertices = self.vertices - center
        norms = np.linalg.norm(vertices, axis=0)
        furthest_vector_distance = np.max(norms)
        return furthest_vector_distance

    def project_vertices_onto_window(self):
        """ Projects the vertices of the Mesh onto a 2D plane an infinite distance away.

        Returns:
            ndarray of shape (2 x V) for the 2D projected vertices, where V is the number of vertices in the Mesh.

        """
        projected_vertices = self.vertices[:2, :]
        return projected_vertices

    def get_projected_faces(self):
        """ Get faces projected onto the 2D window.

        Returns:
            List[ndarray] with each ndarray being of shape (3x2), where each numpy array contains three 2D points.
        """
        projected_vertices = self.project_vertices_onto_window()
        face_polygons = [None] * self.num_faces
        for i, face_vertex_indices in enumerate(self.faces):
            face_polygon = projected_vertices[:, face_vertex_indices].T
            face_polygons[i] = face_polygon
        return face_polygons

    def get_face_z_values(self):
        """ Get z values of the faces.

        Returns:
            List[float] list of floats for distances for each face

        """
        face_z_values = [0] * self.num_faces
        for i, face_vertex_indices in enumerate(self.faces):
            face = self.vertices[:, face_vertex_indices]
            face_z_values[i] = self._compute_z_centroid_of_triangle(face)
        return face_z_values

    def _compute_centroid_of_triangle(self, triangle):
        """ Compute the centroid of a 3D triangle

        Args:
            triangle (ndarray): Array of shape (3,3) representing the three points of a 3D triangle.
                Each column is a 3D point, and the rows are the x, y, and z coordinates of the points

        Returns:
            The triangle's centroid
        """
        assert triangle.shape == (3, 3), 'Argument triangle must have shape 3x3'
        centroid = np.expand_dims(np.average(triangle, axis=1), axis=1)
        return centroid

    def _compute_z_centroid_of_triangle(self, triangle):
        """ Compute the z centroid of a 3D triangle.
        
        Args:
            triangle (ndarray): Array of shape (3,3) representing the three points of a 3D triangle.
                Each column is a 3D point, and the rows are the x, y, and z coordinates of the points

        Returns:
            The z-coordinate of the triangle's centroid.
        """
        return self._compute_centroid_of_triangle(triangle)[2, 0]

    def get_face_normals(self):
        """ Get normal vectors for each face. Tries to get outward facing vectors, but this assumes the mesh is convex.

        Returns:
            List[ndarray] of arrays with shape (3,), where each represents the normal vector of the corresponding face.
        """
        normals = []

        for i, face_vertex_indices in enumerate(self.faces):
            face = self.vertices[:, face_vertex_indices].T
            face_plane_span_vector1 = face[1] - face[0]
            face_plane_span_vector2 = face[2] - face[0]

            normal = np.expand_dims(np.cross(face_plane_span_vector1, face_plane_span_vector2), axis=1)
            normal /= np.linalg.norm(normal)

            normals.append(normal)

        return normals


def read_mesh_from_file(filepath):
    """ Creates a mesh object from a provided CSV file.

    Args:
        filepath (str): Path to the csv file containing vertices and faces.

    Returns:
        Mesh object read from the file.

    """
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        first_row = reader.__next__()
        num_vertices = int(first_row[0])
        num_faces = int(first_row[1])

        vertices = []
        for i in range(num_vertices):
            vertex = reader.__next__()
            vertex = list(map(float, vertex))[1:]
            vertices.append(vertex)
        vertices = np.array(vertices).T

        faces = []
        for i in range(num_faces):
            face = reader.__next__()
            face = list(map(int, face))
            face = list(map(vertex_id_to_index, face))
            faces.append(face)
        faces = np.array(faces)

    return Mesh(vertices, faces)


def vertex_id_to_index(vertex_id):
    """ Converts from vertex_id to zero-based index """
    assert 1 <= vertex_id, 'Vertex id should range from 1 to V, where V is the number of vertices'
    index = vertex_id - 1
    return index
