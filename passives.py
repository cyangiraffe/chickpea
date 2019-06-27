# This file contains functions generating layouts of passive photonic components

# Revsion History
# 26 Jun 2019   Julian Sanders  Initial Revision - added dir'nal coupler

from constants import *

def dir_coupler(layout, cell, layer, length, sep=0.2, width=WIDTH, bend_radius=BEND_RADIUS):
    '''
    Generates layout of a directional coupler. Inserts the coupler into the
    passed cell and layer
    
    Args:
        length: Length of the straight coupling region. Approx. coupling length
        sep:    Distance between edges of waveguides in the straight section
                of the coupler. I.e., min oxide thickness between waveguides.
                float

    '''

    # Set up the s-bends leading into/out of the straight coupling portion

    flipy_shiftx = pya.DTrans(pya.DTrans.M90, 4 * bend_radius + length, 0)
    flipx_shifty = pya.DTrans(pya.DTrans.M0, 0, 4 * bend_radius + sep)
    shift_diag   = pya.DTrans(2 * bend_radius + length, 2 * bend_radius + sep)

    input1  = s_bend_steep(layout, width=width, bend_radius=bend_radius)
    input2  = input1.transformed(flipx_shifty)
    output1 = input1.transformed(flipy_shiftx)
    output2 = input1.transformed(shift_diag)

    # Generate the straight segments for coupling

    bottom_points = [
        DPoint(2 * bend_radius,          2 * bend_radius),
        DPoint(2 * bend_radius + length, 2 * bend_radius)
    ]

    straight1 = DPath(bottom_points, width)
    straight2 = straight1.transformed(0, sep)

    # Insert the paths into the cell

    cell.shapes(layer).insert(input1)
    cell.shapes(layer).insert(input2)
    cell.shapes(layer).insert(output1)
    cell.shapes(layer).insert(output2)
    cell.shapes(layer).insert(straight1)
    cell.shapes(layer).insert(straight2)

    return
