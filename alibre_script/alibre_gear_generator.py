#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alibre CAD Gear Generator - IronPython 2.7 Compatible
Consolidated single-file version (no imports needed)

This script generates involute gear profiles directly in Alibre CAD.
All functions are embedded to avoid import issues.

Usage:
1. Open Alibre CAD
2. Run this script in the Python console
3. Call create_gear_in_alibre() with your parameters

Compatible with IronPython 2.7.10.0 Interactive Console
"""

"""
Spur gear profile generator - IronPython 2.7 compatible version
Generates one tooth profile consisting of:
- trochoid_1: First trochoid curve 
- involute_1: First involute curve
- upper_arc: Upper addendum arc
- involute_2: Second involute curve  
- trochoid_2: Second trochoid curve
- lower_arc: Lower dedendum arc

Dependencies: math (standard library only)
Compatible with: IronPython 2.7.10.0 (Alibre CAD)
"""

import math


def involute_function(angle):
    """Calculate involute function: tan(angle) - angle"""
    return math.tan(angle) - angle


def generate_external_tooth_profile(z, m, alpha_deg, profile_shift=0.0, undercut_auto_suppress=False, num_points=[10,10,5,5]):
    """
    Generate the profile of one tooth consisting of 6 parts.
    
    Parameters:
    -----------
    z : int
        Number of teeth
    m : float
        Module (mm)
    alpha_deg : float
        Pressure angle in degrees
    profile_shift : float
        Profile shifting value (default: 0.0)
    undercut_auto_suppress : bool
        Automatic undercut suppression (default: False)
    num_points : list of int
        Number of points per curve segment, order is following : [involute,trochoid,addendum,deddundum] (default: [20, 20, 20, 20])

    Returns:
    --------
    dict containing the 6 profile parts:
        'trochoid_1': [(x1, y1), (x2, y2), ...] - First trochoid curve
        'involute_1': [(x1, y1), (x2, y2), ...] - First involute curve  
        'upper_arc': [(x1, y1), (x2, y2), ...] - Upper addendum arc
        'involute_2': [(x1, y1), (x2, y2), ...] - Second involute curve
        'trochoid_2': [(x1, y1), (x2, y2), ...] - Second trochoid curve
        'lower_arc': [(x1, y1), (x2, y2), ...] - Lower dedendum arc
    """
    
    # Convert pressure angle to radians
    alpha = math.radians(alpha_deg)
    
    # Standard radii calculations
    pitch_radius = m * z / 2.0
    base_radius = pitch_radius * math.cos(alpha)
    
    # Undercut auto suppress
    if undercut_auto_suppress:
        if base_radius > pitch_radius - m:  # Check for undercut
            profile_shift = base_radius - (pitch_radius - m)
    
    # Apply profile shift
    pitch_radius += profile_shift
    addendum_radius = pitch_radius + m
    dedendum_radius = max(pitch_radius - 1.25 * m, 0.01)
    
    # Handle case where base radius is larger than pitch radius
    if base_radius / pitch_radius > 1.0:
        offset_angle = 0.0
    else:
        offset_angle = math.acos(base_radius / pitch_radius)
    
    # Involute angle at pitch circle
    phi = involute_function(offset_angle)
    
    # Angular dimensions
    angular_tooth_width = math.pi / z
    
    # Calculate involute parameters
    addendum_involute_angle = math.acos(base_radius / addendum_radius)
    max_involute_angle = addendum_involute_angle + involute_function(addendum_involute_angle)

    if base_radius < dedendum_radius:

        deddendum_involute_angle = math.acos(base_radius / dedendum_radius)

    else : 

        deddendum_involute_angle = 0

    min_involute_angle = deddendum_involute_angle + involute_function(deddendum_involute_angle)
    
    # Tooth positioning angle (EXACTLY as in original code)
    tooth_angle = -angular_tooth_width - 2 * phi
    
    # === Generate Involute Curves ===
    involute_1 = []
    involute_2 = []
    
    for i in range(num_points[0]):
        t = float(i) / (num_points[0] - 1)
        theta = t * (max_involute_angle - min_involute_angle) + min_involute_angle

        # Basic involute coordinates
        x_inv = base_radius * (math.cos(theta) + theta * math.sin(theta))
        y_inv = base_radius * (math.sin(theta) - theta * math.cos(theta))
        
        # First involute (rotated by tooth_angle)
        cos_tooth = math.cos(tooth_angle)
        sin_tooth = math.sin(tooth_angle)
        x1 = x_inv * cos_tooth - y_inv * sin_tooth
        y1 = x_inv * sin_tooth + y_inv * cos_tooth
        involute_2.append((x1, y1))
        
        # Second involute (mirrored in y, no rotation)
        involute_1.append((x_inv, -y_inv))
    
    # === Generate Trochoid Curves ===
    trochoid_1 = []
    trochoid_2 = []
    
    if base_radius > dedendum_radius:
        # Trochoid parameters (EXACTLY as in original code)
        t_trochoid = base_radius - dedendum_radius
        b_trochoid = math.sqrt(base_radius**4 / (base_radius - t_trochoid)**2 - base_radius**2)
        h_trochoid = b_trochoid * (1 - t_trochoid / base_radius)
        
        alpha_trochoid = math.atan(h_trochoid / base_radius)
        offset_trochoid_angle = alpha_trochoid + involute_function(alpha_trochoid)
        beta_trochoid = math.atan(b_trochoid / base_radius) - offset_trochoid_angle

        for i in range(num_points[1]):
            t = float(i) / (num_points[1] - 1)
            # EXACTLY as original: theta_trochoid = -np.linspace(-offset_trichoid_angle,0,involute_points)
            # which equals: theta_trochoid = np.linspace(0, offset_trichoid_angle, involute_points)
            theta_tro = t * offset_trochoid_angle
            
            # Basic trochoid coordinates
            x_tro = (base_radius * (math.cos(theta_tro) + theta_tro * math.sin(theta_tro)) - 
                    t_trochoid * math.cos(theta_tro))
            y_tro = (base_radius * (math.sin(theta_tro) - theta_tro * math.cos(theta_tro)) - 
                    t_trochoid * math.sin(theta_tro))
            
            # Apply trochoid beta rotation (EXACTLY as in original)
            cos_beta = math.cos(beta_trochoid)
            sin_beta = math.sin(beta_trochoid)
            x_tro_rot = x_tro * cos_beta - y_tro * sin_beta
            y_tro_rot = x_tro * sin_beta + y_tro * cos_beta
            
            # First trochoid (NO additional rotation, exactly as original)
            trochoid_1.append((x_tro_rot, y_tro_rot))
            
            # Second trochoid (mirrored in y, then rotated by tooth_angle)
            cos_tooth = math.cos(tooth_angle)
            sin_tooth = math.sin(tooth_angle)
            x2 = x_tro_rot * cos_tooth - (-y_tro_rot) * sin_tooth
            y2 = x_tro_rot * sin_tooth + (-y_tro_rot) * cos_tooth
            trochoid_2.append((x2, y2))
        
        # Reverse the trochoid arrays to match original order
        trochoid_1.reverse()
        trochoid_2.reverse()
    
    # === Generate Arc Segments ===
    
    # Upper arc (addendum) - EXACTLY as in original code
    upper_arc = []
    addendum_involute_angle_val = math.acos(base_radius / addendum_radius)
    involute_at_addendum = involute_function(addendum_involute_angle_val)
    start_angle_upper = -involute_at_addendum
    end_angle_upper = tooth_angle + involute_at_addendum
    
    for i in range(num_points[2]):
        t = float(i) / (num_points[2] - 1)
        theta_arc = start_angle_upper + t * (end_angle_upper - start_angle_upper)
        x_arc = addendum_radius * math.cos(theta_arc)
        y_arc = addendum_radius * math.sin(theta_arc)
        upper_arc.append((x_arc, y_arc))
    
    # Lower arc (dedendum) - EXACTLY as in original code
    lower_arc = []

    if base_radius > dedendum_radius:
        start_angle_lower = tooth_angle - beta_trochoid
        end_angle_lower = -angular_tooth_width * 2 + beta_trochoid
    else: 
        start_angle_lower = tooth_angle + involute_function(deddendum_involute_angle)
        end_angle_lower = -angular_tooth_width * 2 - involute_function(deddendum_involute_angle)
        
    for i in range(num_points[3]):
        t = float(i) / (num_points[3] - 1)
        theta_arc = start_angle_lower + t * (end_angle_lower - start_angle_lower)
        x_arc = dedendum_radius * math.cos(theta_arc)
        y_arc = dedendum_radius * math.sin(theta_arc)
        lower_arc.append((x_arc, y_arc))
    
    return {
        'trochoid_1': trochoid_1,
        'involute_1': involute_1,
        'upper_arc': upper_arc,
        'involute_2': involute_2,
        'trochoid_2': trochoid_2,
        'lower_arc': lower_arc,
        'parameters': {
            'z': z,
            'm': m,
            'alpha_deg': alpha_deg,
            'profile_shift': profile_shift,
            'pitch_radius': pitch_radius,
            'base_radius': base_radius,
            'addendum_radius': addendum_radius,
            'dedendum_radius': dedendum_radius
        }
    }

def generate_internal_tooth_profile(z, m, alpha_deg, thickness, profile_shift=0.0, undercut_auto_suppress=False, num_points=[10,5,5,10]):
    """
    Generate the profile of one tooth consisting of 6 parts.
    
    Parameters:
    -----------
    z : int
        Number of teeth
    m : float
        Module (mm)
    alpha_deg : float
        Pressure angle in degrees
    thickness : float
        External thickness (mm)
    profile_shift : float
        Profile shifting value (default: 0.0)
    undercut_auto_suppress : bool
        Automatic undercut suppression (default: False)
    num_points : list of int
        Number of points per curve segment, order is following : [involute,addendum,deddundum,external] (default: [20, 20, 20, 20])

    Returns:
    --------
    dict containing the 6 profile parts:
        'involute_1': [(x1, y1), (x2, y2), ...] - First involute curve  
        'upper_arc': [(x1, y1), (x2, y2), ...] - Upper addendum arc
        'involute_2': [(x1, y1), (x2, y2), ...] - Second involute curve
        'lower_arc': [(x1, y1), (x2, y2), ...] - Lower dedendum arc
        'external_arc': [(x1, y1), (x2, y2), ...] - External arc
    """
    
    # Convert pressure angle to radians
    alpha = math.radians(alpha_deg)
    
    # Standard radii calculations
    pitch_radius = m * z / 2.0
    base_radius = pitch_radius * math.cos(alpha)
    
    # Undercut auto suppress
    if undercut_auto_suppress:
        if base_radius > pitch_radius - m:  # Check for undercut
            profile_shift = base_radius - (pitch_radius - m)
    
    # Apply profile shift
    pitch_radius += profile_shift
    addendum_radius = pitch_radius - m
    dedendum_radius = max(pitch_radius + 1.25 * m, 0.01)
    
    # Handle case where base radius is larger than pitch radius
    if base_radius > pitch_radius :
        offset_angle = 0.0
    else:
        offset_angle = math.acos(base_radius / pitch_radius)
    
    # Involute angle at pitch circle
    phi = involute_function(offset_angle)
    
    # Angular dimensions
    angular_tooth_width = math.pi / z
    
    # Calculate involute parameters
    dedendum_involute_angle = math.acos(base_radius / dedendum_radius)

    if base_radius < addendum_radius:

        addendum_involute_angle = math.acos(base_radius / addendum_radius)

    else : 

        addendum_involute_angle = 0
        
    max_involute_angle = dedendum_involute_angle + involute_function(dedendum_involute_angle)
    min_involute_angle = addendum_involute_angle + involute_function(addendum_involute_angle)
    
    # Tooth positioning angle (EXACTLY as in original code)
    tooth_angle = -angular_tooth_width - 2 * phi
    
    # === Generate Involute Curves ===
    involute_1 = []
    involute_2 = []
    
    for i in range(num_points[0]):
        t = float(i) / (num_points[0] - 1)
        theta = t * (max_involute_angle - min_involute_angle) + min_involute_angle

        # Basic involute coordinates
        x_inv = base_radius * (math.cos(theta) + theta * math.sin(theta))
        y_inv = base_radius * (math.sin(theta) - theta * math.cos(theta))
        
        # First involute (rotated by tooth_angle)
        cos_tooth = math.cos(tooth_angle)
        sin_tooth = math.sin(tooth_angle)
        x1 = x_inv * cos_tooth - y_inv * sin_tooth
        y1 = x_inv * sin_tooth + y_inv * cos_tooth
        involute_2.append((x1, y1))
        
        # Second involute (mirrored in y, no rotation)
        involute_1.append((x_inv, -y_inv))
    
    # === Generate Arc Segments ===
    
    # Upper arc (addendum) - EXACTLY as in original code
    upper_arc = []

    involute_at_dedendum = involute_function(dedendum_involute_angle)
    start_angle_upper = -involute_at_dedendum
    end_angle_upper = tooth_angle + involute_at_dedendum
    
    for i in range(num_points[1]):
        t = float(i) / (num_points[1] - 1)
        theta_arc = start_angle_upper + t * (end_angle_upper - start_angle_upper)
        x_arc = dedendum_radius * math.cos(theta_arc)
        y_arc = dedendum_radius * math.sin(theta_arc)
        upper_arc.append((x_arc, y_arc))
    
    # Lower arc (dedendum) - EXACTLY as in original code
    # In order to avoid issue with to sharp corners, we need to double the lower arc in both side...
    lower_arc_1 = []
    lower_arc_2 = []

    start_angle_lower = tooth_angle + involute_function(addendum_involute_angle)
    end_angle_lower = -angular_tooth_width * 2 - involute_function(addendum_involute_angle)

    angular_width_lower = end_angle_lower - start_angle_lower
    
    half_num_points_lower = num_points[2]//2
    for i in range(half_num_points_lower):
        t = float(i) / (half_num_points_lower - 1)
        theta_arc = start_angle_lower + t * angular_width_lower/2
        x_arc = max(addendum_radius,base_radius) * math.cos(theta_arc)
        y_arc = max(addendum_radius,base_radius) * math.sin(theta_arc)
        lower_arc_1.append((x_arc, y_arc))


    for i in range(half_num_points_lower):
        t = float(i) / (half_num_points_lower - 1)
        theta_arc = -involute_function(addendum_involute_angle) - t * angular_width_lower/2
        x_arc = max(addendum_radius,base_radius) * math.cos(theta_arc)
        y_arc = max(addendum_radius,base_radius) * math.sin(theta_arc)
        lower_arc_2.append((x_arc, y_arc))

    # External arc
    external_arc = []

    start_angle_external = -involute_function(addendum_involute_angle)  - angular_width_lower/2
    end_angle_external = start_angle_lower + angular_width_lower/2

    # Divide by two and 

    for i in range(num_points[3]):
        t = i / (num_points[3] - 1)
        theta_arc = start_angle_external + t * (end_angle_external - start_angle_external)
        x_arc = (dedendum_radius+thickness) * math.cos(theta_arc)
        y_arc = (dedendum_radius+thickness) * math.sin(theta_arc)
        external_arc.append((x_arc, y_arc))

    return {
        'involute_1': involute_1,
        'upper_arc': upper_arc,
        'involute_2': involute_2,
        'lower_arc_1': lower_arc_1,
        'lower_arc_2': lower_arc_2,
        'external_arc': external_arc,
        'parameters': {
            'z': z,
            'm': m,
            'alpha_deg': alpha_deg,
            'profile_shift': profile_shift,
            'pitch_radius': pitch_radius,
            'base_radius': base_radius,
            'addendum_radius': addendum_radius,
            'dedendum_radius': dedendum_radius
        }
    }

def alibre_arc(sketch, arc, reverse = False):

    if reverse:
        start_pt = arc[0]
        end_pt = arc[-1]
    else:
        start_pt = arc[-1]
        end_pt = arc[0]
    
    # Calculate center and create arc using AddArcCenterStartEnd
    center_x, center_y = 0.0, 0.0  # Arc center is at origin for dedendum
    lower_arc = sketch.AddArcCenterStartEnd(center_x, center_y, start_pt[0], start_pt[1], end_pt[0], end_pt[1], False)
    print("  Created lower dedendum arc from (" + str(round(start_pt[0], 3)) + ", " + 
            str(round(start_pt[1], 3)) + ") to (" + str(round(end_pt[0], 3)) + ", " + 
            str(round(end_pt[1], 3)) + ")")
    
    return lower_arc

def alibre_spline(sketch, points):
    
    
    
    if len(points) > 0:

        spline_points = []

        for x, y in points:
            spline_points.append(x)
            spline_points.append(y)
        
        spline = sketch.AddBspline(spline_points, False)
    else: 
        spline = None

    return spline

def create_external_gear_in_alibre(z, m, alpha_deg, profile_shift=0.0,
                         undercut_auto_suppress=False,sketch=None):
    """
    Create a complete spur gear in Alibre CAD
    
    Parameters:
    -----------
    z : int - Number of teeth
    m : float - Module (mm)
    alpha_deg : float - Pressure angle (degrees)
    profile_shift : float - Profile shift coefficient
    undercut_auto_suppress : bool - Auto suppress undercut
    num_points : int - Points per curve (higher = smoother)
    
    Returns:
    --------
    Success status and created objects
    """
    
    try:
        # Alibre API functions are directly accessible (no import needed)
        
        # Generate the tooth profile using our function
        print("Generating gear profile: z=" + str(z) + ", m=" + str(m) + ", alpha=" + str(alpha_deg) + "°")

        tooth_profile = generate_external_tooth_profile(
                z=z, m=m, alpha_deg=alpha_deg, 
                profile_shift=profile_shift,
                undercut_auto_suppress=undercut_auto_suppress
        )
        
        params = tooth_profile['parameters']
        print("Generated profile with pitch radius: " + str(round(params['pitch_radius'], 2)) + "mm")
        
        # === Create the tooth profile geometry ===
        
        # 1. Line from center (0,0) to start of trochoid_1
        if len(tooth_profile['trochoid_1']) == 0:
            trochoid_start = tooth_profile['involute_1'][0]
        else:
            trochoid_start = tooth_profile['trochoid_1'][-1]
        center_to_trochoid = sketch.AddLine(0, 0, trochoid_start[0], trochoid_start[1], False)
        
        # 2. Trochoid_1 spline
        trochoid_1_spline = alibre_spline(sketch, tooth_profile['trochoid_1'])

        # 3. Involute_1 spline
        involute_1_spline = alibre_spline(sketch, tooth_profile['involute_1'])

        # 4. Upper addendum arc
        upper_arc = alibre_arc(sketch, tooth_profile['upper_arc'])
        
        # 5. Involute_2 spline
        involute_2_spline = alibre_spline(sketch, tooth_profile['involute_2'])
        
        # 6. Trochoid_2 spline
        trochoid_2_spline = alibre_spline(sketch, tooth_profile['trochoid_2'])

        # 7. Lower dedendum arc
        lower_arc = alibre_arc(sketch, tooth_profile['lower_arc'])
        
        # 8. Line from end of lower arc back to center
        arc_end = tooth_profile['lower_arc'][-1]
        arc_to_center = sketch.AddLine(arc_end[0], arc_end[1], 0, 0, False)
        print("  Created return line from dedendum arc to center: (" + 
                str(round(arc_end[0], 3)) + ", " + str(round(arc_end[1], 3)) + ") -> (0,0)")
        
        # Close the sketch
        print("Sketch completed successfully")
        
        
    except NameError as e:
        print("Error: Alibre API functions not available. This script must be run within Alibre CAD.")
        print("Make sure you have an active part open before running this script.")
        return False, None
    except Exception as e:
        print("Error creating gear: " + str(e))
        return False, None
    
def create_internal_gear_in_alibre(z, m, alpha_deg, profile_shift=0.0,
                            thickness=10.0,
                            undercut_auto_suppress=False,sketch=None):
    """
    Create a complete internal spur gear in Alibre CAD
    Parameters:
    - z : int - Number of teeth
    - m : float - Module (mm)
    - alpha_deg : float - Pressure angle (degrees)
    - profile_shift : float - Profile shift coefficient
    - thickness : float - External thickness (mm)
    - undercut_auto_suppress : bool - Auto suppress undercut
    - num_points : int - Points per curve (higher = smoother)
    """
    try:
        # Alibre API functions are directly accessible (no import needed)
        
        # Generate the tooth profile using our function
        print("Generating gear profile: z=" + str(z) + ", m=" + str(m) + ", alpha=" + str(alpha_deg) + "°")

        tooth_profile = generate_internal_tooth_profile(
                z=z, m=m, alpha_deg=alpha_deg, 
                thickness=thickness,
                profile_shift=profile_shift,
                undercut_auto_suppress=undercut_auto_suppress
        )
        
        params = tooth_profile['parameters']
        print("Generated profile with pitch radius: " + str(round(params['pitch_radius'], 2)) + "mm")

        # === Create the tooth profile geometry ===

        # 1. Line from involute 1 start to external arc start
        external_start = tooth_profile['external_arc'][-1]
        lower_arc_1_start = tooth_profile['lower_arc_1'][-1]
        involute_to_external = sketch.AddLine(lower_arc_1_start[0], lower_arc_1_start[1], external_start[0], external_start[1], False)

        # 2. External arc
        external_arc = alibre_arc(sketch, tooth_profile['external_arc'])

        # 3. Line from external arc end to lower arc end
        external_end = tooth_profile['external_arc'][0]
        lower_arc_2_end = tooth_profile['lower_arc_2'][-1]
        external_to_lower = sketch.AddLine(external_end[0], external_end[1], lower_arc_2_end[0], lower_arc_2_end[1], False)

        # 4. Lower dedendum arc
        lower_arc_1 = alibre_arc(sketch, tooth_profile['lower_arc_1'])
        lower_arc_2 = alibre_arc(sketch, tooth_profile['lower_arc_2'],reverse=True)

        # 5. Involute_2 spline
        involute_2_spline = alibre_spline(sketch, tooth_profile['involute_2'])

        # 6. Upper addendum arc
        upper_arc = alibre_arc(sketch, tooth_profile['upper_arc'])

        # 7. Involute_1 spline
        involute_1_spline = alibre_spline(sketch, tooth_profile['involute_1'])

        print("Sketch completed successfully")

    except NameError as e:
        print("Error: Alibre API functions not available. This script must be run within Alibre CAD.")
        print("Make sure you have an active part open before running this script.")
        return False, None
    except Exception as e:
        print("Error creating gear: " + str(e))
        return False, None
        

def create_gear_with_plane(z, m, alpha_deg, plane, profile_shift=0.0, thickness=10.0, internal=False,):

    part = CurrentPart()
    sketch = part.AddSketch("ToothProfile", plane)

    if internal:
        create_internal_gear_in_alibre(
            z=z, m=m, alpha_deg=alpha_deg,
            profile_shift=profile_shift,
            thickness=thickness,
            undercut_auto_suppress=False,
            sketch=sketch
        )
    else:
        create_external_gear_in_alibre(
            z=z, m=m, alpha_deg=alpha_deg,
            profile_shift=profile_shift,
            undercut_auto_suppress=False,
            sketch=sketch
        )


def create_gear_with_sketch(z, m, alpha_deg, sketch, profile_shift=0.0, thickness=10.0, internal=False,):

    # Use of AlibreX API to clear existing sketch figures 
    Figures = sketch.Figures

    sketch_object = sketch._Sketch

    sketch_object.BeginChange()

    for fig in Figures[:]:

        fig.FigureObject().Delete()

    if internal:
        create_internal_gear_in_alibre(
            z=z, m=m, alpha_deg=alpha_deg,
            profile_shift=profile_shift,
            thickness=thickness,
            undercut_auto_suppress=False,
            sketch=sketch
        )
    else:
        create_external_gear_in_alibre(
            z=z, m=m, alpha_deg=alpha_deg,
            profile_shift=profile_shift,
            undercut_auto_suppress=False,
            sketch=sketch
        )

    sketch_object.EndChange()

script_name = "Alibre gear generator enhanced"

Win = Windows()

NumberofTeeth = 20
Module = 2.0
PressureAngle = 20.0
Thickness = 10.0
ProfileShift = 0.0

Options = []
Options.append(['Number of Teeth', WindowsInputTypes.Integer, NumberofTeeth])
Options.append(['Module (mm)', WindowsInputTypes.Real, Module])
Options.append(['Pressure Angle', WindowsInputTypes.Real, PressureAngle])
Options.append(['Thickness (mm)', WindowsInputTypes.Real, Thickness])
Options.append(['Profile shift (mm)', WindowsInputTypes.Real, ProfileShift])
Options.append(['Optimal profile shift', WindowsInputTypes.Boolean, False])
Options.append(['Internal Gear', WindowsInputTypes.Boolean, False])
Options.append(['Label',WindowsInputTypes.Label,'Need to choose plane or sketch below'])
Options.append(['Application plane',WindowsInputTypes.Plane,None])
Options.append(['Application sketch',WindowsInputTypes.Sketch,None])

Values = Win.OptionsDialog(script_name, Options, 170)

NumberofTeeth, Module, PressureAngle, Thickness, ProfileShift, OptimalProfileShift, InternalGear,_,Plane,Sketch = Values

if Plane is not None : 

    create_gear_with_plane(
        NumberofTeeth, 
        Module, 
        PressureAngle, 
        Plane, 
        ProfileShift, 
        Thickness, 
        InternalGear,)
    
elif Sketch is not None : 

    create_gear_with_sketch(
        NumberofTeeth, 
        Module, 
        PressureAngle, 
        Sketch, 
        ProfileShift, 
        Thickness, 
        InternalGear,)

else: 
    print("You need to select a plane or a sketch to create the gear")
# Note: Don't auto-run gear creation when script is loaded
# Users should call the functions manually in Alibre CAD
