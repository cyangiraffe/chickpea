# This file contains functions for photonic waveguide auto-routing. 
# The top-level functions are as follows:
#	parallel_route_dense:	
#
#
# Revision History:
# 19 Aug 2019   Julian Sanders  Inital Revision



import pya
import math as ma
import numpy as np
from chickpea.constants import *
from chickpea.transforms import null_trans
from chickpea import paths

#
# Local constants
#

spacing = 2   # default spacing between routed waveguides to avoid coupling


#
# Functions
#

def parallel_route(layout, layer, inputs, outputs, port_dir, spacing=None,
	length=None, min_bend_radius=min_bend_radius, wg_width=wg_width,
	seg_length=seg_length, trans=null_trans, path_output='pcell'):
	'''
	Routes waveguides from the ith 'input' coordinate to the ith 'output'
	coordinate while trying to minimize the distance between the ports in 
	the direction of the ports. To this end, only 90 degree bend are used to 
	get the most compact length in the port direction while allowing a large
	extent in the direction perpendicular to the ports.

	Args:
        layout:         Layout object for instantiation
                        <pya.Layout object>

        layer:          The index of the layer to insert the paths into (this
                        is the value returned from the layout.layer() method).
                        <int>

		inputs:			An array of shape (2, n) specifying the cartesian
						coordinates of the input ports. This function will
						place inputs in the negative direction along the 
						port direction axis 'port_dir' relative to the
						outputs. For example, if port_dir == 'x', then the
						coordinates of the 'inputs' should be further in the
						negative x direction than the outputs. Must be the
						same shape as 'outputs'
						<np.ndarray>

		outputs:		An array of shape (2, n) specifying the cartesian
						coordinates of the input ports. This function will
						place inputs in the negative direction along the 
						port direction axis 'port_dir' relative to the
						outputs. For example, if port_dir == 'x', then the
						coordinates of the 'inputs' should be further in the
						negative x direction than the outputs. Must be the
						same shape as 'inputs'
						<np.ndarray>

		port_dir:		Specified the port direction, i.e., the direction the
						waveguide goes at the input/output ports. Can be
						either of the strings 'x' or 'y'.
						<str>

		spacing:	    Spacing between waveguide edges while they're going in
						the direction perpenicular to the ports. If no two 
						ports are spaced apart by less than this value, then
						'spacing' is the minimum waveguide spacing in the 
						entire interconnection.
						<float or int>
						(default: routing.spacing == 2)

		min_bend_radius:This bend radius will be used for the smallest bends
						generated in the routing process. Note that choosing
						a larger bend radius will result in a longer
						interconnect.
						<float or int>
						(default: constants.min_bend_radius == 5)

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)

        path_output:    If 'pcell' is passed, paths generated as PCells. 
                        If 'path' is passed, paths generated as DPaths.
                        <str>
                        (default: 'pcell')

    Return:
    	routes:			A list of paths that, together, make up the n to n
    					interconnection. Whether they are round path pcells or
    					DPaths with circular bends depends on the value passed
    					to 'path_output'.
    					<list of pya.DCellInstArray or list of pya.DPath>
	'''
	num_ports = len(inputs)

	# Make sure there are the same number of inputs and outputs.
	if num_ports != len(outputs):
		raise ValueError(
			"The arguments 'inputs' and 'outputs' must have the same shape.")

	if (spacing is None) and (length is None):
		spacing = 2

	if spacing is None:
		spacing = parallel_route_dense_spacing(num_ports, length, 
			min_bend_radius=min_bend_radius, wg_width=wg_width)

	elif length is None:
		length = parallel_route_dense_length(num_ports, spacing=spacing, 
			min_bend_radius=min_bend_radius, wg_width=wg_width)

	zeros = np.zeros(num_ports)
	lengths = np.full(num_ports, length)

	if port_dir == 'x':
		inputs_2d  = np.stack((zeros,   inputs))
		outputs_2d = np.stack((lengths, outputs))
	elif port_dir == 'y':
		inputs_2d  = np.stack((inputs,  zeros))
		outputs_2d = np.stack((outputs, lengths))
	else:
		raise ValueError(
			"Expected one of the strings 'x' or 'y' to be passed to the "
			+ "argument 'port_dir'. Instead got '{}'.".format(port_dir))

	return parallel_route_dense(layout, layer, inputs_2d, outputs_2d, 
		port_dir, min_bend_radius=min_bend_radius, spacing=spacing, 
		wg_width=wg_width, seg_length=seg_length, trans=trans, 
		path_output=path_output)







