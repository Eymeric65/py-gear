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


def generate_tooth_profile(z, m, alpha_deg, profile_shift=0.0, undercut_auto_suppress=False, num_points=20):
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
    num_points : int
        Number of points per curve segment (default: 20)
    
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
    
    # Tooth positioning angle (EXACTLY as in original code)
    tooth_angle = -angular_tooth_width - 2 * phi
    
    # === Generate Involute Curves ===
    involute_1 = []
    involute_2 = []
    
    for i in range(num_points):
        t = float(i) / float(num_points - 1)  # Python 2.7 integer division fix
        theta = t * max_involute_angle
        
        # Basic involute coordinates
        x_inv = base_radius * (math.cos(theta) + theta * math.sin(theta))
        y_inv = base_radius * (math.sin(theta) - theta * math.cos(theta))
        
        # First involute (rotated by tooth_angle)
        cos_tooth = math.cos(tooth_angle)
        sin_tooth = math.sin(tooth_angle)
        x1 = x_inv * cos_tooth - y_inv * sin_tooth
        y1 = x_inv * sin_tooth + y_inv * cos_tooth
        involute_1.append((x1, y1))
        
        # Second involute (mirrored in y, no rotation)
        involute_2.append((x_inv, -y_inv))
    
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
        
        for i in range(num_points):
            t = float(i) / float(num_points - 1)  # Python 2.7 integer division fix
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
    
    for i in range(num_points):
        t = float(i) / float(num_points - 1)  # Python 2.7 integer division fix
        theta_arc = start_angle_upper + t * (end_angle_upper - start_angle_upper)
        x_arc = addendum_radius * math.cos(theta_arc)
        y_arc = addendum_radius * math.sin(theta_arc)
        upper_arc.append((x_arc, y_arc))
    
    # Lower arc (dedendum) - EXACTLY as in original code
    lower_arc = []
    if base_radius > dedendum_radius:
        start_angle_lower = tooth_angle - beta_trochoid
        end_angle_lower = -angular_tooth_width * 2 + beta_trochoid
        
        for i in range(num_points):
            t = float(i) / float(num_points - 1)  # Python 2.7 integer division fix
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

