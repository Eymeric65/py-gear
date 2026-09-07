#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alibre CAD Timing Pulley Generator - IronPython 2.7 Compatible
Consolidated single-file version (no imports needed)

This script generates corrected timing-pulley profiles directly in Alibre CAD.
The main gear script (alibre_gear_generator.py) intentionally contains no belt
code anymore; all belt logic lives here.

Corrected timing-belt model:
- Belt pitch (neutral axis pitch): tooth-to-tooth period, imposes Rp = z*p/(2*pi)
- PLD (pitch line differential): belt thickness / 2
- Hole width: width of the rectangular belt cutout along the pitch line,
  equals the pulley tooth thickness at the pitch circle
- Over thickness: how much the involute grows past the upper PLD line
- Pressure angle: angle of the rectangular belt profile
- Addendum = Rp + PLD + over_thickness, Dedendum = Rp - PLD,
  Base = Rp*cos(alpha), same involute/trochoid construction as a normal gear.

Usage:
1. Open Alibre CAD
2. Run this script in the Python console
3. Fill the dialog (plane or sketch required)

Compatible with IronPython 2.7.10.0 Interactive Console
"""

import math
import time

def involute_function(angle):
    """Calculate involute function: tan(angle) - angle"""
    return math.tan(angle) - angle

def rotate_points(points, angle):
    """Rotate a list of (x, y) points by the given angle in radians"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rotated = []
    for x, y in points:
        x_rot = x * cos_a - y * sin_a
        y_rot = x * sin_a + y * cos_a
        rotated.append((x_rot, y_rot))
    return rotated