def parallel_route_dense(layout, layer, inputs, outputs, port_dir,
	min_bend_radius=min_bend_radius, spacing=spacing, wg_width=wg_width,
	seg_length=seg_length, trans=null_trans, path_output='pcell'):
	'''
	Routes waveguides from the ith 'input' coordinate to the ith 'output'
	coordinate while trying to minimize the distance between the ports in 
	the direction of the ports. To this end, only 90 degree bend are used to 
	get the most compact length in the port direction while allowing a large
	extent in the direction perpendicular to the ports.

	Args:
        layout:         Layout object for instantiation
                        <pya.Layout object>

        layer:          The index of the layer to insert the paths into (this
                        is the value returned from the layout.layer() method).
                        <int>

		inputs:			An array of shape (2, n) specifying the cartesian
						coordinates of the input ports. This function will
						place inputs in the negative direction along the 
						port direction axis 'port_dir' relative to the
						outputs. For example, if port_dir == 'x', then the
						coordinates of the 'inputs' should be further in the
						negative x direction than the outputs. Must be the
						same shape as 'outputs'
						<np.ndarray>

		outputs:		An array of shape (2, n) specifying the cartesian
						coordinates of the input ports. This function will
						place inputs in the negative direction along the 
						port direction axis 'port_dir' relative to the
						outputs. For example, if port_dir == 'x', then the
						coordinates of the 'inputs' should be further in the
						negative x direction than the outputs. Must be the
						same shape as 'inputs'
						<np.ndarray>

		port_dir:		Specified the port direction, i.e., the direction the
						waveguide goes at the input/output ports. Can be
						either of the strings 'x' or 'y'.
						<str>

		min_bend_radius:This bend radius will be used for the smallest bends
						generated in the routing process. Note that choosing
						a larger bend radius will result in a longer
						interconnect.
						<float or int>
						(default: constants.min_bend_radius == 5)

		spacing:	    Spacing between waveguide edges while they're going in
						the direction perpenicular to the ports. If no two 
						ports are spaced apart by less than this value, then
						'spacing' is the minimum waveguide spacing in the 
						entire interconnection.
						<float or int>
						(default: routing.spacing == 2)

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)

        path_output:    If 'pcell' is passed, paths generated as PCells. 
                        If 'path' is passed, paths generated as DPaths.
                        <str>
                        (default: 'pcell')

    Return:
    	routes:			A list of paths that, together, make up the n to n
    					interconnection. Whether they are round path pcells or
    					DPaths with circular bends depends on the value passed
    					to 'path_output'.
    					<list of pya.DCellInstArray or list of pya.DPath>
	'''
	# initialize a list of paths that will make up the interconnection
	routes = []

	num_ports = inputs.shape[1]

	# Make sure there are the same number of inputs and outputs.
	if num_ports != outputs.shape[1]:
		raise ValueError(
			"The arguments 'inputs' and 'outputs' must have the same shape.")

	# Convert spacing between waveguide edges to spacing between the centers.
	spacing += wg_width

	# Make room in the parallel port direction for the bends to make a 90
	# degree arc.
	radii = min_bend_radius + (np.arange(num_ports) * spacing)
	zeros = np.zeros(num_ports)

	# The 'radial_term' is the displacement vector from the first point in 
	# the path to the path's vertex.
	if port_dir == 'x':
		radial_term = np.stack((radii, zeros))
	elif port_dir == 'y':
		radial_term = np.stack((zeros, radii))
	else:
		raise ValueError(
			"Expected one of the strings 'x' or 'y' to be passed to the "
			+ "argument 'port_dir'. Instead got '{}'.".format(port_dir))


	# Generate coordinates as two separate arrays so that the first and 
	# second bends can have different radii.
	coords1 = np.stack([
		inputs,											# input port
		inputs  + radial_term,							# bend 1 corner
		inputs + radial_term + np.flipud(radial_term)	# bend 1 finished
	])

	# We flip over axis=1 below because the bend radius of the second bend
	# in the ith path equals the bend radius of the first bend in the
	# (num_ports - i)th path.
	coords2 = np.stack([
		inputs + radial_term + np.flipud(radial_term), 	# bend 1 finished
		outputs - np.fliplr(radial_term),				# bend 2 corner
		outputs											# output port
	])

	for i in range(num_ports):
		routes.append(paths.round_path(layout, layer, coords1[:, :, i],
			wg_width=wg_width, seg_length=seg_length,
			trans=trans, output=path_output))
		routes.append(paths.round_path(layout, layer, coords2[:, :, i],
			wg_width=wg_width, seg_length=seg_length,
			trans=trans, output=path_output))

	return routes


def parallel_route_dense_length(num_inputs, spacing=spacing, 
	min_bend_radius=min_bend_radius, wg_width=wg_width):
	'''
	Returns the minimum length of the interconnection generated by 
	'parallel_route_dense' when passed the corresponding arguments.

	Args:
		spacing:	    Spacing between waveguide edges while they're going in
						the direction perpenicular to the ports. If no two 
						ports are spaced apart by less than this value, then
						'spacing' is the minimum waveguide spacing in the 
						entire interconnection.
						<float or int>
						(default: routing.spacing == 2)

		num_inputs:		Number of input ports (which should be the same as
						the number of output ports) to the interconnect. In
						terms of parameters that are passed directly to 
						'parallel_route_dense', this is inputs.shape[1] or
						ouputs.shape[1]

		min_bend_radius:This bend radius will be used for the smallest bends
						generated in the routing process. Note that choosing
						a larger bend radius will result in a longer
						interconnect.
						<float or int>

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)
	'''
	bend1_radius = min_bend_radius
	bend2_radius = min_bend_radius + ((num_inputs - 1) * (spacing + wg_width))
	return bend1_radius + bend2_radius


def parallel_route_dense_spacing(num_inputs, length, 
	min_bend_radius=min_bend_radius, wg_width=wg_width):
	'''
	Returns the spacing between waveguides to be supplied to
	'parallel_route_dense' to obtain the passed interconnection length
	'length' with the corresponding parameters.

	Args:
		num_inputs:		Number of input ports (which should be the same as
						the number of output ports) to the interconnect. In
						terms of parameters that are passed directly to 
						'parallel_route_dense', this is inputs.shape[1] or
						ouputs.shape[1]

		length:			Length of the interconnection in the direction of
						the input/output ports.
						<float or int>

		min_bend_radius:This bend radius will be used for the smallest bends
						generated in the routing process. Note that choosing
						a larger bend radius will result in a longer
						interconnect.
						<float or int>

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)
    '''
	return (length - (2 * min_bend_radius) / (num_inputs - 1)) - wg_width

