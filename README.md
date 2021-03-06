# CHICkpea

## Description
The _Caltech Holisitic Integrated Circuits KLayout Photonic Element 
Autogenerator_ (chickpea) is a python package that can be imported into a
python-based KLayout macro from which functions can be called that will
generate various photonic devices. The value of the package lies in that 
functional parameters of the device are passed to the generating function,
and the generating function produces the device layout.

## Dependencies
This package needs a version of [KLayout](https://www.klayout.de/) that has numpy built in. Versions
0.25 and 0.26 have both been verified to work with chickpea.

## Installation
Clone the chickpea directory into the directory 

    C:\Users\[user name]\AppData\Roaming\KLayout\python

The name 'chickpea' can then be used to import the python package into
any python-based KLayout macro.


## Primary Features
* N-to-N parallel port auto-routing
* Delay spirals
* Directional Couplers
* Parabolic and linear tapers
* S-bends


## Use and example script
Here is an example script that generates a directional coupler. 
Note the import statements at the top of the file
using this folder name. There, we import a sub-module (corresponding to .py
files inside the folder) called 'couplers', which includes the function we 
want to generate a directional coupler with.

```python
# This script generates a directional coupler.

import pya    # Module containing KLayout API
from chickpea import couplers   # contains directional coupler generation
from chickpea import paths      # path/waveguide generation

layout = pya.Layout()               # create new layout
top = layout.create_cell("TOP")     # create top-level cell
dc  = layout.create_cell("dc")      # create cell for a dir'nal coupler
rib = layout.layer(1, 0)            # create rib waveguide layer


couplers.dir_coupler(layout, rib, 
  dc,   # place the entire coupler in the cell 'dc'
  10,   # set the coupling length to 10 um
  20,   # make all s-bend arm lengths 20 um
  10,   # make all s-bend arm heights 10 um
  sbend_output='pcell'  # Have the s-bends output as PCells
)

# Insert the cell 'dc', which contains the directional coupler,
# into the top cell of our layout.
top.insert(pya.DCellInstArray(
  dc.cell_index(),
  pya.DTrans(pya.DVector(-20, 70))  # Shift away from first coupler
))

# Write the layout to a GDS file at this path
layout.write("C:/Users/julli/Desktop/dir_coupler.gds")
```

## Learning the Package
* There's a subdirectory within chickpea called "example_scripts", which
  contains example KLayout macro scripts using the functions provided by
  chickpea, along with the GDS files that each of those macros generate.

* At the top of the .py files in the package, there is a list of "top level
  functions" that briefly list and describe the functions in that file that
  might be used in a macro script (as opposed to the helper functions in 
  that file, which are only used within the chickpea package). From those
  names, you can either ctrl+F the files or use python's help() function to
  read the function docstrings for detailed reference documentation on each
  function. This may contain details the example scripts don't.

* There is also a subdirectory called "user_manual". Right now, it just
  contains some examples of the outputs of various parameter sets supplied
  to the delay spiral function, and in the future may contain information
  on the geometry involved in the package's various functions.


## Troubleshooting

* DLL load failed: The specified module could not be found.
  If KLayout gives this message when attempting to run a macro that uses
  chickpea, followed by messages indicating it can't find numpy, close
  KLayout and open it via the start menu/taskbar/equivalent, NOT by double
  clicking on a GDS file. It KLayout is opened the latter way, it seems it
  won't load numpy properly. Bug present in KLayout v. 0.26

## Releases

### Version 1.0
This is the first public release of chickpea. The major features follow:
* N-to-N parallel port auto-routing
* Delay spirals
* Directional Couplers
* Parabolic and linear tapers
* S-bends
