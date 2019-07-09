# CHICkpea

## Description
The _Caltech Holisitic Integrated Circuits KLayout Photonic Element 
Autogenerator_ (chickpea) is a python package that can be imported into a
python-based KLayout macro from which functions can be called that will
generate various photonic devices. 


## Installation

Clone the chickpea directory into the directory 

    C:\Users\[user name]\AppData\Roaming\KLayout\python

The name 'chickpea' can then be used to import the python package into
any python-based KLayout macro.


## Use and example script

Here is an example script that generates a directional coupler for testing
in lumerical FDTD. Note the import statements at the top of the file
using this folder name. There, we import a sub-module (corresponding to .py
files inside the folder) called 'couplers', which includes the function we 
want to generate a directional coupler with.

```python
import pya    # Module containing KLayout API
from chickpea import couplers

# Initialize a layout, cell, and layer in KLayout
layout = pya.Layout()               # create new layout
top = layout.create_cell("TOP")     # create top-level cell
rib = layout.layer(1, 0)            # create rib waveguide layer

# Generate the directional coupler
couplers.dir_coupler(
    layout,         # layout object coupler will be inserted in
    'divide',       # instructs function to divide coupler into 6 cells
    rib,            # layer to insert coupler on
    16,             # length of straight coupling waveguides, microns
    bend_radius=8,  # bend radius of s-bends
    seg_length=0.2  # length of straight segments that approximate round corners
 )

# Write the resulting layout to a GDS file.
layout.write("C:/Users/julli/OneDrive - " 
   + "California Institute of Technology/"
   + "Research/gds_models/dir_couplers/dir_coupler_3dB.gds")
```
