# This file contains functions that will generate photonic couplers.
# It contains the following top-level functions:
# 
#   dir_coupler             Generates a directional coupler
#
#   dir_coupler_ports       Calculates the coordinates of the ports of the
#                           directional coupler generated by dir_coupler.
#
#   dir_coupler_center      Calculates the coordinates of the center of the
#                           directional coupler generated by dir_coupler.
#
#   dir_coupler_length      Calculates the length of the directional coupler
#                           generated by dir_coupler.
#
#   dir_coupler_height      Calculates the height of the directional coupler
#                           generated by dir_coupler.

# Revsion History:
# 26 Jun 2019   Julian Sanders  Initial Revision - added directional coupler
# 28 Jun 2019   Julian Sanders  Debugging and documentation. Added ability to
#                               divide directional coupler into 6 cells for
#                               easy modification upon import into lumerical.
#                               Also split into two functions.
# 01 Jun 2019   Julian Sanders  Added function 'dir_coupler_varfdtd', which 
#                               generates a lumerical script to simulate the
#                               directional coupler generated by dir_coupler.
# 02 Jun 2019   Julian Sanders  Got script generation function working, but
#                               package must be installed in AppData directory
#                               for KLayout.
# 03 Jul 2019   Julian Sanders  Cleaned up script generation function. Made
#                               constants lowercase.
# 05 Jul 2019   Julian Sanders  Updated for new package name 'chickpea'.
# 08 Jul 2019   Julian Sanders  Lengths of directional coupler arms can now
#                               be individually adjusted.
# 13 Jul 2019   Julian Sanders  Can now generate directional couplers with 
#                               shallow s-bends for arms. The arm shape is no
#                               longer parameterized by bend raidus. Instead 
#                               each s-bend has its length and height specified,
#                               from which the bend radius is computed.

import pya
from chickpea.constants import *
from chickpea import paths
import os.path

#
# Local constants
#

sep = 0.2   # default separation between directional coupler waveguies


#
# Functions
#

def dir_coupler(layout, cell, layer, coupling_length, arm_lengths=16, 
    arm_heights=8, sep=sep, wg_width=wg_width, seg_length=seg_length, 
    n_pts='auto', origin='port0'):
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

        coupling_length:Length of the straight waveguides 
                        separated by the distance 'sep'.
                        <float>

        sep:            Distance between edges of waveguides in the straight 
                        section of the coupler. I.e., min oxide thickness
                        between the waveguides.
                        <float>
                        (default: 0.2)

        arm_lengths:    Length in x direction of the s-bends leading into/
                        out of the straight couling waveguides.

                        If a scalar, every arm will have the same length.

                        If a list, its entries will correspond to the arms
                        in the following positions:
                            [lower left, upper left, lower right, upper right]

                        If a dict, the keys should be 'lower left', 
                        'upper left', 'lower right', or 'upper right'.

                        <float or list(float) or dict(str: float)> 
                        (default: 16)

        arm_heights:    Length in y direction of the s-bends leading into/
                        out of the straight couling waveguides.

                        If a scalar, every arm will have the same length.

                        If a list, its entries will correspond to the arms
                        in the following positions:
                            [lower left, upper left, lower right, upper right]

                        If a dict, the keys should be 'lower left', 
                        'upper left', 'lower right', or 'upper right'.

                        <float or list(float) or dict(str: float)> 
                        (default: 8)

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)

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

        origin:         Indicates the location of the origin relative to 
                        the directional coupler. Can be 'port0' or 'center'.

                        value       origin location
                        -----------------------------------------------------
                        'port0'     Lower left port
                        'center'    Center relative to max device dimensions

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
        layout, coupling_length, arm_lengths=arm_lengths, arm_heights=arm_heights, 
        sep=sep, wg_width=wg_width,
        seg_length=seg_length, n_pts=n_pts, origin=origin)

    if cell == 'divide':    # Divide coupler into 6 cells
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

    else:   # Insert the coupler into the passed cell
        # Insert the paths into the passed cell so that the user can customize
        # the coupler's placement in their layout by transforming the cell.
        cell.shapes(layer).insert(input1)
        cell.shapes(layer).insert(input2)
        cell.shapes(layer).insert(output1)
        cell.shapes(layer).insert(output2)
        cell.shapes(layer).insert(straight1)
        cell.shapes(layer).insert(straight2)

    return


