#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Animated spur gear 2D outline with trochoidal root - Profile shifting animation.
Copies EXACTLY the behavior of involute.py but creates a GIF with profile_shift 
animating back and forth between min and max values.

Dependencies: numpy, matplotlib, Pillow (for GIF creation)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import os

def calculate_gear(profile_shift):
    """
    Function that wraps the exact behavior from involute.py
    Returns all the calculated values for a given profile_shift
    """
    # =========================
    # Editable parameters (same as involute.py)
    # =========================
    z       = 5                 # number of teeth
    m       = 2.0                # module
    alpha   = np.deg2rad(20.0)   # pressure angle (radians)

    # On first version unused 
    rho_f   = 0.38*m             # rack cutter tip radius (≈hob/shaper tip radius)
    backlash= 0.0                # preview only
    face_w  = 8.0                # for later 3D extrusion (unused here)

    undercut_auto_suppress = False # automatic undercut suppression( set the profile shifting value accordingly)

    # =========================
    # Calculated values (same as involute.py)
    # =========================

    # Standard radii
    rp = m*z/2.0                             # pitch radius
    rb = rp*np.cos(alpha)                    # base radius

    # -------------------------
    # Under cut auto suppress (same as involute.py)
    # -------------------------

    if undercut_auto_suppress:
        if rb > rp-m : # No undercut until the base radius (don't take in account the clearance of the dedendum)
            profile_shift = rb - (rp - m)

    rp += profile_shift                      # apply profile shift
    ra = rp + m                              # addendum radius
    rd = max(rp - 1.25*m, 0.01)              # dedendum/root radius (ISO-ish)

    # Handle case where rb/rp > 1 (very negative profile shifts)
    if rb/rp > 1.0:
        offset_angle = 0  # No offset when base circle is larger than pitch circle, clearly should happen
    else:
        offset_angle = np.arccos(rb/rp)

    def involute(alpha):
        return np.tan(alpha) - alpha

    phi = involute(offset_angle)# involute angle at pitch circle

    tooth_thickness = m * np.pi / 2
    angular_width = np.pi/z # tooth angular width

    involute_points = 400

    theta = np.linspace(0, 2*np.pi, involute_points)

    # Generate involute curve points (same as involute.py)
    x_involute = rb * (np.cos(theta) + theta * np.sin(theta))
    y_involute = rb * (np.sin(theta) - theta * np.cos(theta))

    # Trim involute by addendum and dedendum radius (same as involute.py)
    r_involute = np.sqrt(x_involute**2 + y_involute**2)
    valid_indices = (r_involute >= rd) & (r_involute <= ra)
    x_involute = x_involute[valid_indices]
    y_involute = y_involute[valid_indices]

    # Generate the trochoid curve (same as involute.py)
    x_trochoid = None
    y_trochoid = None

    if rb > rd: 
        t_trochoid = rb-rd # Big T on my attached calc sheet

        b_trochoid = np.sqrt(rb**4/(rb-t_trochoid)**2 - rb**2) # y on the calc sheet

        h_trochoid = b_trochoid*(1-t_trochoid/rb)# h on the calc sheet

        alpha_trichoid = np.arctan(h_trochoid/rb)  #starting angle

        offset_trichoid_angle = alpha_trichoid + involute(alpha_trichoid)
        beta_trichoid = np.arctan(b_trochoid/rb) - offset_trichoid_angle   #offset angle (rotation)

        theta_trochoid = -np.linspace(-offset_trichoid_angle,0,involute_points)

        x_trochoid = rb * (np.cos(theta_trochoid) + theta_trochoid * np.sin(theta_trochoid)) - t_trochoid * np.cos(theta_trochoid)
        y_trochoid = rb * (np.sin(theta_trochoid) - theta_trochoid * np.cos(theta_trochoid)) - t_trochoid * np.sin(theta_trochoid)

        rotation_matrix_trochoid = np.array([
            [np.cos(beta_trichoid), -np.sin(beta_trichoid)],
            [np.sin(beta_trichoid), np.cos(beta_trichoid)]
        ])
        x_trochoid, y_trochoid = rotation_matrix_trochoid @ np.vstack((x_trochoid, y_trochoid))

    # Rotation matrix for a quarter of the tooth width (same as involute.py)
    tooth_angle =  angular_width - 2*phi
    rotation_matrix = np.array([
        [np.cos(tooth_angle), -np.sin(tooth_angle)],
        [np.sin(tooth_angle), np.cos(tooth_angle)]
    ])

    # build one teeth (same as involute.py)
    x_involute_1, y_involute_1 = rotation_matrix @ np.vstack((x_involute, y_involute))
    x_involute_2, y_involute_2 = np.vstack((x_involute, -y_involute))

    x_trochoid_1 = None
    y_trochoid_1 = None
    x_trochoid_2 = None
    y_trochoid_2 = None

    if rb > rd: 
        x_trochoid_1, y_trochoid_1 = np.vstack((x_trochoid, y_trochoid))
        x_trochoid_2, y_trochoid_2 = rotation_matrix @ np.vstack((x_trochoid, -y_trochoid))

    return {
        'z': z, 'm': m, 'profile_shift': profile_shift,
        'rp': rp, 'rb': rb, 'ra': ra, 'rd': rd,
        'x_involute_1': x_involute_1, 'y_involute_1': y_involute_1,
        'x_involute_2': x_involute_2, 'y_involute_2': y_involute_2,
        'x_trochoid_1': x_trochoid_1, 'y_trochoid_1': y_trochoid_1,
        'x_trochoid_2': x_trochoid_2, 'y_trochoid_2': y_trochoid_2,
        'rb_gt_rd': rb > rd
    }

