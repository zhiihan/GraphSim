# GraphSim

This is a modified repository of Simon Anders' library to simulate an important class of quantum circuits which supports pybind11.

## Installation

To install, run
```
uv build
```

then navigate to the `dist/` folder and pip install the wheel.
```
uv pip install graphsim-*.*.*-cp312-cp312-linux_x86_64.whl
```

This code is not actively supported or maintained, but pull requests for minor bug fixes will be accepted.

> This is GraphSim, a library do simulate stabilizer quantum circuits.
>
> - Author: Simon Anders, sanders@fs.tum.de, University of Innsbruck
> - Version: v.10 (initial release)
> - Date: 1 Feb 2005 (last change), 18 Apr 2005 (release prep)
> - (c) 2005, released under GPL
>
> For information about this package, please read
> - the paper describing the algorithm:
>      S. Anders, H. J. Briegel:
>      Fast Simulation of Stabilizer Circuits using a Graph State Formalism
>      quant-ph/0504117
> - the documentation of the C++ library in doc/html/index.html
> - the documentation of the Python bindings in doc/graphsim_py.html
> - the file COPYING for the text of the GPL
>
> If you use this paper for scientific work, please cite the paper 
> referenced above in your publication.
     
In case of problems, please submit an issue: https://github.com/marcusps/GraphSim/issues

This code is not actively supported or maintained, but pull requests for minor bug fixes will be accepted.
