# This file contains functions for generating various photonic waveguide paths
# in KLayout. 
# Revision History:
#   Julian Sanders  25 Jun 2019 Inital Revision
#   Julian Sanders  26 Jun 2019 Added s-bends

import math
import numpy as np
import pya
from constants import *

def s_bend_shallow_curve(a, b, x):
    '''
    Function defining the curve used for the s bend

    Args:
        a - height of the s-bend
        b - slope of the bend at x = 0
        x - position along x axis

    Return
        Value of the function at x
    '''
    return (4 * a * x)(b + 1 - np.abs(x)) / ((b + 1) ** 2)
    

def s_bend_shallow_curve_length(a, b):
    '''
    Function defining the curve used for the s bend

    Args:
        a - height of the s-bend
        b - slope of the bend at x = 0
        x - position along x axis

    Return
        Length of the curve between the curve's extrema
    '''
    p = (b + 1) / 4
    q = 2 * np.sqrt(1 + ((4 * a**2) / ((1 + b)**2)))
    r = (b + 1) * np.arcsinh(2 * a / (1 + b)) / a

    return p * (q + r)


def s_bend_shallow_length(height, length):
    '''
    Function defining the curve used for the s bend

    Args:
        a - height of the s-bend
        b - slope of the bend at x = 0
        x - position along x axis

    Return
        Length of the curve between the curve's extrema
    '''
    return s_bend_shallow_curve_length(height, length - 1)


def s_bend_shallow(layout, height, length, width=WIDTH, n_pts=100):
    '''
    Generates a shallow s-bend path.

    Args:
        layout: Layout object for instantiation
                pya.Layout object

        height: Distance between ports in direction perpendicular to
                port direction
                float

        length: Radius of corner arcs
                float

    Return:
        path: The s-bend path
              pya.DPath object

    '''
    x = np.linspace(0, length, n_pts)
    b = length - 1
    y = s_bend_shallow_curve(height, length, x)

    # Convert to DPoints
    points = []
    for i in range(n_pts):
        points.append(DPoint(x[i], y[i]))

    return pya.DPath(points, width)


def s_bend_steep(layout, length=0, width=WIDTH, bend_radius=BEND_RADIUS, n_pts=None, 
    seg_length=SEG_LENGTH):
    '''
    Generates a path in the shape of an s-bend. Origin at the lower left port.
    Looks like this, but with rounded corners:

                 ---------------
                 |
                 |
                 |
    --------------

    Args:
        layout:         Layout object for instantiation
                        pya.Layout object

        length:         Length of straight segment in middle of the s-bend
                        float

        bend_radius:    Radius of corner arcs
                        float

    Return:
        path: The s-bend path
              pya.DPath object
    '''
    points = [pya.DPoint(0, 0)]   # init a list of points

    points.append(pya.DPoint(bend_radius, 0))
    points.append(pya.DPoint(bend_radius, length + 2 * bend_radius))
    points.append(pya.DPoint(2 * bend_radius, length + 2 * bend_radius))

    return path(layout, points, width=width, bend_radius=bend_radius,
        n_pts=n_pts, seg_length=seg_length)


def path(layout, points, width=WIDTH, bend_radius=BEND_RADIUS, n_pts='auto', 
    seg_length=SEG_LENGTH):
    '''
    Generates a path with rounded corners.

    Args:
        layout: Layout object for instantiation
                pya.Layout object
        points: Points of verticies of manhattan path
                list of 2-tuples (or 2 x n array-like) of ints
        width:  Width of the path
                float

    Return:
        path: The rounded path
              pya.DPath object

    '''
    # Compute number of points to keep the distance bewteen points on the
    # circle to seg_length
    if n_pts == 'auto':
        n_pts = 2 * math.pi * bend_radius / seg_length

    # If elements of 'points' aren't DPoints, try to convert them.
    if points[0].is_instance(pya.DPoint) == False:
        for point, idx in enumerate(points):
            points[idx] = pya.DPoint(p[0], p[1])

    path = pya.DPath(points, width)

    path = path.round_corners(bend_radius, n_pts, layout.dbu)

    return path
