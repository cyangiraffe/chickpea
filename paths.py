# This file contains functions for generating various photonic waveguide paths
# in KLayout. 
# Revision History:
# 25 Jun 2019   Julian Sanders  Inital Revision
# 26 Jun 2019   Julian Sanders  Added s-bends
# 28 Jun 2019   Julian Sanders  Debugging and documentation
# 03 Jun 2019   Julian Sanders  Updated constants to be lowercase
# 05 Jul 2019   Julian Sanders  Updated for new package name 'chickpea'.

import math
import pya
import numpy as np
from chickpea.constants import *

def s_bend_shallow_curve(a, b, x):
    '''
    Function defining the curve used for the shallow s-bend.

    Args:
        a - height of the s-bend (also function's value at its local extrema)
        b - slope of the bend at x = 0
        x - position along x axis

    Return
        Value of the function at x
        <float>
    '''
    return (4 * a * x) * (b + 1 - np.abs(x)) / ((b + 1) ** 2)
    

def s_bend_shallow_curve_length(a, b):
    '''
    Gives the path length of the curve bewteen it extrema given the curve 
    parameters supplied to 's_bend_shallow_curve'.

    Args:
        a: height of the s-bend (also function's value at its local extrema)
        b: slope of the bend at x = 0

    Return:
        Length of the curve between the curve's extrema
        <float>
    '''
    p = (b + 1) / 4
    q = 2 * np.sqrt(1 + ((4 * a**2) / ((1 + b)**2)))
    r = (b + 1) * np.arcsinh(2 * a / (1 + b)) / a

    return p * (q + r)


def s_bend_shallow_length(height, length):
    '''
    Gives the path length of the curve bewteen it extrema given the curve 
    parameters supplied to 's_bend_shallow'.

    Args:
        height:	height of the s-bend

        length: distance between curve's extrema. Corresponds to horizontal
        		length of the s-bend's layout.

    Return:
        Length of the curve between the curve's extrema
        <float>
    '''
    return s_bend_shallow_curve_length(height, length - 1)


def s_bend_shallow(layout, height, length, wg_width=wg_width, n_pts='auto',
    seg_length=seg_length):
    '''
    Generates a shallow s-bend path.

    Args:
        layout: Layout object for instantiation
                <pya.Layout object>

        height: Distance between ports in direction perpendicular to
                port direction
                <float>

        length: Distance between ports in direction parallel to
                port direction
                <float>

        wg_width:  Width of the path
                <float>
                (default: constants.wg_width == 0.5)

        n_pts:	Number of points defining the path
        		<int>
        		(default: 100)

    Return:
        The s-bend path
        pya.DPath object

    '''
    # Compute number of points to keep the distance bewteen points on the
    # bend to approximately seg_length
    if n_pts == 'auto':
        n_pts = int(s_bend_shallow_length(height, length) / seg_length)


    x = np.linspace(-length / 2, length / 2, n_pts)
    y = s_bend_shallow_curve(height, length - 1, x)

    # Convert to DPoints
    points = []
    for i in range(n_pts):
        points.append(pya.DPoint(x[i], y[i]))

    return pya.DPath(points, wg_width)


def s_bend_steep(layout, length=0, wg_width=wg_width, bend_radius=bend_radius, 
	n_pts='auto', seg_length=seg_length):
    '''
    Generates a path in the shape of an s-bend. Origin at the lower left port.
    Looks like this, but with rounded corners:

               ------------
               |
               |
               |
    ------------

    Args:
        layout: 		Layout object for instantiation
                		<pya.Layout object>

        length:         Length of straight segment in middle of the s-bend
                        <float>
                        (default: 0)

        wg_width:  		Width of the path
                		<float>
                		(default: constants.wg_width == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)

        n_pts:			Number of points per full circle to use when rounding
        				corners. If 'auto', this is computed based on the
        				value of 'seg_length'.
        				<int or 'auto'>
        				(default: 'auto')

        seg_length:		When rounding corners, gives the distance between the
        				points defining the arc and sets n_pts appropriately.
        				Only used if n_pts == 'auto'.
        				<float>
        				(default: constants.SEG_LEGNTH == 1.0)

    Return:
        The s-bend path
        <pya.DPath object>
    '''
    points = [
    	pya.DPoint(0,               0                       ),
    	pya.DPoint(bend_radius,     0                       ),
    	pya.DPoint(bend_radius,     length + 2 * bend_radius),
    	pya.DPoint(2 * bend_radius, length + 2 * bend_radius)
	]

    return path(layout, points, wg_width=wg_width, bend_radius=bend_radius,
        n_pts=n_pts, seg_length=seg_length)


def path(layout, points, wg_width=wg_width, bend_radius=bend_radius, n_pts='auto', 
    seg_length=seg_length):
    '''
    Generates a path with rounded corners.

    Args:
        layout: 		Layout object for instantiation
                		<pya.Layout object>

        points: 		Points of verticies of manhattan path
               		 	<list of 2-tuples (or 2 x n array-like) of ints>

        wg_width:  		Width of the path
                		<float>
                		(default: constants.wg_width == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)

        n_pts:			Number of points per full circle to use when rounding
        				corners. If 'auto', this is computed based on the
        				value of 'seg_length'.
        				<int or 'auto'>
        				(default: 'auto')

        seg_length:		When rounding corners, gives the distance between the
        				points defining the arc and sets n_pts appropriately.
        				Only used if n_pts == 'auto'.
        				<float>
        				(default: constants.SEG_LEGNTH == 1.0)

    Return:
        The rounded path
        pya.DPath object

    '''
    # Compute number of points to keep the distance bewteen points on the
    # circle to seg_length
    if n_pts == 'auto':
        n_pts = 2 * math.pi * bend_radius / seg_length

    # If elements of 'points' aren't DPoints, try to convert them.
    if isinstance(points[0], pya.DPoint) == False:
        for point, idx in enumerate(points):
            points[idx] = pya.DPoint(p[0], p[1])

    path = pya.DPath(points, wg_width)

    return path.round_corners(bend_radius, n_pts, layout.dbu)
