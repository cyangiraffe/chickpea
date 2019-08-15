import pya    # Module containing KLayout API
import numpy as np
from chickpea import paths
from chickpea import my_constants

# For debugging chickpea without exiting KLayout
from importlib import reload
reload(paths)

layout = pya.Layout()               # create new layout
top = layout.create_cell("TOP")     # create top-level cell
sp  = layout.create_cell("spiral")  # create cell for a delay spiral
rib = layout.layer(1, 0)            # create strip waveguide layer

horizontal = np.concatenate((
  np.array([0, 4, 4, 4, 8]),
  np.full(6, 8)))   # Pad to total length 9 with 8's 

vertical = np.concatenate((
  np.array([16, 20, 20, 20, 24]),
  np.full(6, 24)))  # Pad to total length 9 with 24's

# Generate the spiral and instantiate its cell
paths.delay_spiral_geo(layout, rib, sp, 
  turns=4, 
  spacing=2.5, 
  vertical=vertical,
  horizontal=horizontal,
  horizontal_mode='symmetric',
  vertical_mode='symmetric',
  quad_shift=0,
  start_turn=1, 
  start_angle=0, 
  end_angle=0,
  radial_shift=4.80, 
  n_pts=5000)
  
top.insert(pya.DCellInstArray(
  sp.cell_index(),
  pya.DTrans(pya.DVector(0, 30))
))


layout.write(my_constants.gds_models_path + 'test_spiral.gds')
