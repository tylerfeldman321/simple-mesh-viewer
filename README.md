# Simple Mesh Rendering Application

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

After the application is run, you can press the key `'q'` to quit the application.

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


