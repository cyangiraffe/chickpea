# This file contains functions generating layouts of passive photonic components

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

def dir_coupler(layout, cell, layer, length, sep=sep, arm_length=0, 
    wg_width=wg_width, bend_radius=bend_radius, seg_length=seg_length, 
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

        length:         Coupling distance. Length of the straight waveguides 
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

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)

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
        layout, length, sep=sep, wg_width=wg_width, bend_radius=bend_radius, 
        seg_length=seg_length, n_pts=n_pts, arm_length=arm_length, 
        origin=origin)

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


def dir_coupler_paths(layout, length, sep=sep, arm_length=0, wg_width=wg_width, 
    bend_radius=bend_radius, seg_length=seg_length, n_pts='auto',
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

        length:         Coupling distance. Length of the straight waveguides 
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

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)

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

    # If arm length is not passed as a list, generate the appropriate list
    # and store it in 'arm_length_list'.

    arm_length = parse_arm_length(arm_length)

    # Generate each s-bend with the requested length
    input1 = paths.s_bend_steep(layout, arm_length[0], wg_width=wg_width, 
        bend_radius=bend_radius, seg_length=seg_length, n_pts=n_pts)
    input2 = paths.s_bend_steep(layout, arm_length[1], wg_width=wg_width, 
        bend_radius=bend_radius, seg_length=seg_length, n_pts=n_pts)
    output1 = paths.s_bend_steep(layout, arm_length[2], wg_width=wg_width, 
        bend_radius=bend_radius, seg_length=seg_length, n_pts=n_pts)
    output2 = paths.s_bend_steep(layout, arm_length[3], wg_width=wg_width, 
        bend_radius=bend_radius, seg_length=seg_length, n_pts=n_pts)


    # Now we'll need some transformations for getting the s-bends output by
    # 's_bend_steep' into the right positions for the coupler.

    flipy_shiftx = pya.DTrans(  # lower left arm -> lower right arm
        pya.DTrans.M90,                # mirror across y
        4 * bend_radius + length,      # right by 4r + l
        arm_length[0] - arm_length[2]) # adjust for length diff b/w lower arms
    
    device_height_left = (      # distance between left side ports
        2 * bend_radius + arm_length[0] +   # lower arm total length
        2 * bend_radius + arm_length[1] +   # upper arm total length
        sep + wg_width)                     # length from coupling gap

    flipx_shifty = pya.DTrans(  # lower left arm -> upper left arm
        pya.DTrans.M0,                      # mirror across x
        0,                                  # same horizontal
        device_height_left)                 # move up

    shift_diag = pya.DTrans(pya.DPoint(  # lower left arm -> upper right arm
        2 * bend_radius + length,                          # shift right
        2 * bend_radius + arm_length[0] + sep + wg_width)) # shift up

    # Generate the straight segments for coupling

    bottom_points = [
        pya.DPoint(2 * bend_radius,          2 * bend_radius + arm_length[0]),
        pya.DPoint(2 * bend_radius + length, 2 * bend_radius + arm_length[0])
    ]

    straight1 = pya.DPath(bottom_points, wg_width)

    sep_waveguides = pya.DTrans(pya.DPoint(0, sep + wg_width))
    straight2 = straight1.transformed(sep_waveguides)

    input2  = input2.transformed(flipx_shifty)
    output1 = output1.transformed(flipy_shiftx)
    output2 = output2.transformed(shift_diag)

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
        raise TypeError('Argument must be a float or list(float) or dict(str: float)')

    return arm_length_list


def dir_coupler_length(length, bend_radius=bend_radius):
    '''
    Computes full device length of the directional coupler generated by
    'dir_coupler' given parameters 'length' and 'bend_radius'. Height
    refers to the dimension of the coupler parallel to port direction;
    also the x-direction if the output of 'dir_coupler' isn't rotated.

    Args:
        length:         Coupling distance. Length of the straight waveguides 
                        separatedby the distance 'sep'.
                        <float>

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)
    
    Return:
        Directional coupler device length.
        <float>
    '''
    return length + 4 * bend_radius


def dir_coupler_height(sep=sep, wg_width=wg_width, bend_radius=bend_radius):
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

        wg_width:          Width of the path
                        <float>
                        (default: constants.wg_width == 0.5)

        bend_radius:    Radius of corner arcs
                        <float>
                        (default: constants.bend_radius == 10.0)
    
    Return:
        Directional coupler device height.
        <float>
    '''
    return (4 * bend_radius) + (2 * wg_width) + sep


def dir_coupler_varfdtd(save_path, gds_path, length, sep=sep,  
    wg_width=wg_width, bend_radius=bend_radius):
    '''
    This function generates a lumerical script file that will set up a varFDTD
    simulation for the directional coupler generated with 'dir_coupler' when
    passed arguemnts 'length', 'sep', 'wg_width', and 'bend_radius'. The
    script file is saved to the passed directory 'save_path'.

    Args:
        save_path:      Path to which the generated script file is saved, 
                        including file name. If just a file name is passed, 
                        the file might get saved to the KLayout installation 
                        directory, though I'm not sure.
                        <str>

        gds_path:       Path to the GDS of the directional coupler to simulate.
                        <str>

        length:         Coupling distance. Length of the straight waveguides 
                        separatedby the distance 'sep'.
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
                    length=length,
                    wg_width=wg_width)

                script.write(formatted_line)
    return


def dir_coupler_fdtd(save_path, gds_path, length, sep=sep,  
    wg_width=wg_width, bend_radius=bend_radius):
    '''
    This function generates a lumerical script file that will set up a FDTD
    simulation for the directional coupler generated with 'dir_coupler' when
    passed arguemnts 'length', 'sep', 'wg_width', and 'bend_radius'. The
    script file is saved to the passed directory 'save_path'.

    Args:
        save_path:      Path to which the generated script file is saved, 
                        including file name. If just a file name is passed, 
                        the file might get saved to the KLayout installation 
                        directory, though I'm not sure.
                        <str>

        gds_path:       Path to the GDS of the directional coupler to simulate.
                        <str>

        length:         Coupling distance. Length of the straight waveguides 
                        separatedby the distance 'sep'.
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
                    length=length,
                    wg_width=wg_width)

                script.write(formatted_line)
    return