# Animation parameters
profile_shift_min = -1.0
profile_shift_max = 1.5
num_frames = 60
fps = 10

# Create array of profile_shift values that go back and forth
profile_shifts = np.concatenate([
    np.linspace(profile_shift_min, profile_shift_max, num_frames//2),
    np.linspace(profile_shift_max, profile_shift_min, num_frames//2)
])

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

def animate(frame):
    """Animation function - exactly copies the plotting from involute.py"""
    ax.clear()
    
    # Get current profile shift value
    current_profile_shift = profile_shifts[frame]
    
    # Calculate gear for current profile shift
    gear_data = calculate_gear(current_profile_shift)
    
    z = gear_data['z']
    m = gear_data['m']
    rp = gear_data['rp']
    rb = gear_data['rb']
    ra = gear_data['ra']
    rd = gear_data['rd']
    
    # Draw circles (same as involute.py)
    circle_pitch = plt.Circle((0, 0), rp, fill=False, color='blue', linewidth=2, label=f'Pitch circle (r={rp:.1f})')
    circle_base = plt.Circle((0, 0), rb, fill=False, color='green', linewidth=2, label=f'Base circle (r={rb:.1f})')
    circle_addendum = plt.Circle((0, 0), ra, fill=False, color='red', linewidth=2, label=f'Addendum circle (r={ra:.1f})')
    circle_dedendum = plt.Circle((0, 0), rd, fill=False, color='orange', linewidth=2, label=f'Dedendum circle (r={rd:.1f})')

    ax.add_patch(circle_pitch)
    ax.add_patch(circle_base)
    ax.add_patch(circle_addendum)
    ax.add_patch(circle_dedendum)

    # Plot involute curves for all teeth (same as involute.py)
    for i in range(z):
        tooth_angle = i * 2 * np.pi / z
        cos_angle = np.cos(tooth_angle)
        sin_angle = np.sin(tooth_angle)
        tooth_rotation = np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle]
        ])
        
        # Rotate first involute
        x_inv_rot_1, y_inv_rot_1 = tooth_rotation @ np.vstack((gear_data['x_involute_1'], gear_data['y_involute_1']))
        # Rotate second involute
        x_inv_rot_2, y_inv_rot_2 = tooth_rotation @ np.vstack((gear_data['x_involute_2'], gear_data['y_involute_2']))
        
        label = 'Involute curve' if i == 0 else None
        ax.plot(x_inv_rot_1, y_inv_rot_1, 'k-', linewidth=3, label=label)
        ax.plot(x_inv_rot_2, y_inv_rot_2, 'k-', linewidth=3)

        # Plot trochoid curves if they exist
        if gear_data['rb_gt_rd'] and gear_data['x_trochoid_1'] is not None:
            x_tro_rot_1, y_tro_rot_1 = tooth_rotation @ np.vstack((gear_data['x_trochoid_1'], gear_data['y_trochoid_1']))
            x_tro_rot_2, y_tro_rot_2 = tooth_rotation @ np.vstack((gear_data['x_trochoid_2'], gear_data['y_trochoid_2']))
            ax.plot(x_tro_rot_1, y_tro_rot_1, 'k-', linewidth=3)
            ax.plot(x_tro_rot_2, y_tro_rot_2, 'k-', linewidth=3)

    # Set equal aspect ratio and limits (same as involute.py)
    ax.set_aspect('equal')
    margin = m*z/2.0 + 3*m 
    ax.set_xlim(-margin, margin)
    ax.set_ylim(-margin, margin)

    # Add grid and labels (same as involute.py)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title(f'Gear Circles and Involute (z={z}, m={m}, profile_shifting={current_profile_shift:.2f})')
    ax.legend()

# Create animation
anim = FuncAnimation(fig, animate, frames=len(profile_shifts), interval=1000/fps, repeat=True)

# Save as GIF
print("Creating GIF animation...")
writer = PillowWriter(fps=fps)
anim.save('gear_profile_shift_animation.gif', writer=writer)
print("GIF saved as 'gear_profile_shift_animation.gif'")

# Optionally show the animation
plt.show()
