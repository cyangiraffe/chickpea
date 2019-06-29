# PIC Component Library

## Installation

Clone the directory into the directory 

	C:\Users\usr\KLayout\python

The name of the directory can then be used to import the python package into
any python-based KLayout.

## Use and example script

Here is an example script that generates a directional coupler for testing
in lumerical FDTD. The name of the directory containing this package is
'pic_component_library'. Note the import statements at the top of the file
using this folder name. There, we import a sub-module (corresponding to .py
files inside the folder) called 'couplers', which includes the function we 
want to generate a directional coupler with.

'''python
	# This script generates a directional coupler.
	#
	# Revision History:
	#   Julian Sanders  25 Jun 2019 Initial Revision
	#   Julian Sanders  28 Jun 2019 Debugging

	import pya    # Module containing KLayout API
	from pic_component_library import couplers

	# For debugging pic_component_library without exiting KLayout
	from importlib import reload
	reload(paths)
	reload(couplers)

	# Initialize a layout, cell, and layer in KLayout
	layout = pya.Layout()               # create new layout
	top = layout.create_cell("TOP")     # create top-level cell
	rib = layout.layer(1, 0)            # create rib waveguide layer

	# Generate the directional coupler
	length_3dB = 18.75 / 2  # coupling length
	couplers.dir_coupler(layout, 'divide', rib, length_3dB,
	  bend_radius=8, seg_length=0.2)

	# Write the resulting layout to a GDS file.
	layout.write("C:/Users/julli/OneDrive - " 
	   + "California Institute of Technology/"
	   + "Research/gds_models/dir_couplers/dir_coupler_3dB.gds")
'''
