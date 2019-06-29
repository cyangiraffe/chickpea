# This file contains functions generating layouts of passive photonic components

# Revsion History:
# 26 Jun 2019   Julian Sanders  Initial Revision - added directional coupler
# 28 Jun 2019   Julian Sanders  Debugging and documentation. Added ability to
#                               divide directional coupler into 6 cells for
#                               easy modification upon import into lumerical.
#                               Also split into two functions.

import pya
from pic_component_library.constants import *
from pic_component_library import paths



def dir_coupler(layout, cell, layer, length, sep=0.2, width=WIDTH, 
    bend_radius=BEND_RADIUS, seg_length=SEG_LENGTH, n_pts='auto'):
    '''
    Generates layout of a directional coupler like the one shown below. 
    Inserts the coupler into the passed cell and layer. The center of the 
    lower left waveguide port is at the origin. In the diagram below, 
    the origin would be around the X's.
    

    Args:
        layout:         Layout object for instantiation
                        <pya.Layout object>

        height:         Distance between ports in direction perpendicular to
                        port direction
                        <float>

        length:         Coupling distance. Length of the straight waveguides 
                        separatedby the distance 'sep'.
                        <float>

        sep:            Distance between edges of waveguides in the straight 
                        section of the coupler. I.e., min oxide thickness
                        between the waveguides.
                        <float>
                        (default: 0.2)

        width:          Width of the path
                        <float>
                        (default: constants.WIDTH == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.BEND_RADIUS == 10.0)

        n_pts:          Number of points per full circle to use when rounding
                        corners. If 'auto', this is computed based on the
                        value of 'seg_length'.
                        <int or 'auto'>
                        (default: 'auto')

        seg_length:     When rounding corners, gives the distance between the
                        points defining the arc and sets n_pts appropriately.
                        Only used if n_pts == 'auto'.
                        <float>
                        (default: constants.SEG_LEGNTH == 1.0)

    Diagram:
        ,:;,.                                                            .,;:'
        .'',,,,'.                                                    .';,,,''.
              .,:;.                                                .;;'.      
                 ':,                                              ;:.         
                  .:;                                           .::           
                   .;,                                          ;:            
                    ;;.                                        .;'            
                    ';.                                        ';.            
                    .;'                                        ,;.            
                     ::                                       .;,             
                     .;;                                     .::              
                      .;:.                                  .:,               
                        .;;.                              .;;.                
                          .,;::::::::::::::::::::::::::::,,.                  
                        
                          .,;::::::::::::::::::::::::::::,;,.                  
                        ':;.                              .;;.                
                      .:;.                                  .:;.              
                     .;,                                      ::.             
                     :;                                       .:;             
                    .;.                                        ,;.            
                    ';.                                        ';.            
                    ;:                                         .;,            
                   .;'                                          ;;.           
                  .;,                                            ;:.          
                 ,;'                                              ,:'         
              .,;,.                                                .,;,.      
        XX,,,,,.                                                      ',,,,,'.
        XX,..                                                            .',;.
    

    '''

    # Generate the paths for the directional coupler
    input1, straight1, output1, input2, straight2, output2 = dir_coupler_paths(
        layout, length, sep=sep, width=width, bend_radius=bend_radius, 
        seg_length=seg_length, n_pts=n_pts)

    if cell == 'divide':
        # Segregate each path to its own cell to facilitate parameter sweeps.
        cell_input1 = layout.create_cell('input1')
        cell_input2 = layout.create_cell('input2')
        cell_output1 = layout.create_cell('output1')
        cell_output2 = layout.create_cell('output2')
        cell_straight1 = layout.create_cell('straight1')
        cell_straight2 = layout.create_cell('straight2')

        cell_input1.shapes(layer).insert(input1)
        cell_input2.shapes(layer).insert(input2)
        cell_output1.shapes(layer).insert(output1)
        cell_output2.shapes(layer).insert(output2)
        cell_straight1.shapes(layer).insert(straight1)
        cell_straight2.shapes(layer).insert(straight2)

        null_trans = pya.DTrans(0, 0)   # transformation does nothing
        top = layout.cell(0)            # get top-level cell in the heirarchy

        # Instatiate each cell as a subcell of 'top'.
        top.insert(pya.DCellInstArray(cell_input1.cell_index(), null_trans))
        top.insert(pya.DCellInstArray(cell_input2.cell_index(), null_trans))
        top.insert(pya.DCellInstArray(cell_output1.cell_index(), null_trans))
        top.insert(pya.DCellInstArray(cell_output2.cell_index(), null_trans))
        top.insert(pya.DCellInstArray(cell_straight1.cell_index(), null_trans))
        top.insert(pya.DCellInstArray(cell_straight2.cell_index(), null_trans))

    else:
        # Insert the paths into the passed cell so that the user can customize
        # the coupler's placement in their layout by transforming the cell.
        cell.shapes(layer).insert(input1)
        cell.shapes(layer).insert(input2)
        cell.shapes(layer).insert(output1)
        cell.shapes(layer).insert(output2)
        cell.shapes(layer).insert(straight1)
        cell.shapes(layer).insert(straight2)

    return


