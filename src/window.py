import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon


class Window:
    """ Handles a window shown to the user, including plotting, and displaying

    Attributes:
        fig (matplotlib.pyplot.figure): Internal figure used for plotting
        color (matplotlib.color): Color used when plotting.

    """

    def __init__(self, limit, figsize=(6.4, 6.4), color='b'):
        """ Initialize the window.

        Args:
            figsize (Tuple): Tuple containing the desired size of the figure in inches.
            color (matplotlib.color): Default color to use when plotting.

        """
        self.limit = limit
        self.fig = plt.figure(figsize=figsize, dpi=100)
        self.color = color

    def show(self):
        """ Shows the window """
        plt.show()

    def set_axes_limits(self):
        """ Set the axes limits based on self.limit """
        plt.xlim(-self.limit, self.limit)
        plt.ylim(-self.limit, self.limit)

    def clear(self):
        """ Clears the internal figure and turns the axes off """
        plt.clf()
        plt.axis('off')
        self.set_axes_limits()

    def _plot_wireframe(self, vertices, edges=None, invisible=False):
        """ Plots a wireframe of 2D vertices and edges.

        Args:
            vertices (ndarray): 2 x V ndarray, where V is the number of vertices
            edges (ndarray): Tuple of two entries: (x, y), where x and y have shape 2 x E. Each column in x and y
                represents the x / y coordinates of the start and end of the edge.

                For example:

                    x = np.array([[1, 2, 3],
                                  [4, 5, 6]])
                    y = np.array([[7, 8, 9],
                                  [10, 11, 12]])
                    edges = (x, y)

                represents three edges, where the first edge goes from (1, 7) to (4, 8)

        Usage:
            projected_points = mesh.project_onto_window()
            edges = mesh.get_projected_edges()
            self._plot_wireframe(projected_points, edges)

        """
        color = (0, 0, 0, 0) if invisible else self.color

        plt.plot(vertices[0, :], vertices[1, :], '.', color=color)

        x, y = edges
        plt.plot(x, y, color=color)

    def plot_mesh(self, mesh, draw_faces=True):
        """ Plots a Mesh object onto the 2D window.

        The order of triangle rendering is determined by the z values of each of the faces. This is NOT ideal and runs
        into issues.

        Ideally, we could compute the outward facing normal vector for each face and order the rendering
        by the dot product of the normal vector with the z-axis, since then face that point away from the viewer are
        rendered first and then replaced by faces that point toward the viewer. However, given a 3D triangle, we cannot
        determine the outward facing normal vector. We could use find it by making sure it is aligned with the vector
        from the center to the centroid of each face, but this assumes the mesh object is convex, so this can also run
        into issues if this assumption fails.

        We could take a starting face, fix its normal, and then do bfs to set nearby normals as a similar direction.
        Once they are all set, we can then analyze to determine whether we need to flip all the normals or not.
        However, this assumes that we have many meshes and that the normals vectors do not change drastically between
        neighboring faces. This assumption doesn't hold for this application.

        Using the z-values is unideal, but works fairly consistently for different shapes I've tried.

        Args:
            mesh (Mesh): Mesh object representing the object to project and display.
            draw_faces (bool): Whether to draw faces instead of wireframe.

        """
        projected_vertices = mesh.project_vertices_onto_window()
        edges = mesh.get_projected_edges()
        self._plot_wireframe(projected_vertices, edges, invisible=draw_faces)

        if draw_faces:
            faces = mesh.get_projected_faces()
            normals = mesh.get_face_normals()
            face_z_values = mesh.get_face_z_values()
            colors = self._get_face_colors_from_normals(normals)
            self.draw_triangles(faces, colors, render_order_values=face_z_values)

    def get_figure(self):
        """ Gets the internal figure being used.

        Returns:
            matplotlib.pyplot.figure for the figure being used.

        """
        return self.fig

    def get_figure_resolution(self):
        """ Get the resolution of the figure in pixels.

        Uses solution from https://stackoverflow.com/questions/29702424/how-to-get-matplotlib-figure-size#:~:text

        Returns:
            List with two entries: [resolution in x, resolution in y]

        """
        resolution = self.fig.get_size_inches() * self.fig.dpi
        return resolution

    def _compute_projection_norm_with_z_axis(self, normals):
        """ Computes magnitudes of norm of projection of normal vector onto the z-axis.

         Args:
             normals (List[ndarray]): List of arrays that have shape (3, 1), each representing a unit-norm normal vector

         Returns:
             List of values that range from 0 to 1, where 0 is when the normal is perpendicular to the z-axis
             and 1 when the normal is parallel with the z axis.

         """
        normals = np.array(normals)[:, :, 0].T
        z_axis = np.array([[0], [0], [1]])
        norms_of_projection_onto_z = np.abs(np.matmul(normals.T, z_axis)[:, 0])
        return list(norms_of_projection_onto_z)

    def draw_triangles(self, triangles, colors, render_order_values):
        """ Draw a list of triangles in order determined by list of input values.

        Args:
            triangles (List[ndarray]): List of triangle vertices for each face. Each array should have shape (3,2).
            colors (List[matplotlib.color]): List of colors for each face.
            render_order_values (List[float]): List of values for each face, where a low / negative value means to render
                first, and a high / positive value means to render last

        """
        assert len(triangles) == len(colors) == len(render_order_values), 'All input lists should have the same length'

        triangles, colors, render_order_values = self._sort_faces_by_render_order_values(triangles, colors,
                                                                                         render_order_values)

        for triangle, color in zip(triangles, colors):
            self.draw_triangle(triangle, color)

    def draw_triangle(self, points, color):
        """ Draw a triangle on the window.

        Args:
            points (ndarray): Points for the triangle. Should be shape (3,2), where each row is a 2D point of
                the triangle
            color (matplotlib.color): Color for the triangle.

        """
        assert points.shape == (3, 2), 'The argument points needs to have shape (3,2)'

        triangle = Polygon(points, color=color)
        plt.gca().add_patch(triangle)

    def _sort_faces_by_render_order_values(self, triangles, colors, render_order_values):
        """ Reorder the list of faces so the faces in front are rendered last.

        Args:
            triangles (List[ndarray]): List of triangle vertices for each face. Each array should have shape (3,2).
            colors (List[matplotlib.color]): List of colors for each face.
            render_order_values (List[float]): List of values for each face, where a low / negative value means to render
                first, and a high / positive value means to render last

        Returns:
            Input lists sorted in order that they should be rendered.
        """
        sorted_lists = sorted(zip(triangles, colors, render_order_values), key=lambda x: x[2])
        triangles, colors, render_order_values = zip(*sorted_lists)
        return triangles, colors, render_order_values

    def _get_face_colors_from_normals(self, normals):
        """ Get colors for each face based on the normal vectors.

        Args:
            normals (List[ndarray]): list of normal vectors of shape (3,).

        Returns:
            List[matplotlib.color] list of colors.
        """
        colors = [None] * len(normals)
        projection_norms = self._compute_projection_norm_with_z_axis(normals)
        for i, projection_norm in enumerate(projection_norms):
            color = self._get_face_color_from_projection_norm(projection_norm)
            colors[i] = color
        return colors

    def _get_face_color_from_projection_norm(self, projection_norm, blue_min=95, blue_max=255):
        """ Get face color from a projection norm

        Linearly interpolates the color from blue_min to blue_max based on the similarity between the normal
        vector and the z axis (where the z-axis comes out of the page)

        Args:
            projection_norm (float): value from 0 to 1 for linear interpolation
            blue_min (int): Minimum blue value (from 0-255). This is the blue value when the face is perpendicular to
                the z-axis
            blue_max (int): Maximum blue value (from 0-255). This is the blue value when the face is parallel with the
                z-axis

        Returns:
            r,g,b,a for the color
        """

        blue_value = blue_min + projection_norm * (blue_max - blue_min)
        blue_value_normalized = blue_value / 255

        return 0.0, 0.0, blue_value_normalized, 1.0
