from mesh import Mesh, read_mesh_from_file
from window import Window
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import argparse
import os


class MeshRendererApp:
    """ Application for rendering a Mesh object.

    Attributes:
        mesh (Mesh): Mesh that is being displayed.
        window (Window): Window to display the mesh.
        last_mouse_drag_location (Tuple): The x and y coordinates in pixels of the most recent mouse move.
        mouse_is_pressed (bool): True if the mouse is currently pressed.
        degrees_per_full_screen_mouse_move (float): Degrees to rotate the mesh by after the mouse has moved the full
            length of the figure.

    """

    def __init__(self, filepath, degrees_per_full_screen_mouse_move=200):
        """ Initializes the rendering application.

        Args:
            filepath (str): path to the mesh object csv file.
            degrees_per_full_screen_mouse_move (float): How many degrees to rotate the mesh by after the mouse has been dragged
                from one side of the figure to the other.

        """

        self.mesh = read_mesh_from_file(filepath)
        self.mesh.center_at_origin()
        window_limit = self.mesh.get_furthest_vertex_distance()

        self.window = Window(window_limit)

        self._connect()

        self.last_mouse_drag_location = None
        self.mouse_is_pressed = False

        self.degrees_per_full_screen_mouse_move = degrees_per_full_screen_mouse_move

    def update(self, i):
        """ Update the rendering by clearing the window and plotting the mesh again.

        Args:
            i (int): Current frame number of the animation.

        """
        self.window.clear()
        self.window.plot_mesh(self.mesh)

    def run(self):
        """ Runs an animation to render the Mesh and update the display, and displays the window to the user.

        See https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html for more information.

        """

        print("Press 'q' to quit the application")
        animation = FuncAnimation(plt.gcf(), self.update, interval=1, repeat=True)
        self.window.show()

    def _connect(self):
        """ Enable events for pressing, releasing, and moving the mouse.

        See https://matplotlib.org/stable/users/explain/event_handling.html for more information.

        """
        self.cidpress = self.window.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.window.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.window.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidkeypress = self.window.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def on_key_press(self, event):
        """ Closes the application when "q" is pressed by the user.

        Args:
            event (matplotlib.backend_bases.KeyEvent): Key press event.

        """
        if event.key == "q":
            quit(-1)

    def on_press(self, event):
        """ Signals that the mouse is pressed and saves the clicked location.

        Args:
            event (matplotlib.backend_bases.MouseEvent): Mouse press event.

        """
        self.mouse_is_pressed = True
        self.last_mouse_drag_location = (event.x, event.y)

    def on_release(self, event):
        """ Updates attributes to signal that the mouse has been released.

        Args:
            event (matplotlib.backend_bases.MouseEvent): Mouse release event.

        """
        self.mouse_is_pressed = False
        self.last_mouse_drag_location = None

    def on_motion(self, event):
        """ Handles mouse movement, including rotating the mesh.

        Args:
            event (matplotlib.backend_bases.MouseEvent): Mouse move event.

        """
        if not self.mouse_is_pressed:
            return

        current_mouse_x, current_mouse_y = event.x, event.y

        if current_mouse_x is None or current_mouse_y is None:
            return

        self.rotate_mesh_based_on_mouse_move(current_mouse_x, current_mouse_y)
        self.mesh.center_at_origin()
        self.last_mouse_drag_location = (current_mouse_x, current_mouse_y)

    def rotate_mesh_based_on_mouse_move(self, current_mouse_x, current_mouse_y, movement_factor=100):
        """ Rotates the mesh based on the mouse movement.

        Args:
            current_mouse_x (int): Current x-location of the mouse in pixels.
            current_mouse_y (int): Current y-location of the mouse in pixels.
            movement_factor (float): Scales how much rotation occurs for a mouse movement.

        """
        x_displacement = current_mouse_x - self.last_mouse_drag_location[0]
        y_displacement = current_mouse_y - self.last_mouse_drag_location[1]

        x_displacement_normalized, y_displacement_normalized = \
            self.normalize_by_figure_resolution(x_displacement, y_displacement)

        self.mesh.rotate_about_x_and_y(-y_displacement_normalized * self.degrees_per_full_screen_mouse_move,
                                       x_displacement_normalized * self.degrees_per_full_screen_mouse_move)

    def normalize_by_figure_resolution(self, x_pixels, y_pixels):
        """ Normalizes an x and y position in pixels by the resolution of the Window.

        Args:
            x_pixels (int): x-location in pixels of a point on the window.
            y_pixels (int): y-location in pixels of a point on the window.

        Returns:
            Normalized x and y values between 0 and 1 based on the resolution of the window.

        """
        fig_size = self.window.get_figure_resolution()
        normalized_x = x_pixels / fig_size[0]
        normalized_y = y_pixels / fig_size[1]
        return normalized_x, normalized_y


def main(args):
    """ Run the mesh renderer application.

    Args:
        args(List[str]): List of strings to parse.

    """
    mesh_filepath = args.mesh_filepath
    assert os.path.exists(mesh_filepath), f'Provided mesh filepath is invalid: {mesh_filepath}'

    renderer = MeshRendererApp(mesh_filepath)
    renderer.run()


if __name__ == "__main__":
    DEFAULT_MESH_OBJECT_FILEPATH = '../data/object.txt'

    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh-filepath', type=str, default=DEFAULT_MESH_OBJECT_FILEPATH,
                        help='Path to csv file containing information about the mesh object')
    args = parser.parse_args()
    main(args)
