#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spur gear profile generator - Clean function implementation using only math library.
Generates one tooth profile consisting of:
- trochoid_1: First trochoid curve 
- involute_1: First involute curve
- upper_arc: Upper addendum arc
- involute_2: Second involute curve  
- trochoid_2: Second trochoid curve
- lower_arc: Lower dedendum arc

Dependencies: math (standard library only)
For visualization example: matplotlib
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
    # Lead to mathematically wrong gear... only occur when profile shift is very high negative...
    if base_radius > pitch_radius:
        raise ValueError("Base radius is larger than pitch radius, resulting in invalid gear geometry.")
    else:
        offset_angle = math.acos(base_radius / pitch_radius)
    
    # Involute angle at pitch circle
    phi = involute_function(offset_angle)
    
    # Angular dimensions
    angular_tooth_width = math.pi / z
    
    # Calculate involute parameters
    addendum_involute_angle = math.acos(base_radius / addendum_radius)
    max_involute_angle = addendum_involute_angle + involute_function(addendum_involute_angle)

    # Calculate dedendum involute angle only if base radius is smaller than dedendum radius otherwise set to 0 and add undercut.
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
    # Lead to mathematically wrong gear... only occur when profile shift is very high negative...
    if base_radius > pitch_radius:
        raise ValueError("Base radius is larger than pitch radius, resulting in invalid gear geometry.")
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


