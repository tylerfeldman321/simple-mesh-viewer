# Simple Mesh Rendering Application
This is a simple mesh rendering application to display full meshes or wireframes.

## Usage
### Installing Dependencies
A requirements.txt file is included. These dependencies can be installed using: `pip install -r requirements.txt` after
creating a virtual environment if desired.

### Running the Application
In both part1 and part2, the `mesh_renderer.py` file is used to run the application. To run this, change into the 
directory for either part1 or part2, and then run `python mesh_renderer.py`. This will run the 
application with the default file: `data/object.txt`. To specify a different object file,
run `python mesh_renderer.py --mesh-filepath={path/to/file.txt}`, replacing what is in the brackets with the desired
csv file to load.

- `python mesh_renderer.py`: Runs the application with `data/object.txt`
- `python mesh_renderer.py --mesh-filepath=path/to/file.txt` runs application with provided file path

### User Controls
Once the application is running, you can:
- Press the key `'q'` to quit the application.
- Drag and move the mouse to rotate the shape about the upwards and rightwards axes. Horizontal movement rotates the 
  mesh about the y (upward) axis, and vertical movement rotates the mesh about the x (rightwards) axis

## Structure
### Directories:
- `part1/`: Contains code for part1 of the assessment
- `part2/`: Contains code for part2 of the assessment
- `data/`: Contains CSV files for mesh objects. The CSV files are in the format specified in the assessment description

### Python files 
These python files are in both `part1/` and `part2/` and their overall logic is the same for both parts. The files 
in `part2/` do have added functionality
- `mesh_renderer.py`: Contains class to handle high level logic for the rendering application.
- `mesh.py`: Contains class to handle loading, transforming, and projecting a 3D mesh.
- `window.py`: Contains class to handle the user interface, including plotting.

## Mesh File Format
Mesh objects can be read in from CSV files, such as the example ones provided in the `data/` directory. 
The format of these files is as follows:

- The first line contains two integers. The first integer is the number of vertices that define the 3D 
object, and the second number is the number of faces that define the 3D object.
- Starting at the second line each line will define one vertex of the 3D object and will consist of an 
integer followed by three real numbers. The integer is the ID of the vertex and the three real 
numbers define the (x,y,z) coordinates of the vertex. The number of lines in this section will be 
equal to the first integer in the file.
- Following the vertex section will be a section defining the faces of the 3D object. The number of 
lines in this section will be equal to the second integer on the first line of the file. Each line in
this section will consist of three integers that define a triangle that is a face of the object. The 
three integers each refer to the ID of a vertex from the second section of the file.
