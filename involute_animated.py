#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Animated spur gear 2D outline with trochoidal root - Profile shifting animation.
Uses the generate_external_tooth_profile function from gear_profile.py
Animates profile_shift back and forth between min and max values.

Dependencies: numpy, matplotlib, Pillow (for GIF creation)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import os
from gear_profile import generate_external_tooth_profile

# =========================
# Editable parameters 
# =========================
z = 5                        # number of teeth
m = 2.0                      # module
alpha_deg = 20.0             # pressure angle (degrees)
undercut_auto_suppress = False # automatic undercut suppression

# =========================
# Animation parameters
# =========================
# Standard radii for calculating limits
rp = m*z/2.0                 # pitch radius  
rb = rp*np.cos(np.deg2rad(alpha_deg))  # base radius

profile_shift_min = rb-rp
profile_shift_max = 1

print(f"Profile shift range: {profile_shift_min:.3f} to {profile_shift_max:.3f}")
num_frames = 100
fps = 25

# Create array of profile_shift values that go back and forth using cosine wave
theta = np.linspace(0, 2*np.pi, num_frames)
profile_shifts = (profile_shift_max-profile_shift_min)*(np.cos(theta)+1)/2 + profile_shift_min


# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

def animate(frame):
    """Animation function - exactly copies the plotting from involute.py"""
    ax.clear()
    
    # Get current profile shift value
    current_profile_shift = profile_shifts[frame]
    
    # Use the gear_profile function instead of calculate_gear
    gear_data = generate_external_tooth_profile(
        z, m, alpha_deg, current_profile_shift, undercut_auto_suppress
    )
    
    # Extract parameters from the nested structure
    params = gear_data['parameters']
    rp = params['pitch_radius']
    rb = params['base_radius']
    ra = params['addendum_radius']
    rd = params['dedendum_radius']
    
    # Draw circles (same as involute.py)
    circle_pitch = plt.Circle((0, 0), rp, fill=False, color='blue', linewidth=2, label=f'Pitch circle (r={rp:.1f})')
    circle_base = plt.Circle((0, 0), rb, fill=False, color='green', linewidth=2, label=f'Base circle (r={rb:.1f})')
    circle_addendum = plt.Circle((0, 0), ra, fill=False, color='red', linewidth=2, label=f'Addendum circle (r={ra:.1f})')
    circle_dedendum = plt.Circle((0, 0), rd, fill=False, color='orange', linewidth=2, label=f'Dedendum circle (r={rd:.1f})')

    ax.add_patch(circle_pitch)
    ax.add_patch(circle_base)
    ax.add_patch(circle_addendum)
    ax.add_patch(circle_dedendum)

    # Convert profile data to numpy arrays for plotting
    trochoid_1_points = gear_data['trochoid_1']
    involute_1_points = gear_data['involute_1']
    upper_arc_points = gear_data['upper_arc']
    involute_2_points = gear_data['involute_2']
    trochoid_2_points = gear_data['trochoid_2']
    lower_arc_points = gear_data['lower_arc']
    
    # Convert to numpy arrays
    if trochoid_1_points:
        trochoid_1_array = np.array([[p[0], p[1]] for p in trochoid_1_points]).T
    else:
        trochoid_1_array = None
        
    if trochoid_2_points:
        trochoid_2_array = np.array([[p[0], p[1]] for p in trochoid_2_points]).T
    else:
        trochoid_2_array = None
        
    involute_1_array = np.array([[p[0], p[1]] for p in involute_1_points]).T
    involute_2_array = np.array([[p[0], p[1]] for p in involute_2_points]).T
    
    if upper_arc_points:
        upper_arc_array = np.array([[p[0], p[1]] for p in upper_arc_points]).T
    else:
        upper_arc_array = None
        
    if lower_arc_points:
        lower_arc_array = np.array([[p[0], p[1]] for p in lower_arc_points]).T
    else:
        lower_arc_array = None

    # Plot involute curves for all teeth (same as involute.py)
    for i in range(z):
        tooth_angle = i * 2 * np.pi / z
        cos_angle = np.cos(tooth_angle)
        sin_angle = np.sin(tooth_angle)
        tooth_rotation = np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle]
        ])
        
        # Rotate involute profiles
        x_inv_rot_1, y_inv_rot_1 = tooth_rotation @ involute_1_array
        x_inv_rot_2, y_inv_rot_2 = tooth_rotation @ involute_2_array
        
        label = 'Involute curve' if i == 0 else None
        ax.plot(x_inv_rot_1, y_inv_rot_1, 'k-', linewidth=3, label=label)
        ax.plot(x_inv_rot_2, y_inv_rot_2, 'k-', linewidth=3)

        # Plot trochoid curves if they exist
        if trochoid_1_array is not None:
            x_tro_rot_1, y_tro_rot_1 = tooth_rotation @ trochoid_1_array
            x_tro_rot_2, y_tro_rot_2 = tooth_rotation @ trochoid_2_array
            trochoid_label = 'Trochoid curve' if i == 0 else None
            ax.plot(x_tro_rot_1, y_tro_rot_1, 'k-', linewidth=3, label=trochoid_label)
            ax.plot(x_tro_rot_2, y_tro_rot_2, 'k-', linewidth=3)
            
        # Plot upper arc if it exists
        if upper_arc_array is not None:
            x_upper_rot, y_upper_rot = tooth_rotation @ upper_arc_array
            upper_arc_label = 'Upper arc' if i == 0 else None
            ax.plot(x_upper_rot, y_upper_rot, 'k-', linewidth=3, label=upper_arc_label)
            
        # Plot lower arc if it exists  
        if lower_arc_array is not None:
            x_lower_rot, y_lower_rot = tooth_rotation @ lower_arc_array
            lower_arc_label = 'Lower arc' if i == 0 else None
            ax.plot(x_lower_rot, y_lower_rot, 'k-', linewidth=3, label=lower_arc_label)

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