def dir_coupler_paths(layout, coupling_length, sep=sep, arm_lengths=16,
    arm_heights=8, wg_width=wg_width, seg_length=seg_length, n_pts='auto', 
    origin='port0'):
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

        coupling_length: Length of the straight waveguides 
                         separatedby the distance 'sep'.
                         <float>

        sep:            Distance between edges of waveguides in the straight 
                        section of the coupler. I.e., min oxide thickness
                        between the waveguides.
                        <float>
                        (default: 0.2)

        arm_length:     Length of the straight section of the S-bend arms
                        leading into the coupling section of the coupler.

                        If a scalar, every arm will have the same length.

                        If a list, its entries will correspond to the arms
                        in the following positions:
                            [lower left, upper left, lower right, upper right]

                        If a dict, the keys should be 'lower left', 
                        'upper left', 'lower right', or 'upper right'.

                        <float or list(float) or dict(str: float)> 
                        (default: 0)

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)

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

        origin:         Indicates the location of the origin relative to 
                        the directional coupler. Can be 'port0' or 'center'.

                        value       origin location
                        -----------------------------------------------------
                        'port0'     Lower left port
                        'center'    Center relative to max device dimensions

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
    #
    # Set up the s-bends leading into/out of the straight coupling portion
    #

    # If arm_lengths or arm_heights is not passed as a list, convert it

    arm_lengths = parse_arm_length(arm_lengths)
    arm_heights = parse_arm_length(arm_heights)

    for arm in arm_lengths:
        print(arm)

    # Generate each s-bend with the requested length
    input1 = paths.s_bend(layout, length=arm_lengths[0], height=arm_heights[0], 
        wg_width=wg_width, seg_length=seg_length, n_pts=n_pts)
    input2 = paths.s_bend(layout, length=arm_lengths[1], height=arm_heights[1], 
        wg_width=wg_width, seg_length=seg_length, n_pts=n_pts)
    output1 = paths.s_bend(layout, length=arm_lengths[2], height=arm_heights[2], 
        wg_width=wg_width, seg_length=seg_length, n_pts=n_pts)
    output2 = paths.s_bend(layout, length=arm_lengths[3], height=arm_heights[3], 
        wg_width=wg_width, seg_length=seg_length, n_pts=n_pts)


    # Now we'll need some transformations for getting the s-bends output by
    # 's_bend_steep' into the right positions for the coupler.

    flipy_shiftx = pya.DTrans(  # lower left arm -> lower right arm
        pya.DTrans.M90,                # mirror across y
        arm_lengths[0] + arm_lengths[2] + coupling_length,  # shift right 
        arm_heights[0] - arm_heights[2])           # adjust for height diff b/w lower arms

    flipx_shifty = pya.DTrans(  # lower left arm -> upper left arm
        pya.DTrans.M0,                  # mirror across x
        arm_lengths[0] - arm_lengths[1],            # adjust for length diff b/w left arms
        arm_heights[0] + arm_heights[1] + sep + wg_width)    # move up

    shift_diag = pya.DTrans(pya.DPoint(  # lower left arm -> upper right arm
        arm_lengths[0] + coupling_length,                          # shift right
        arm_heights[0] + sep + wg_width))                 # shift up

    input2  = input2.transformed(flipx_shifty)
    output1 = output1.transformed(flipy_shiftx)
    output2 = output2.transformed(shift_diag)


    #
    # Generate the straight segments for coupling
    #

    bottom_points = [
        pya.DPoint(arm_lengths[0],                   arm_heights[0]),
        pya.DPoint(arm_lengths[0] + coupling_length, arm_heights[0])
    ]

    straight1 = pya.DPath(bottom_points, wg_width)

    sep_waveguides = pya.DTrans(pya.DPoint(0, sep + wg_width))
    straight2 = straight1.transformed(sep_waveguides)

    # If the origin is at the center, transform paths appropriately
    if origin == 'center':
        cx, cy = dir_coupler_center(
            coupling_length, arm_lengths, arm_heights, sep, wg_width=wg_width)
        origin_to_center = pya.DTrans(pya.DPoint(-cx, -cy))

        straight1  = straight1.transformed(origin_to_center)
        straight2  = straight2.transformed(origin_to_center)
        input1     = input1.transformed(origin_to_center)
        input2     = input2.transformed(origin_to_center)
        output1    = output1.transformed(origin_to_center)
        output2    = output2.transformed(origin_to_center)

    return input1, straight1, output1, input2, straight2, output2