def generate_belt_tooth_profile(z, belt_hole, belt_full, tooth_height, num_points=[10,5,5]):
    """
    Generate the profile of one belt gear tooth consisting of 4 parts.

    A belt gear drives a perforated belt: the full part of the belt lies flat on the
    pulley surface while the teeth rise through the holes. The radius is therefore not
    a free parameter, it is imposed by the belt pitch:
    perimeter = (belt_hole + belt_full) * z.

    Parameters:
    -----------
    z : int
        Number of teeth
    belt_hole : float
        Width of the hole in the belt (mm), measured on the pulley surface
    belt_full : float
        Width of the full part of the belt (mm), measured on the pulley surface.
        This is the tooth footprint.
    tooth_height : float
        Height of the tooth above the pulley surface (mm)
    num_points : list of int
        Number of points per curve segment, order is following : [involute,addendum,deddundum] (default: [10, 5, 5])

    Returns:
    --------
    dict containing the 4 profile parts:
        'involute_1': [(x1, y1), (x2, y2), ...] - First involute curve (rising flank)
        'upper_arc': [(x1, y1), (x2, y2), ...] - Upper tip arc
        'involute_2': [(x1, y1), (x2, y2), ...] - Second involute curve (falling flank)
        'lower_arc': [(x1, y1), (x2, y2), ...] - Lower arc, the land the belt lies on
    """

    if z < 1:
        raise ValueError("Number of teeth must be at least 1.")
    if belt_hole <= 0.0 or belt_full <= 0.0:
        raise ValueError("Belt hole and belt full widths must be strictly positive.")
    if tooth_height <= 0.0:
        raise ValueError("Tooth height must be strictly positive.")

    # The belt imposes the radius: one perimeter is exactly z belt pitches
    belt_pitch = belt_hole + belt_full
    pitch_radius = z * belt_pitch / (2.0 * math.pi)

    # The pulley surface is both the land the belt lies on and the base circle
    # of the two involute flanks, so base = dedendum = pitch radius here.
    base_radius = pitch_radius
    dedendum_radius = pitch_radius
    addendum_radius = pitch_radius + tooth_height

    # Angular dimensions (the tooth footprint is the full part of the belt)
    angular_tooth_width = belt_full / pitch_radius
    angular_gap_width = belt_hole / pitch_radius

    # Involute parameter at the tip: theta = tan(alpha) with cos(alpha) = base/tip
    max_involute_angle = math.sqrt((addendum_radius / base_radius) ** 2 - 1.0)
    involute_at_addendum = max_involute_angle - math.atan(max_involute_angle)

    # Both flanks are involutes of the same circle, so the tooth narrows as it rises.
    # Above a certain height the two flanks cross and the tooth becomes pointed.
    if angular_tooth_width - 2 * involute_at_addendum <= 0.0:
        # Bisect theta - atan(theta) = angular_tooth_width/2 to report the usable height
        theta_low = 0.0
        theta_high = 1.0
        while theta_high - math.atan(theta_high) < angular_tooth_width / 2.0:
            theta_high = theta_high * 2.0
        for _ in range(80):
            theta_mid = 0.5 * (theta_low + theta_high)
            if theta_mid - math.atan(theta_mid) < angular_tooth_width / 2.0:
                theta_low = theta_mid
            else:
                theta_high = theta_mid
        max_tooth_height = base_radius * math.sqrt(1.0 + theta_high ** 2) - base_radius
        raise ValueError("Tooth height " + str(round(tooth_height, 3)) +
                         "mm makes the tooth pointed, maximum usable tooth height is " +
                         str(round(max_tooth_height, 3)) + "mm.")

    # Tooth positioning angle (negative = clockwise, same convention as the spur gears)
    tooth_angle = -angular_tooth_width

    # === Generate Involute Curves ===
    involute_1 = []
    involute_2 = []

    for i in range(num_points[0]):
        t = float(i) / (num_points[0] - 1)
        theta = t * max_involute_angle

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

    # Upper arc (tooth tip)
    upper_arc = []
    start_angle_upper = -involute_at_addendum
    end_angle_upper = tooth_angle + involute_at_addendum

    for i in range(num_points[1]):
        t = float(i) / (num_points[1] - 1)
        theta_arc = start_angle_upper + t * (end_angle_upper - start_angle_upper)
        x_arc = addendum_radius * math.cos(theta_arc)
        y_arc = addendum_radius * math.sin(theta_arc)
        upper_arc.append((x_arc, y_arc))

    # Lower arc (the land the full part of the belt lies on)
    lower_arc = []
    start_angle_lower = tooth_angle
    end_angle_lower = -(angular_tooth_width + angular_gap_width)

    for i in range(num_points[2]):
        t = float(i) / (num_points[2] - 1)
        theta_arc = start_angle_lower + t * (end_angle_lower - start_angle_lower)
        x_arc = dedendum_radius * math.cos(theta_arc)
        y_arc = dedendum_radius * math.sin(theta_arc)
        lower_arc.append((x_arc, y_arc))

    # Rotate all profiles by half tooth angle to center tooth on x-axis
    rotation_angle = -tooth_angle/2
    involute_1 = rotate_profile_part(involute_1, rotation_angle)
    upper_arc = rotate_profile_part(upper_arc, rotation_angle)
    involute_2 = rotate_profile_part(involute_2, rotation_angle)
    lower_arc = rotate_profile_part(lower_arc, rotation_angle)

    return {
        'involute_1': involute_1,
        'upper_arc': upper_arc,
        'involute_2': involute_2,
        'lower_arc': lower_arc,
        'parameters': {
            'z': z,
            'belt_hole': belt_hole,
            'belt_full': belt_full,
            'tooth_height': tooth_height,
            'belt_pitch': belt_pitch,
            'pitch_radius': pitch_radius,
            'base_radius': base_radius,
            'addendum_radius': addendum_radius,
            'dedendum_radius': dedendum_radius
        }
    }

