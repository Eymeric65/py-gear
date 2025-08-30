#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spur gear 2D outline with trochoidal root (rack cutter simulation).
- Builds involute flank
- Simulates rack cutter tip (radius rho_f) to get trochoid envelope
- Splices trochoid ↔ involute
- Patterns tooth around the gear
- Plots preview (and can export a tooth SVG)

Dependencies: numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt




# =========================
# Editable parameters
# =========================
z       = 5                 # number of teeth
m       = 2.0                # module
alpha   = np.deg2rad(20.0)   # pressure angle (radians)

# On first version unused 
rho_f   = 0.38*m             # rack cutter tip radius (≈hob/shaper tip radius)
profile_shift = 0            # profile shifting value
backlash= 0.0                # preview only
face_w  = 8.0                # for later 3D extrusion (unused here)

undercut_auto_suppress = False # automatic undercut suppression( set the profile shifting value accordingly)

# =========================
# Calculated values
# =========================

# Standard radii
rp = m*z/2.0                             # pitch radius
rb = rp*np.cos(alpha)                    # base radius

# -------------------------
# Under cut auto suppress
# -------------------------

if undercut_auto_suppress:
    
    if rb > rp-m : # No undercut until the base radius (don't take in account the clearance of the dedendum)

        profile_shift = rb - (rp - m)

rp += profile_shift                      # apply profile shift
ra = rp + m                              # addendum radius
rd = max(rp - 1.25*m, 0.01)              # dedendum/root radius (ISO-ish)

offset_angle = np.arccos(rb/rp)

def involute(alpha):
    return np.tan(alpha) - alpha

phi = involute(offset_angle)# involute angle at pitch circle

print(phi)

tooth_thickness = m * np.pi / 2
angular_width = np.pi/z # tooth angular width




involute_points = 400


theta = np.linspace(0, 2*np.pi, involute_points)

# Generate involute curve points
x_involute = rb * (np.cos(theta) + theta * np.sin(theta))
y_involute = rb * (np.sin(theta) - theta * np.cos(theta))

# Trim involute by addendum and dedendum radius
r_involute = np.sqrt(x_involute**2 + y_involute**2)
valid_indices = (r_involute >= rd) & (r_involute <= ra)
x_involute = x_involute[valid_indices]
y_involute = y_involute[valid_indices]

# Generate the trochoid curve (the undercut from base pitch to dedendum)

if rb > rd: 

    t_trochoid = rb-rd # Big T on my attached calc sheet

    b_trochoid = np.sqrt(rb**4/(rb-t_trochoid)**2 - rb**2) # y on the calc sheet

    h_trochoid = b_trochoid*(1-t_trochoid/rb)# h on the calc sheet

    alpha_trichoid = np.arctan(h_trochoid/rb)  #starting angle

    offset_trichoid_angle = alpha_trichoid + involute(alpha_trichoid)
    beta_trichoid = np.arctan(b_trochoid/rb) - offset_trichoid_angle   #offset angle (rotation)

    theta_trochoid = -np.linspace(-offset_trichoid_angle,0,involute_points)
    #theta_trochoid = np.linspace(-2*np.pi,2*np.pi,involute_points)

    x_trochoid = rb * (np.cos(theta_trochoid) + theta_trochoid * np.sin(theta_trochoid)) - t_trochoid * np.cos(theta_trochoid)
    y_trochoid = rb * (np.sin(theta_trochoid) - theta_trochoid * np.cos(theta_trochoid)) - t_trochoid * np.sin(theta_trochoid)

    rotation_matrix_trochoid = np.array([
        [np.cos(beta_trichoid), -np.sin(beta_trichoid)],
        [np.sin(beta_trichoid), np.cos(beta_trichoid)]
    ])
    x_trochoid, y_trochoid = rotation_matrix_trochoid @ np.vstack((x_trochoid, y_trochoid))

# Rotation matrix for a quarter of the tooth width
tooth_angle =  angular_width - 2*phi
rotation_matrix = np.array([
    [np.cos(tooth_angle), -np.sin(tooth_angle)],
    [np.sin(tooth_angle), np.cos(tooth_angle)]
])

# build one teeth 
x_involute_1, y_involute_1 = rotation_matrix @ np.vstack((x_involute, y_involute))
x_involute_2, y_involute_2 = np.vstack((x_involute, -y_involute))

if rb > rd: 

    x_trochoid_1, y_trochoid_1 = np.vstack((x_trochoid, y_trochoid))
    x_trochoid_2, y_trochoid_2 = rotation_matrix @ np.vstack((x_trochoid, -y_trochoid))

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(10, 10))


# Draw circles
circle_pitch = plt.Circle((0, 0), rp, fill=False, color='blue', linewidth=2, label=f'Pitch circle (r={rp:.1f})')
circle_base = plt.Circle((0, 0), rb, fill=False, color='green', linewidth=2, label=f'Base circle (r={rb:.1f})')
circle_addendum = plt.Circle((0, 0), ra, fill=False, color='red', linewidth=2, label=f'Addendum circle (r={ra:.1f})')
circle_dedendum = plt.Circle((0, 0), rd, fill=False, color='orange', linewidth=2, label=f'Dedendum circle (r={rd:.1f})')

ax.add_patch(circle_pitch)
ax.add_patch(circle_base)
ax.add_patch(circle_addendum)
ax.add_patch(circle_dedendum)

# Plot involute curve
# Plot involute curve for all teeth
# Plot involute curves for all teeth
for i in range(z):
    tooth_angle = i * 2 * np.pi / z
    cos_angle = np.cos(tooth_angle)
    sin_angle = np.sin(tooth_angle)
    tooth_rotation = np.array([
        [cos_angle, -sin_angle],
        [sin_angle, cos_angle]
    ])
    
    # Rotate first involute
    x_inv_rot_1, y_inv_rot_1 = tooth_rotation @ np.vstack((x_involute_1, y_involute_1))
    # Rotate second involute
    x_inv_rot_2, y_inv_rot_2 = tooth_rotation @ np.vstack((x_involute_2, y_involute_2))
    
    label = 'Involute curve' if i == 0 else None
    ax.plot(x_inv_rot_1, y_inv_rot_1, 'k-', linewidth=3, label=label)
    ax.plot(x_inv_rot_2, y_inv_rot_2, 'k-', linewidth=3)

    x_tro_rot_1, y_tro_rot_1 = tooth_rotation @ np.vstack((x_trochoid_1, y_trochoid_1))
    # Rotate second involute
    x_tro_rot_2, y_tro_rot_2 = tooth_rotation @ np.vstack((x_trochoid_2, y_trochoid_2))
    ax.plot(x_tro_rot_1, y_tro_rot_1, 'k-', linewidth=3)
    ax.plot(x_tro_rot_2, y_tro_rot_2, 'k-', linewidth=3)

# Set equal aspect ratio and limits
ax.set_aspect('equal')
margin = m*z/2.0 + 3*m 
ax.set_xlim(-margin, margin)
ax.set_ylim(-margin, margin)

# Add grid and labels
ax.grid(True, alpha=0.3)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title(f'Gear Circles and Involute (z={z}, m={m}, profile_shifting={profile_shift})')
ax.legend()

plt.show()