def parse_arm_length(arm_length):
    '''
    If arm length is not passed as a list, return the corresponding list.

    Args:
        arm_length:     Length of the straight section of the S-bend arms
                        leading into the coupling section of the coupler.

                        If a scalar, every arm will have the same length.

                        If a list, its entries will correspond to the arms
                        in the following positions:
                            [lower left, upper left, lower right, upper right]

                        If a dict, the keys should be 'lower left', 
                        'upper left', 'lower right', or 'upper right'.

                        <float or list(float) or dict(str: float)> 
    Return:
        A list containing the information implied by the argument.
    '''
    arm_length_list = []

    if type(arm_length) == dict:
        arm_order = ['lower left', 'upper left', 'lower right', 'upper right']
        for arm in arm_order:
            try: arm_length_list.append(arm_length[arm])
            except KeyError:

                err = "Keys of 'arm_length' must include '{arm_order[0]}', "\
                    + "'{arm_order[1]}', '{arm_order[2]}', "\
                    + "and '{arm_order[3]}'."
                raise KeyError(err.format(arm_order=arm_order))

    elif type(arm_length) == float or type(arm_length) == int:
        arm_length_list = [arm_length] * 4

    elif type(arm_length) == list:
        arm_length_list = arm_length

    else:
        raise TypeError('Argument must be a float or list(float) or'
                      + 'dict(str: float)')

    return arm_length_list


def dir_coupler_length(coupling_length, arm_lengths=16):
    '''
    Computes full device length of the directional coupler generated by
    'dir_coupler' given parameters 'coupling_length' and 'bend_radius'. Height
    refers to the dimension of the coupler parallel to port direction;
    also the x-direction if the output of 'dir_coupler' isn't rotated.

    Args:
        coupling_length: Length of the straight waveguides 
                        separatedby the distance 'sep'.
                        <float>

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)
    
    Return:
        Directional coupler device length.
        <float>
    '''

    arm_lengths = parse_arm_length(arm_lengths)

    left_arm_length = max(arm_lengths[0:2])
    right_arm_length = max(arm_lengths[2:4])

    return left_arm_length + coupling_length + right_arm_length


def dir_coupler_height(arm_heights=8, sep=sep, wg_width=wg_width):
    '''
    Computes full device height of the directional coupler generated by
    'dir_coupler' given parameters 'sep', 'wg_width', and 'bend_radius'. Height
    refers to the dimension of the coupler perpendicular to port direction;
    also the y-direction if the output of 'dir_coupler' isn't rotated.

    Args:
        sep:            Distance between edges of waveguides in the straight 
                        section of the coupler. I.e., min oxide thickness
                        between the waveguides.
                        <float>
                        (default: 0.2)

        wg_width:       Width of the waveguide
                        <float>
                        (default: constants.wg_width == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)
    
    Return:
        Directional coupler device height.
        <float>
    '''

    arm_heights = parse_arm_length(arm_heights)

    upper_arm_height = max(arm_heights[1], arm_heights[3])
    lower_arm_height = max(arm_heights[0], arm_heights[2])

    return lower_arm_height + sep + upper_arm_height + (2 * wg_width)


def dir_coupler_center(coupling_length, arm_lengths=16, arm_heights=8, sep=sep,
    wg_width=wg_width):
    '''
    Computes the center of the directional coupler generated by 'dir_coupler'
    when supplied with these arguments. The center is defined as the center of
    the smallest rectangle that can completely enclose the coupler.
    '''
    total_length = dir_coupler_length(coupling_length, arm_lengths)
    total_height = dir_coupler_height(arm_heights, sep, wg_width)

    center_x = total_length / 2
    center_y = total_height / 2

    return center_x, center_y


def dir_coupler_ports(coupling_length, arm_lengths=16, arm_heights=8, sep=sep,
    wg_width=wg_width, origin='port0'):
    '''
    Computes the coordinates of each port of the directional coupler generated
    by 'dir_coupler' when supplied with these arguments.
    '''

    # If arm_lengths or arm_heights is not passed as a list, convert it

    arm_lengths = parse_arm_length(arm_lengths)
    arm_heights = parse_arm_length(arm_heights)

    ports = []  # list of port coordinates

    ports.append((0, 0))    # lower left port

    ports.append((          # upper left port
        arm_lengths[0] - arm_lengths[1],
        arm_heights[0] + sep + wg_width + arm_heights[1]
    ))

    ports.append((          # lower right port
        arm_lengths[0] + coupling_length + arm_lengths[2],
        arm_heights[0] - arm_heights[2]
    ))

    ports.append((          # upper right port
        arm_lengths[0] + coupling_length + arm_lengths[3],
        arm_heights[0] + sep + wg_width + arm_heights[3]
    ))

    # If the origin is at the center, transform port coords appropriately
    if origin == 'center':
        cx, cy = dir_coupler_center(coupling_length, arm_lengths, arm_heights, sep,
                                    wg_width=wg_width)
        for idx, port in enumerate(ports):
            ports[idx] = (port[0] - cx, port[1] - cy)

    return ports