def rotate_point(x, y, angle):
    """Rotate a point by given angle (radians)"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)


def rotate_profile_part(points, angle):
    """Rotate a list of points by given angle"""
    return [rotate_point(x, y, angle) for x, y in points]


if __name__ == "__main__":
    # Example usage - draw a complete gear
    import matplotlib.pyplot as plt
    
    # Gear parameters
    z = 5                    # number of teeth
    m = 2.0                  # module
    alpha_deg = 20.0         # pressure angle in degrees
    profile_shift = 0.0      # profile shifting
    undercut_auto_suppress = False

    thickness= 3.0 # thickness of internal gear

    num_points = [10, 10, 5, 5]  # Number of points per segment

    external= True

    # Belt gear parameters (used when belt is True, m/alpha_deg/profile_shift are ignored)
    belt = False
    belt_hole = 3.0          # width of the hole in the belt (mm)
    belt_full = 3.0          # width of the full part of the belt (mm)
    tooth_height = 2.0       # height of the tooth above the pulley surface (mm)
    belt_num_points = [10, 5, 5]

    # Generate one tooth profile
    if belt:
        tooth_profile = generate_belt_tooth_profile(z, belt_hole, belt_full, tooth_height, num_points=belt_num_points)
    elif external:
        tooth_profile = generate_external_tooth_profile(z, m, alpha_deg, profile_shift, undercut_auto_suppress,num_points=num_points)
    else:
        tooth_profile = generate_internal_tooth_profile(z, m, alpha_deg, thickness, profile_shift, undercut_auto_suppress,num_points=num_points)

    params = tooth_profile['parameters']

    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    
    # Draw reference circles
    circle_pitch = plt.Circle((0, 0), params['pitch_radius'], fill=False, color='blue', 
                             linewidth=2, label=f'Pitch circle (r={params["pitch_radius"]:.1f})')
    circle_base = plt.Circle((0, 0), params['base_radius'], fill=False, color='green', 
                            linewidth=2, label=f'Base circle (r={params["base_radius"]:.1f})')
    circle_addendum = plt.Circle((0, 0), params['addendum_radius'], fill=False, color='red', 
                                linewidth=2, label=f'Addendum circle (r={params["addendum_radius"]:.1f})')
    circle_dedendum = plt.Circle((0, 0), params['dedendum_radius'], fill=False, color='orange', 
                                linewidth=2, label=f'Dedendum circle (r={params["dedendum_radius"]:.1f})')
    
    ax.add_patch(circle_pitch)
    ax.add_patch(circle_base)
    ax.add_patch(circle_addendum)
    ax.add_patch(circle_dedendum)
    
    # Draw all teeth
    for i in range(z):
        tooth_angle = i * 2 * math.pi / z
        
        # Rotate and plot each part of the tooth profile
        if belt:
            parts = ['involute_1', 'upper_arc', 'involute_2', 'lower_arc']
            colors = ['black', 'black', 'black', 'black']
        elif external:
            parts = ['trochoid_1', 'involute_1', 'upper_arc', 'involute_2', 'trochoid_2', 'lower_arc']
            colors = ['black', 'black', 'black', 'black', 'black', 'black']  # Changed upper_arc to cyan and lower_arc to brown
        else:
            parts = [ 'involute_1', 'upper_arc', 'involute_2', 'lower_arc_1','lower_arc_2','external_arc']
            colors = ['black', 'black', 'black', 'black', 'black', 'black']  # Changed upper_arc to cyan and lower_arc to brown
        
        for j, part_name in enumerate(parts):
            part_points = tooth_profile[part_name]
            if part_points:  # Only plot if points exist
                rotated_points = rotate_profile_part(part_points, tooth_angle)
                x_coords = [p[0] for p in rotated_points]
                y_coords = [p[1] for p in rotated_points]
                
                label = part_name if i == 0 else None  # Only label first tooth
                ax.plot(x_coords, y_coords, color=colors[j], linewidth=2.5, label=label)
    
    # Set equal aspect ratio and limits
    ax.set_aspect('equal')
    if belt:
        margin = params['addendum_radius'] + tooth_height
    elif external:
        margin = params['addendum_radius'] + m
    else:
        margin = params['dedendum_radius'] + m + thickness
    ax.set_xlim(-margin, margin)
    ax.set_ylim(-margin, margin)
    
    # Add grid and labels
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    if belt:
        ax.set_title(f'Complete Belt Gear Profile (z={z}, hole={belt_hole}, full={belt_full}, h={tooth_height})')
    else:
        ax.set_title(f'Complete Gear Profile (z={z}, m={m}, α={alpha_deg}°, shift={profile_shift})')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.show()
    
    # Print some information
    print(f"Generated gear profile:")
    print(f"  Number of teeth: {z}")
    if belt:
        print(f"  Belt hole width: {belt_hole} mm")
        print(f"  Belt full width: {belt_full} mm")
        print(f"  Belt pitch: {params['belt_pitch']} mm")
        print(f"  Tooth height: {tooth_height} mm")
    else:
        print(f"  Module: {m} mm")
        print(f"  Pressure angle: {alpha_deg}°")
        print(f"  Profile shift: {profile_shift}")
    print(f"  Pitch radius: {params['pitch_radius']:.2f} mm")
    print(f"  Base radius: {params['base_radius']:.2f} mm")
    print(f"  Addendum radius: {params['addendum_radius']:.2f} mm")
    print(f"  Dedendum radius: {params['dedendum_radius']:.2f} mm")