def dir_coupler_paths(layout, length, sep=0.2, width=WIDTH, 
    bend_radius=BEND_RADIUS, seg_length=SEG_LENGTH, n_pts='auto'):
    '''
    Generates layout of a directional coupler like the one shown below. 
    Inserts the coupler into the passed cell and layer. The center of the 
    lower left waveguide port is at the origin. In the diagram below, 
    the origin would be around the X's.
    

    Args:
        layout:         Layout object for instantiation
                        <pya.Layout object>

        height:         Distance between ports in direction perpendicular to
                        port direction
                        <float>

        length:         Coupling distance. Length of the straight waveguides 
                        separatedby the distance 'sep'.
                        <float>

        sep:            Distance between edges of waveguides in the straight 
                        section of the coupler. I.e., min oxide thickness
                        between the waveguides.
                        <float>
                        (default: 0.2)

        width:          Width of the path
                        <float>
                        (default: constants.WIDTH == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.BEND_RADIUS == 10.0)

        n_pts:          Number of points per full circle to use when rounding
                        corners. If 'auto', this is computed based on the
                        value of 'seg_length'.
                        <int or 'auto'>
                        (default: 'auto')

        seg_length:     When rounding corners, gives the distance between the
                        points defining the arc and sets n_pts appropriately.
                        Only used if n_pts == 'auto'.
                        <float>
                        (default: constants.SEG_LEGNTH == 1.0)

    Diagram:
        ,:;,.                                                            .,;:'
        .'',,,,'.                                                    .';,,,''.
              .,:;.                                                .;;'.      
                 ':,                                              ;:.         
                  .:;                                           .::           
                   .;,                                          ;:            
                    ;;.                                        .;'            
                    ';.                                        ';.            
                    .;'                                        ,;.            
                     ::                                       .;,             
                     .;;                                     .::              
                      .;:.                                  .:,               
                        .;;.                              .;;.                
                          .,;::::::::::::::::::::::::::::,,.                  
                        
                          .,;::::::::::::::::::::::::::::,;,.                  
                        ':;.                              .;;.                
                      .:;.                                  .:;.              
                     .;,                                      ::.             
                     :;                                       .:;             
                    .;.                                        ,;.            
                    ';.                                        ';.            
                    ;:                                         .;,            
                   .;'                                          ;;.           
                  .;,                                            ;:.          
                 ,;'                                              ,:'         
              .,;,.                                                .,;,.      
        XX,,,,,.                                                      ',,,,,'.
        XX,..                                                            .',;.
    
    Return:
        input1:     Lower-left s-bend

        straight1:  Lower straight segment for coupling

        output1:    Lower-right s-bend

        input2:     Upper-left s-bend

        straight2:  Upper straight segment for coupling

        output2:    Upper-right s-bend

    '''

    # Set up the s-bends leading into/out of the straight coupling portion

    flipy_shiftx = pya.DTrans(  # transform lower left arm into lower right arm
        pya.DTrans.M90,                     # mirror across y
        4 * bend_radius + length,           # right by 4r + l
        0)                                  # same vertical
    
    flipx_shifty = pya.DTrans(  # transform lower left arm into upper left arm
        pya.DTrans.M0,                      # mirror across x
        0,                                  # same horizontal
        4 * bend_radius + sep + width)      # up by 4r + l + width

    shift_diag   = pya.DTrans(  # transform lower left arm into upper right arm
        2 * bend_radius + length,           # up by 2r + l
        2 * bend_radius + sep + width)      # right by 2r + sep + width

    # Generate lower left arm and apply transformation to get the rest
    input1  = paths.s_bend_steep(layout, width=width, bend_radius=bend_radius,
        seg_length=seg_length, n_pts=n_pts)
    input2  = input1.transformed(flipx_shifty)
    output1 = input1.transformed(flipy_shiftx)
    output2 = input1.transformed(shift_diag)

    # Generate the straight segments for coupling

    bottom_points = [
        pya.DPoint(2 * bend_radius,          2 * bend_radius),
        pya.DPoint(2 * bend_radius + length, 2 * bend_radius)
    ]

    straight1 = pya.DPath(bottom_points, width)

    sep_waveguides = pya.DTrans(pya.DPoint(0, sep + width))
    straight2 = straight1.transformed(sep_waveguides)

    return input1, straight1, output1, input2, straight2, output2