def create_gear_in_alibre(z, m, alpha_deg, profile_shift=0.0, thickness=10.0, 
                         undercut_auto_suppress=False, num_points=50):
    """
    Create a complete spur gear in Alibre CAD
    
    Parameters:
    -----------
    z : int - Number of teeth
    m : float - Module (mm)
    alpha_deg : float - Pressure angle (degrees)
    profile_shift : float - Profile shift coefficient
    thickness : float - Gear thickness (mm)
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
        tooth_profile = generate_tooth_profile(
            z=z, m=m, alpha_deg=alpha_deg, 
            profile_shift=profile_shift,
            undercut_auto_suppress=undercut_auto_suppress,
            num_points=num_points
        )
        
        params = tooth_profile['parameters']
        print("Generated profile with pitch radius: " + str(round(params['pitch_radius'], 2)) + "mm")
        
        # Get the current part (like in Alibre's gear generator)
        part = CurrentPart()
        if part is None:
            print("Error: No active part found. Please create or open a part first.")
            return False, None
            
        # Get the XY plane to create the gear on
        gear_plane = part.XYPlane
        
        # Create a new sketch on the XY plane
        sketch = part.AddSketch("ToothProfile", gear_plane)
        
        print("Creating tooth profile sketch...")
        
        # === Create the tooth profile geometry ===
        
        # 1. Line from center (0,0) to start of trochoid_1
        if tooth_profile['trochoid_1']:
            trochoid_start = tooth_profile['trochoid_1'][-1]
            center_to_trochoid = sketch.AddLine(0, 0, trochoid_start[0], trochoid_start[1], False)
            print("  Created center line to trochoid_1: (0,0) -> (" + 
                  str(round(trochoid_start[0], 3)) + ", " + str(round(trochoid_start[1], 3)) + ")")
        
        # 2. Trochoid_1 spline
        if tooth_profile['trochoid_1'] and len(tooth_profile['trochoid_1']) > 1:
            trochoid_1_points = []
            for x, y in tooth_profile['trochoid_1']:
                trochoid_1_points.append(x)
                trochoid_1_points.append(y)
            
            trochoid_1_spline = sketch.AddBspline(trochoid_1_points, False)
            print("  Created trochoid_1 spline with " + str(len(trochoid_1_points)) + " points")
        
        # 3. Involute_1 spline  
        if tooth_profile['involute_1'] and len(tooth_profile['involute_1']) > 1:
            involute_1_points = []
            for x, y in tooth_profile['involute_1']:
                involute_1_points.append(x)
                involute_1_points.append(y)
            
            involute_1_spline = sketch.AddBspline(involute_1_points, False)
            print("  Created involute_1 spline with " + str(len(involute_1_points)) + " points")
        
        # 4. Upper addendum arc
        if tooth_profile['upper_arc'] and len(tooth_profile['upper_arc']) >= 3:
            # For arc creation using center, start, and end points
            start_pt = tooth_profile['upper_arc'][-1]
            end_pt = tooth_profile['upper_arc'][0]
            
            # Calculate center and create arc using AddArcCenterStartEnd
            center_x, center_y = 0.0, 0.0  # Arc center is at origin for addendum
            upper_arc = sketch.AddArcCenterStartEnd(center_x, center_y, start_pt[0], start_pt[1], end_pt[0], end_pt[1], False)
            print("  Created upper addendum arc from (" + str(round(start_pt[0], 3)) + ", " + 
                  str(round(start_pt[1], 3)) + ") to (" + str(round(end_pt[0], 3)) + ", " + 
                  str(round(end_pt[1], 3)) + ")")
        
        # 5. Involute_2 spline
        if tooth_profile['involute_2'] and len(tooth_profile['involute_2']) > 1:
            involute_2_points = []
            for x, y in tooth_profile['involute_2']:
                involute_2_points.append(x)
                involute_2_points.append(y)
            
            involute_2_spline = sketch.AddBspline(involute_2_points, False)
            print("  Created involute_2 spline with " + str(len(involute_2_points)) + " points")
        
        # 6. Trochoid_2 spline
        if tooth_profile['trochoid_2'] and len(tooth_profile['trochoid_2']) > 1:
            trochoid_2_points = []
            for x, y in tooth_profile['trochoid_2']:
                trochoid_2_points.append(x)
                trochoid_2_points.append(y)
            
            trochoid_2_spline = sketch.AddBspline(trochoid_2_points, False)
            print("  Created trochoid_2 spline with " + str(len(trochoid_2_points)) + " points")
        
        # 7. Lower dedendum arc
        if tooth_profile['lower_arc'] and len(tooth_profile['lower_arc']) >= 3:
            start_pt = tooth_profile['lower_arc'][-1]
            end_pt = tooth_profile['lower_arc'][0]
            
            # Calculate center and create arc using AddArcCenterStartEnd
            center_x, center_y = 0.0, 0.0  # Arc center is at origin for dedendum
            lower_arc = sketch.AddArcCenterStartEnd(center_x, center_y, start_pt[0], start_pt[1], end_pt[0], end_pt[1], False)
            print("  Created lower dedendum arc from (" + str(round(start_pt[0], 3)) + ", " + 
                  str(round(start_pt[1], 3)) + ") to (" + str(round(end_pt[0], 3)) + ", " + 
                  str(round(end_pt[1], 3)) + ")")
        
        # 8. Line from end of lower arc back to center
        if tooth_profile['lower_arc']:
            arc_end = tooth_profile['lower_arc'][-1]
            arc_to_center = sketch.AddLine(arc_end[0], arc_end[1], 0, 0, False)
            print("  Created return line from dedendum arc to center: (" + 
                  str(round(arc_end[0], 3)) + ", " + str(round(arc_end[1], 3)) + ") -> (0,0)")
        
        # Close the sketch
        print("Sketch completed successfully")
        
        # === Create 3D Feature ===
        
        # Extrude the sketch using AddExtrudeBoss (like in Alibre's gear generator)
        print("Extruding sketch by " + str(thickness) + "mm...")
        extrusion = part.AddExtrudeBoss("Gear", sketch, thickness, False)
        
        if extrusion is None:
            print("Error: Failed to create extrusion")
            return False, None
        
        print("Extrusion created successfully")
        
        # === Create Circular Pattern ===
        
        # Create circular pattern for all teeth (if more than 1)
        if z > 1:
            print("Creating circular pattern for " + str(z) + " teeth...")
            
            # Create circular pattern using Alibre's API
            # AddCircularPattern(name, feature, axis, count, angle)
            pattern_angle = 360.0  # Full circle
            pattern = part.AddCircularPattern(
                "GearTeeth",         # Pattern name
                extrusion,           # Feature to pattern
                part.ZAxis,          # Axis of rotation (Z-axis)
                z,                   # Number of instances (teeth)
                pattern_angle        # Total angle
            )
            
            if pattern is None:
                print("Warning: Failed to create circular pattern")
                return True, extrusion  # Still return success for single tooth
            else:
                print("Circular pattern created successfully with " + str(z) + " teeth")
                return True, pattern
        
        return True, extrusion
        
    except NameError as e:
        print("Error: Alibre API functions not available. This script must be run within Alibre CAD.")
        print("Make sure you have an active part open before running this script.")
        return False, None
    except Exception as e:
        print("Error creating gear: " + str(e))
        return False, None


def create_standard_gear():
    """Create a standard 20-tooth gear for testing"""
    return create_gear_in_alibre(
        z=20,                    # 20 teeth
        m=2.0,                   # 2mm module
        alpha_deg=20.0,          # 20° pressure angle
        profile_shift=0.0,       # No profile shift
        thickness=10.0,          # 10mm thick
        undercut_auto_suppress=False,
        num_points=10            # Smooth curves
    )


def create_small_gear_with_undercut_suppression():
    """Create a small gear with automatic undercut suppression"""
    return create_gear_in_alibre(
        z=8,                     # 8 teeth (prone to undercut)
        m=2.5,                   # 2.5mm module
        alpha_deg=20.0,          # 20° pressure angle
        profile_shift=0.0,       # Will be auto-calculated
        thickness=12.0,          # 12mm thick
        undercut_auto_suppress=True,  # Auto suppress undercut
        num_points=40            # Very smooth curves
    )


def create_metric_gear(z, m, thickness=None):
    """Create a standard metric gear with common parameters"""
    if thickness is None:
        thickness = max(5.0, m * 3)  # Default thickness = 3 * module
    
    return create_gear_in_alibre(
        z=z,
        m=m,
        alpha_deg=20.0,          # Standard pressure angle
        thickness=thickness,
        undercut_auto_suppress=True  # Always prevent undercut
    )


def create_fine_pitch_gear(z, m, thickness=None):
    """Create a fine-pitch gear with higher resolution"""
    if thickness is None:
        thickness = max(2.0, m * 2)
    
    return create_gear_in_alibre(
        z=z,
        m=m,
        alpha_deg=20.0,
        thickness=thickness,
        num_points=60            # Very high resolution for small gears
    )



print("Alibre CAD Gear Generator - IronPython 2.7 Compatible")
print("=" * 50)

print("Alibre CAD Gear Generator - IronPython 2.7 Compatible")
print("=" * 50)
print("")
print("This script is ready to run in Alibre CAD!")
print("")
print("Usage Instructions:")
print("1. Open Alibre CAD")
print("2. Create or open a part")
print("3. Copy and paste this entire script into the Python console")
print("4. Call one of the gear creation functions:")
print("")
print("Examples:")
print("# Create a standard 20-tooth gear:")
print("create_standard_gear()")
print("")
print("# Create a custom gear:")
print("create_gear_in_alibre(z=15, m=2.5, alpha_deg=25.0, thickness=12.0)")
print("")
print("# Create a small gear with undercut suppression:")
print("create_small_gear_with_undercut_suppression()")
print("")
print("Available functions:")
print("- create_standard_gear()")
print("- create_small_gear_with_undercut_suppression()")  
print("- create_metric_gear(z, m, thickness=None)")
print("- create_fine_pitch_gear(z, m, thickness=None)")
print("- create_gear_in_alibre(z, m, alpha_deg, profile_shift, thickness, undercut_auto_suppress, num_points)")

create_standard_gear()
# Note: Don't auto-run gear creation when script is loaded
# Users should call the functions manually in Alibre CAD
