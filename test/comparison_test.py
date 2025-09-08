#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparison script to verify gear_profile.py matches involute.py exactly
"""

import math
import matplotlib.pyplot as plt
import numpy as np
from gear_profile import generate_tooth_profile

# Run the original involute.py logic to compare
def original_involute_calculation():
    """Recreate the exact calculation from involute.py for comparison"""
    # Same parameters as involute.py
    z = 5
    m = 2.0
    alpha = np.deg2rad(20.0)
    profile_shift = 0
    undercut_auto_suppress = False
    
    # Standard radii
    rp = m*z/2.0
    rb = rp*np.cos(alpha)
    
    if undercut_auto_suppress:
        if rb > rp-m:
            profile_shift = rb - (rp - m)
    
    rp += profile_shift
    ra = rp + m
    rd = max(rp - 1.25*m, 0.01)
    
    offset_angle = np.arccos(rb/rp)
    
    def involute(alpha):
        return np.tan(alpha) - alpha
    
    phi = involute(offset_angle)
    angular_width = np.pi/z
    
    involute_points = 5  # Match original arc_points
    angle_at_dedendum = np.arccos(rb/ra) + involute(np.arccos(rb/ra))
    theta = np.linspace(0, angle_at_dedendum, involute_points)
    
    # Generate involute curve points
    x_involute = rb * (np.cos(theta) + theta * np.sin(theta))
    y_involute = rb * (np.sin(theta) - theta * np.cos(theta))
    
    # Generate trochoid
    if rb > rd:
        t_trochoid = rb-rd
        b_trochoid = np.sqrt(rb**4/(rb-t_trochoid)**2 - rb**2)
        h_trochoid = b_trochoid*(1-t_trochoid/rb)
        alpha_trichoid = np.arctan(h_trochoid/rb)
        offset_trichoid_angle = alpha_trichoid + involute(alpha_trichoid)
        beta_trichoid = np.arctan(b_trochoid/rb) - offset_trichoid_angle
        
        theta_trochoid = -np.linspace(-offset_trichoid_angle,0,involute_points)
        x_trochoid = rb * (np.cos(theta_trochoid) + theta_trochoid * np.sin(theta_trochoid)) - t_trochoid * np.cos(theta_trochoid)
        y_trochoid = rb * (np.sin(theta_trochoid) - theta_trochoid * np.cos(theta_trochoid)) - t_trochoid * np.sin(theta_trochoid)
        
        rotation_matrix_trochoid = np.array([
            [np.cos(beta_trichoid), -np.sin(beta_trichoid)],
            [np.sin(beta_trichoid), np.cos(beta_trichoid)]
        ])
        x_trochoid, y_trochoid = rotation_matrix_trochoid @ np.vstack((x_trochoid, y_trochoid))
    
    # Tooth rotation
    tooth_angle = -angular_width - 2*phi
    rotation_matrix = np.array([
        [np.cos(tooth_angle), -np.sin(tooth_angle)],
        [np.sin(tooth_angle), np.cos(tooth_angle)]
    ])
    
    # Build one tooth - EXACTLY as in original
    x_involute_1, y_involute_1 = rotation_matrix @ np.vstack((x_involute, y_involute))
    x_involute_2, y_involute_2 = np.vstack((x_involute, -y_involute))
    
    if rb > rd:
        x_trochoid_1, y_trochoid_1 = np.vstack((x_trochoid, y_trochoid))  # NO rotation
        x_trochoid_2, y_trochoid_2 = rotation_matrix @ np.vstack((x_trochoid, -y_trochoid))  # Rotated
    
    # Build arcs - EXACTLY as in original
    arc_points = 5
    
    upper_arc_theta = np.linspace(-involute(np.arccos(rb/ra)), tooth_angle + involute(np.arccos(rb/ra)), arc_points)
    x_upper_arc = ra * np.cos(upper_arc_theta)
    y_upper_arc = ra * np.sin(upper_arc_theta)
    
    down_arc_theta = np.linspace(tooth_angle - beta_trichoid, -angular_width*2 + beta_trichoid, arc_points)
    x_down_arc = rd * np.cos(down_arc_theta)
    y_down_arc = rd * np.sin(down_arc_theta)
    
    # Convert to same format as gear_profile function
    original_result = {
        'involute_1': list(zip(x_involute_1.flatten(), y_involute_1.flatten())),
        'involute_2': list(zip(x_involute_2.flatten(), y_involute_2.flatten())),
        'trochoid_1': list(zip(x_trochoid_1.flatten(), y_trochoid_1.flatten())),
        'trochoid_2': list(zip(x_trochoid_2.flatten(), y_trochoid_2.flatten())),
        'upper_arc': list(zip(x_upper_arc.flatten(), y_upper_arc.flatten())),
        'lower_arc': list(zip(x_down_arc.flatten(), y_down_arc.flatten())),
    }
    
    return original_result

# Test with same parameters
print("Comparing gear_profile.py with original involute.py...")

# Get result from gear_profile function
new_result = generate_tooth_profile(z=5, m=2.0, alpha_deg=20.0, profile_shift=0.0, 
                                   undercut_auto_suppress=False, num_points=5)  # Use same number as original

# Get result from original calculation
original_result = original_involute_calculation()

# Compare key points
print("\nComparing trochoid_1 (should be identical):")
print("Original first point:", original_result['trochoid_1'][0])
print("New first point:", new_result['trochoid_1'][0])
print("Original last point:", original_result['trochoid_1'][-1])
print("New last point:", new_result['trochoid_1'][-1])

print("\nComparing trochoid_2 (should be identical):")
print("Original first point:", original_result['trochoid_2'][0])
print("New first point:", new_result['trochoid_2'][0])
print("Original last point:", original_result['trochoid_2'][-1])
print("New last point:", new_result['trochoid_2'][-1])

print("\nComparing involute_1 (should be identical):")
print("Original first point:", original_result['involute_1'][0])
print("New first point:", new_result['involute_1'][0])
print("Original last point:", original_result['involute_1'][-1])
print("New last point:", new_result['involute_1'][-1])

print("\nComparing involute_2 (should be identical):")
print("Original first point:", original_result['involute_2'][0])
print("New first point:", new_result['involute_2'][0])
print("Original last point:", original_result['involute_2'][-1])
print("New last point:", new_result['involute_2'][-1])

print("\nComparing upper_arc (should be identical):")
print("Original first point:", original_result['upper_arc'][0])
print("New first point:", new_result['upper_arc'][0])
print("Original last point:", original_result['upper_arc'][-1])
print("New last point:", new_result['upper_arc'][-1])

print("\nComparing lower_arc (should be identical):")
print("Original first point:", original_result['lower_arc'][0])
print("New first point:", new_result['lower_arc'][0])
print("Original last point:", original_result['lower_arc'][-1])
print("New last point:", new_result['lower_arc'][-1])

# Visual comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Plot original
ax1.plot([p[0] for p in original_result['trochoid_1']], [p[1] for p in original_result['trochoid_1']], 'r-', linewidth=3, label='trochoid_1')
ax1.plot([p[0] for p in original_result['involute_1']], [p[1] for p in original_result['involute_1']], 'b-', linewidth=3, label='involute_1')
ax1.plot([p[0] for p in original_result['upper_arc']], [p[1] for p in original_result['upper_arc']], 'c-', linewidth=3, label='upper_arc')
ax1.plot([p[0] for p in original_result['involute_2']], [p[1] for p in original_result['involute_2']], 'g-', linewidth=3, label='involute_2')
ax1.plot([p[0] for p in original_result['trochoid_2']], [p[1] for p in original_result['trochoid_2']], 'm-', linewidth=3, label='trochoid_2')
ax1.plot([p[0] for p in original_result['lower_arc']], [p[1] for p in original_result['lower_arc']], 'orange', linewidth=3, label='lower_arc')
ax1.set_title('Original involute.py')
ax1.legend()
ax1.set_aspect('equal')
ax1.grid(True)

# Plot new function
ax2.plot([p[0] for p in new_result['trochoid_1']], [p[1] for p in new_result['trochoid_1']], 'r-', linewidth=3, label='trochoid_1')
ax2.plot([p[0] for p in new_result['involute_1']], [p[1] for p in new_result['involute_1']], 'b-', linewidth=3, label='involute_1')
ax2.plot([p[0] for p in new_result['upper_arc']], [p[1] for p in new_result['upper_arc']], 'c-', linewidth=3, label='upper_arc')
ax2.plot([p[0] for p in new_result['involute_2']], [p[1] for p in new_result['involute_2']], 'g-', linewidth=3, label='involute_2')
ax2.plot([p[0] for p in new_result['trochoid_2']], [p[1] for p in new_result['trochoid_2']], 'm-', linewidth=3, label='trochoid_2')
ax2.plot([p[0] for p in new_result['lower_arc']], [p[1] for p in new_result['lower_arc']], 'orange', linewidth=3, label='lower_arc')
ax2.set_title('New gear_profile.py')
ax2.legend()
ax2.set_aspect('equal')
ax2.grid(True)

plt.tight_layout()
plt.show()
