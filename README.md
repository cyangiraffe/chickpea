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
# This script generates a directional coupler.
#
# Revision History:
#   Julian Sanders  25 Jun 2019 Initial Revision
#   Julian Sanders  28 Jun 2019 Debugging
#   Julian Sanders  05 Jul 2019 Updated for package name change to
#                               'chickpea' and added generation of
#                               3D FDTD script.
#   Julian Sanders  13 Jul 2019 Updated for changes to the coupler's 
#                               arm parametrization.

import pya    # Module containing KLayout API
from chickpea import couplers
from chickpea import paths

# For debugging chickpea without exiting KLayout
from importlib import reload
reload(couplers)
reload(paths)

layout = pya.Layout()               # create new layout
top = layout.create_cell("TOP")     # create top-level cell
rib = layout.layer(1, 0)            # create rib waveguide layer

length_3dB = 16.23  # coupling length

# Specify the length and height of each s-bend arm of the 
# coupler individually. The largest possible bend radius
# for the given length and height specifications will be used.
arm_lengths = {
  'lower left': 20,
  'upper right': 60,
  'lower right': 20,
  'upper left': 10
}

arm_heights = {
  'lower left': 5,
  'upper right': 52,
  'lower right': 2,
  'upper left': 30
}

# Note: to make all arms the same, just make 'arm_lengths'
# and 'arm_heights' scalars.

# Generate the directional coupler
couplers.dir_coupler(layout, 'divide', rib, length_3dB,
  arm_lengths, arm_heights, seg_length=0.2)

# Print the device's length, height, and port coordinates
print(couplers.dir_coupler_length(length_3dB, arm_x))
print(couplers.dir_coupler_height(arm_heights=arm_y, sep=0.2))
print(couplers.dir_coupler_ports(length_3dB, arm_lengths=arm_x, 
  arm_heights=arm_y, sep=0.2))


layout.write("C:/Users/julli/OneDrive - " 
   + "California Institute of Technology/"
   + "CHIC/gds_models/dir_couplers/dir_coupler_3dB.gds")
```