def generate_belt_tooth_profile(z, belt_pitch, pld, hole_width, over_thickness, alpha_deg, num_points=[10,10,5,5]):
    """
    Generate the profile of one timing-pulley tooth consisting of 6 parts.

    Parameters:
    -----------
    z : int - Number of teeth
    belt_pitch : float - Belt pitch = neutral axis pitch (mm)
    pld : float - Pitch line differential = belt thickness / 2 (mm)
    hole_width : float - Width of the belt cutout along the pitch line (mm)
    over_thickness : float - How much the involute grows past the upper PLD (mm)
    alpha_deg : float - Pressure angle of the belt / rectangular profile (degrees)
    num_points : list of int - Points per segment [involute,trochoid,addendum,dedendum]

    Returns:
    --------
    dict with 'trochoid_1', 'involute_1', 'upper_arc', 'involute_2',
    'trochoid_2', 'lower_arc' and 'parameters'
    """

    if z < 1:
        raise ValueError("Number of teeth must be at least 1.")
    if belt_pitch <= 0.0:
        raise ValueError("Belt pitch must be strictly positive.")
    if pld <= 0.0:
        raise ValueError("PLD must be strictly positive.")
    if hole_width <= 0.0:
        raise ValueError("Hole width must be strictly positive.")
    if over_thickness < 0.0:
        raise ValueError("Over thickness must be positive or zero.")
    if hole_width >= belt_pitch:
        raise ValueError("Hole width must be strictly smaller than belt pitch.")

    alpha = math.radians(alpha_deg)
    if not 0.0 < alpha < math.radians(45.0):
        raise ValueError("Pressure angle must be in (0, 45) degrees.")

    # Pitch radius imposed by the belt neutral axis
    pitch_radius = z * belt_pitch / (2.0 * math.pi)
    base_radius = pitch_radius * math.cos(alpha)
    addendum_radius = pitch_radius + pld + over_thickness
    dedendum_radius = pitch_radius - pld

    if dedendum_radius <= 0.0:
        raise ValueError("PLD is too large for this pitch radius, dedendum radius is <= 0.")
    if addendum_radius <= base_radius:
        raise ValueError("Addendum radius must be larger than base radius.")
    if base_radius > pitch_radius:
        raise ValueError("Base radius is larger than pitch radius, resulting in invalid gear geometry.")

    offset_angle = math.acos(base_radius / pitch_radius)

    # Involute angle at pitch circle
    phi = involute_function(offset_angle)

    # Pulley tooth thickness at pitch = hole width
    angular_tooth_width = hole_width / pitch_radius
    angular_pitch = belt_pitch / pitch_radius

    # Involute parameters (same as standard external gear)
    addendum_involute_angle = math.acos(base_radius / addendum_radius)
    max_involute_angle = addendum_involute_angle + involute_function(addendum_involute_angle)

    if base_radius < dedendum_radius:
        deddendum_involute_angle = math.acos(base_radius / dedendum_radius)
    else:
        deddendum_involute_angle = 0

    min_involute_angle = deddendum_involute_angle + involute_function(deddendum_involute_angle)

    # Pointed-tooth guard
    involute_at_addendum = involute_function(addendum_involute_angle)
    if angular_tooth_width - 2 * involute_at_addendum <= 0.0:
        raise ValueError("Tooth is pointed: hole width " + str(hole_width) +
                         "mm is too small for PLD + over thickness " +
                         str(round(pld + over_thickness, 3)) + "mm at this pressure angle.")

    # Tooth positioning angle (same convention as the spur gears)
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

    # === Generate Trochoid Curves (pitch -> dedendum, formed by the belt) ===
    trochoid_1 = []
    trochoid_2 = []

    if base_radius > dedendum_radius:
        # Same construction as the standard external gear
        t_trochoid = base_radius - dedendum_radius
        b_trochoid = math.sqrt(base_radius**4 / (base_radius - t_trochoid)**2 - base_radius**2)
        h_trochoid = b_trochoid * (1 - t_trochoid / base_radius)

        alpha_trochoid = math.atan(h_trochoid / base_radius)
        offset_trochoid_angle = alpha_trochoid + involute_function(alpha_trochoid)
        beta_trochoid = math.atan(b_trochoid / base_radius) - offset_trochoid_angle

        for i in range(num_points[1]):
            t = float(i) / (num_points[1] - 1)
            theta_tro = t * offset_trochoid_angle

            # Basic trochoid coordinates
            x_tro = (base_radius * (math.cos(theta_tro) + theta_tro * math.sin(theta_tro)) -
                    t_trochoid * math.cos(theta_tro))
            y_tro = (base_radius * (math.sin(theta_tro) - theta_tro * math.cos(theta_tro)) -
                    t_trochoid * math.sin(theta_tro))

            # Apply trochoid beta rotation
            cos_beta = math.cos(beta_trochoid)
            sin_beta = math.sin(beta_trochoid)
            x_tro_rot = x_tro * cos_beta - y_tro * sin_beta
            y_tro_rot = x_tro * sin_beta + y_tro * cos_beta

            # First trochoid (NO additional rotation)
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

    # Upper arc (tooth tip)
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

    # Lower arc (dedendum)
    lower_arc = []

    if base_radius > dedendum_radius:
        start_angle_lower = tooth_angle - beta_trochoid
        end_angle_lower = -angular_pitch + beta_trochoid
    else:
        start_angle_lower = tooth_angle + involute_function(deddendum_involute_angle)
        end_angle_lower = -angular_pitch - involute_function(deddendum_involute_angle)

    for i in range(num_points[3]):
        t = float(i) / (num_points[3] - 1)
        theta_arc = start_angle_lower + t * (end_angle_lower - start_angle_lower)
        x_arc = dedendum_radius * math.cos(theta_arc)
        y_arc = dedendum_radius * math.sin(theta_arc)
        lower_arc.append((x_arc, y_arc))

    # Rotate all profiles by half tooth angle to center tooth on x-axis
    rotation_angle = -tooth_angle/2
    trochoid_1 = rotate_points(trochoid_1, rotation_angle)
    involute_1 = rotate_points(involute_1, rotation_angle)
    upper_arc = rotate_points(upper_arc, rotation_angle)
    involute_2 = rotate_points(involute_2, rotation_angle)
    trochoid_2 = rotate_points(trochoid_2, rotation_angle)
    lower_arc = rotate_points(lower_arc, rotation_angle)

    return {
        'trochoid_1': trochoid_1,
        'involute_1': involute_1,
        'upper_arc': upper_arc,
        'involute_2': involute_2,
        'trochoid_2': trochoid_2,
        'lower_arc': lower_arc,
        'parameters': {
            'z': z,
            'belt_pitch': belt_pitch,
            'pld': pld,
            'hole_width': hole_width,
            'over_thickness': over_thickness,
            'alpha_deg': alpha_deg,
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

def create_timing_pulley_in_alibre(z, belt_pitch, pld, hole_width, over_thickness, alpha_deg, sketch=None):
    """
    Create a complete timing pulley in Alibre CAD

    Parameters:
    -----------
    z : int - Number of teeth
    belt_pitch : float - Belt pitch = neutral axis pitch (mm)
    pld : float - Pitch line differential = belt thickness / 2 (mm)
    hole_width : float - Width of the belt cutout along the pitch line (mm)
    over_thickness : float - How much the involute grows past the upper PLD (mm)
    alpha_deg : float - Pressure angle of the belt (degrees)
    sketch : Alibre sketch object
    """

    try:
        print("Generating timing pulley profile: z=" + str(z) + ", p=" + str(belt_pitch) +
              "mm, PLD=" + str(pld) + "mm, hole=" + str(hole_width) +
              "mm, over=" + str(over_thickness) + "mm, alpha=" + str(alpha_deg) + "deg")

        tooth_profile = generate_belt_tooth_profile(
                z=z, belt_pitch=belt_pitch, pld=pld,
                hole_width=hole_width, over_thickness=over_thickness,
                alpha_deg=alpha_deg
        )

        params = tooth_profile['parameters']
        print("Generated profile with pitch radius: " + str(round(params['pitch_radius'], 2)) + "mm")

        # === Create the tooth profile geometry ===

        # 1. Line from center (0,0) to start of trochoid_1 (or involute if no trochoid)
        if len(tooth_profile['trochoid_1']) == 0:
            trochoid_start = tooth_profile['involute_1'][0]
        else:
            trochoid_start = tooth_profile['trochoid_1'][-1]
        center_to_trochoid = sketch.AddLine(0, 0, trochoid_start[0], trochoid_start[1], False)

        # 2. Trochoid_1 spline
        trochoid_1_spline = alibre_spline(sketch, tooth_profile['trochoid_1'])

        # 3. Involute_1 spline
        involute_1_spline = alibre_spline(sketch, tooth_profile['involute_1'])

        # 4. Upper tip arc
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
        return tooth_profile['parameters']


    except NameError as e:
        print("Error: Alibre API functions not available. This script must be run within Alibre CAD.")
        print("Make sure you have an active part open before running this script.")
        return False, None
    except Exception as e:
        print("Error creating timing pulley: " + str(e))
        return False, None

def create_timing_pulley_with_plane(z, belt_pitch, pld, hole_width, over_thickness, alpha_deg, plane):

    name = "timing_pulley1"
    part = CurrentPart()
    sketch = part.AddSketch(name, plane)

    parameters=create_timing_pulley_in_alibre(
        z=z, belt_pitch=belt_pitch, pld=pld,
        hole_width=hole_width, over_thickness=over_thickness,
        alpha_deg=alpha_deg,
        sketch=sketch
    )

    p2=part.AddParameter(name+"_pitch_radius",ParameterTypes.Distance, float(parameters['pitch_radius']))
    time.sleep(1) # Wait a bit to ensure parameter is registered
    p1=part.AddParameter(name+"_z",ParameterTypes.Count, int(parameters['z']))
    time.sleep(1) # Wait a bit to ensure parameter is registered
    part.Regenerate()

def create_timing_pulley_with_sketch(z, belt_pitch, pld, hole_width, over_thickness, alpha_deg, sketch):

    # Use of AlibreX API to clear existing sketch figures
    Figures = sketch.Figures

    sketch_object = sketch._Sketch

    sketch_object.BeginChange()

    for fig in Figures[:]:

        fig.FigureObject().Delete()

    parameters=create_timing_pulley_in_alibre(
        z=z, belt_pitch=belt_pitch, pld=pld,
        hole_width=hole_width, over_thickness=over_thickness,
        alpha_deg=alpha_deg,
        sketch=sketch
    )

    sketch_object.EndChange()

    name = sketch.Name

    part = sketch.GetPart()

    p1=part.GetParameter(name+"_pitch_radius")
    p1.Value = float(parameters['pitch_radius'])

    time.sleep(0.1) # Wait a bit to ensure parameter is registered
    p2=part.GetParameter(name+"_z")
    p2.Value = int(parameters['z'])
    time.sleep(0.1) # Wait a bit to ensure parameter is registered
    part.Regenerate()


script_name = "Alibre timing pulley generator"

Win = Windows()

NumberofTeeth = 20
BeltPitch = 5.0
PLD = 0.5
HoleWidth = 2.5
OverThickness = 0.3
PressureAngle = 20.0

Options = []
Options.append(['Number of Teeth', WindowsInputTypes.Integer, NumberofTeeth])
Options.append(['Belt pitch / neutral axis pitch (mm)', WindowsInputTypes.Real, BeltPitch])
Options.append(['PLD / belt thickness / 2 (mm)', WindowsInputTypes.Real, PLD])
Options.append(['Hole width along pitch line (mm)', WindowsInputTypes.Real, HoleWidth])
Options.append(['Over thickness past upper PLD (mm)', WindowsInputTypes.Real, OverThickness])
Options.append(['Belt pressure angle (deg)', WindowsInputTypes.Real, PressureAngle])
Options.append(['Label',WindowsInputTypes.Label,'Need to choose plane or sketch below'])
Options.append(['Application plane',WindowsInputTypes.Plane,None])
Options.append(['Application sketch',WindowsInputTypes.Sketch,None])

Values = Win.OptionsDialog(script_name, Options, 170)

NumberofTeeth, BeltPitch, PLD, HoleWidth, OverThickness, PressureAngle,_,Plane,Sketch = Values

if Plane is not None :

    create_timing_pulley_with_plane(
        NumberofTeeth,
        BeltPitch,
        PLD,
        HoleWidth,
        OverThickness,
        PressureAngle,
        Plane,)

elif Sketch is not None :

    create_timing_pulley_with_sketch(
        NumberofTeeth,
        BeltPitch,
        PLD,
        HoleWidth,
        OverThickness,
        PressureAngle,
        Sketch,)

else:
    print("You need to select a plane or a sketch to create the gear")
# Note: Don't auto-run gear creation when script is loaded
# Users should call the functions manually in Alibre CAD
