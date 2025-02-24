# Setup Environment for Python Demos

* Setup [Python 3.x](https://www.python.org/downloads/windows/)
* Setup the pipenv environment

    pip install --user pipenv
    pipenv shell

* Setup the required packages
  Install custom PyOpenGL package due to missing GLUT on Windows

    pipenv install numpy
    pipenv install scipy
    pipenv install PyOpenGL-3.1.3b2-cp37-cp37m-win_amd64
    pipenv install imgui[glfw]