def dir_coupler_varfdtd(save_path, gds_path, coupling_length, sep=sep,  
    wg_width=wg_width, bend_radius=bend_radius):
    '''
    THIS FUNCTION IS OUT OF DATE. No guarantees it'll work.

    This function generates a lumerical script file that will set up a varFDTD
    simulation for the directional coupler generated with 'dir_coupler' when
    passed arguemnts 'coupling_length', 'sep', 'wg_width', and 'bend_radius'. The
    script file is saved to the passed directory 'save_path'.

    Args:
        save_path:      Path to which the generated script file is saved, 
                        including file name. If just a file name is passed, 
                        the file might get saved to the KLayout installation 
                        directory, though I'm not sure.
                        <str>

        gds_path:       Path to the GDS of the directional coupler to simulate.
                        <str>

        coupling_length: Length of the straight waveguides 
                        separated by the distance 'sep'.
                        <float>

        sep:            Distance between edges of waveguides in the straight 
                        section of the coupler. I.e., min oxide thickness
                        between the waveguides.
                        <float>
                        (default: 0.2)

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)
    '''
    template_path = os.path.abspath(
        'python\\chickpea\\lumerical_template_scripts'
        '\\varfdtd_setup_dir_coupler.lsf')

    # Clear contents of old script, if one exists
    with open(save_path, 'w') as old_script:
        old_script.write('')

    # Clear contents of old script, if one exists
    with open(save_path, 'w') as old_script:
        old_script.write('')

    # Transcribe and fill in template to script line-by-line
    with open(template_path, 'r') as template:
        with open(save_path, 'a') as script:
            for line in template:
                formatted_line = line.format(
                    gds_path=gds_path,
                    bend_radius=bend_radius,
                    sep=sep,
                    length=coupling_length,
                    wg_width=wg_width)

                script.write(formatted_line)
    return


def dir_coupler_fdtd(save_path, gds_path, coupling_length, sep=sep,  
    wg_width=wg_width, bend_radius=bend_radius):
    '''
    THIS FUNCTION IS OUT OF DATE. It will only work for the special case in
    which all directional coupler arms are the same length and height, and
    height == length. The bend radius will then just be length / 2, which can
    be supplied as the bend_raidus argument to this function. The rest of the
    arguments should correspond to the arguments to 'dir_coupler'.

    This function generates a lumerical script file that will set up a FDTD
    simulation for the directional coupler generated with 'dir_coupler' when
    passed arguemnts 'coupling_length', 'sep', 'wg_width', and 'bend_radius'. The
    script file is saved to the passed directory 'save_path'.

    Args:
        save_path:      Path to which the generated script file is saved, 
                        including file name. If just a file name is passed, 
                        the file might get saved to the KLayout installation 
                        directory, though I'm not sure.
                        <str>

        gds_path:       Path to the GDS of the directional coupler to simulate.
                        <str>

        coupling_length: Length of the straight waveguides 
                         separated by the distance 'sep'.
                         <float>

        sep:            Distance between edges of waveguides in the straight 
                        section of the coupler. I.e., min oxide thickness
                        between the waveguides.
                        <float>
                        (default: 0.2)

        wg_width:       Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)
    '''
    template_path = os.path.abspath(
        'python\\chickpea\\lumerical_template_scripts'
        '\\fdtd_setup_dir_coupler.lsf')

    # Clear contents of old script, if one exists
    with open(save_path, 'w') as old_script:
        old_script.write('')

    # Clear contents of old script, if one exists
    with open(save_path, 'w') as old_script:
        old_script.write('')

    # Transcribe and fill in template to script line-by-line
    with open(template_path, 'r') as template:
        with open(save_path, 'a') as script:
            for line in template:
                formatted_line = line.format(
                    gds_path=gds_path,
                    bend_radius=bend_radius,
                    sep=sep,
                    length=coupling_length,
                    wg_width=wg_width)

                script.write(formatted_line)
    return
