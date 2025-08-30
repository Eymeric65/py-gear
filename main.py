#!/usr/bin/env python3
# Spur gear 2D outline with trochoidal root (robust).
# deps: numpy, matplotlib

import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Params (edit these)
# ----------------------------
z       = 6                # tooth count
m       = 2.0               # module
alpha   = np.deg2rad(20.0)  # pressure angle
rho_f   = 0.40*m            # rack/shaper tip radius
# radii (ISO-ish)
rp = m*z/2.0
rb = rp*np.cos(alpha)
ra = rp + m
rd = max(rp - 1.25*m, 1e-3)

# ----------------------------
# Helpers
# ----------------------------
def rot2d(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c,-s],[s,c]])

def involute_xy(rb, t):
    ct, st = np.cos(t), np.sin(t)
    return rb*(ct + t*st), rb*(st - t*ct)

def involute_t_for_radius(rb, R):
    T = np.linspace(0, 2.8, 7000)
    x, y = involute_xy(rb, T)
    r = np.hypot(x, y)
    return np.interp(R, r, T) if np.any(r >= R) else T[-1]

def arc_between_on_radius(R, p1, p2, steps=160):
    th1, th2 = np.arctan2(p1[1], p1[0]), np.arctan2(p2[1], p2[0])
    while th2 <= th1: th2 += 2*np.pi
    th = np.linspace(th1, th2, steps)
    return R*np.cos(th), R*np.sin(th)

def rotate_poly(x, y, theta):
    XY = rot2d(theta) @ np.vstack([x, y])
    return XY[0], XY[1]

def nearest_join(x1, y1, x2, y2):
    if len(x1)==0 or len(x2)==0:
        raise ValueError("nearest_join: empty curve")
    i_best=j_best=0; d2_best=1e99
    step=max(1,len(x1)//1000)
    for i in range(0,len(x1),step):
        dx=x2-x1[i]; dy=y2-y1[i]
        j = np.argmin(dx*dx + dy*dy)
        d2 = (x2[j]-x1[i])**2 + (y2[j]-y1[i])**2
        if d2<d2_best: d2_best,i_best,j_best=d2,i,j
    return i_best,j_best,np.sqrt(d2_best)

# ----------------------------
# 1) Involute flank (one side)
# ----------------------------
t_add = involute_t_for_radius(rb, ra)
tv = np.linspace(0, max(1e-6,t_add), 3000)
xi, yi = involute_xy(rb, tv)
ri = np.hypot(xi, yi)
mask_invo = (ri >= rd*0.85) & (ri <= ra*1.01)
xi, yi = xi[mask_invo], yi[mask_invo]

# ----------------------------
# 2) Trochoidal root: sweep cutter tip circle, keep lower envelope
# Robust binning by polar angle, with auto-relax + fallback.
# ----------------------------
tooth_angle = 2*np.pi/z
half_tooth  = tooth_angle/2
def build_trochoid(theta_span_mult=1.6, sector_factor=0.95, phis=361, thetas=1400):
    TH = np.linspace(-theta_span_mult*tooth_angle/2,
                      theta_span_mult*tooth_angle/2, thetas)
    PH = np.linspace(0, 2*np.pi, phis)

    Xc=[]; Yc=[]
    for th in TH:
        dx = rp*th
        C_r = np.array([dx, -(m + rho_f)])      # center under pitch by m+rho
        C_g = rot2d(-th) @ C_r                  # into gear coords
        xC = C_g[0] + rho_f*np.cos(PH)
        yC = C_g[1] + rho_f*np.sin(PH)
        Xc.append(xC); Yc.append(yC)

    Xc = np.concatenate(Xc); Yc = np.concatenate(Yc)
    rC = np.hypot(Xc, Yc)

    # radius window: near root up to a bit over base
    mask_r = (rC >= 0.15*rd) & (rC <= 1.25*rb)
    Xc, Yc, rC = Xc[mask_r], Yc[mask_r], rC[mask_r]
    if Xc.size==0: return np.array([]), np.array([])

    ang = np.arctan2(Yc, Xc)
    # gate around tooth space centered at 0 (after later centering by half-tooth)
    sector = np.abs(ang) < (sector_factor*half_tooth)
    Xc, Yc, rC, ang = Xc[sector], Yc[sector], rC[sector], ang[sector]
    if Xc.size==0: return np.array([]), np.array([])

    # bin by angle; pick min radius per bin
    nbins = 600
    edges = np.linspace(-sector_factor*half_tooth, sector_factor*half_tooth, nbins+1)
    idx = np.digitize(ang, edges) - 1
    tx=[]; ty=[]
    for b in range(nbins):
        sel = (idx==b)
        if not np.any(sel): continue
        j = np.argmin(rC[sel])
        tx.append(Xc[sel][j]); ty.append(Yc[sel][j])
    tx = np.array(tx); ty = np.array(ty)
    # ensure monotone by angle
    order = np.argsort(np.arctan2(ty, tx))
    return tx[order], ty[order]

# try strict → relax → wide-open; finally fallback to a small arc
tro_x, tro_y = build_trochoid(1.6, 0.95, 361, 1400)
if tro_x.size==0:
    tro_x, tro_y = build_trochoid(2.0, 1.2, 361, 2200)
if tro_x.size==0:
    tro_x, tro_y = build_trochoid(2.5, 2.5, 721, 3000)

fallback_arc = False
if tro_x.size==0:
    # last-resort: approximate root with small circular arc (still produces a valid outline)
    th = np.linspace(-0.8*half_tooth, 0.8*half_tooth, 80)
    tro_x = rd*np.cos(th); tro_y = rd*np.sin(th)
    fallback_arc = True

# ----------------------------
# 3) Splice trochoid ↔ involute
# ----------------------------
ii, jj, djoin = nearest_join(xi, yi, tro_x, tro_y)
x_flank = np.concatenate([tro_x[:jj+1], xi[ii:]])
y_flank = np.concatenate([tro_y[:jj+1], yi[ii:]])

# ----------------------------
# 4) Build full tooth (mirror, rotate, close with addendum)
# ----------------------------
Rhalf = rot2d(half_tooth)
left  = Rhalf @ np.vstack([ x_flank,  y_flank])
right = Rhalf @ np.vstack([ x_flank, -y_flank])

pL = left[:, -1]; pR = right[:, -1]
xtop, ytop = arc_between_on_radius(ra, pL, pR, steps=180)

x_tooth = np.concatenate([left[0], xtop, right[0][::-1]])
y_tooth = np.concatenate([left[1], ytop, right[1][::-1]])

# ----------------------------
# 5) Pattern and plot
# ----------------------------
plt.figure(figsize=(7,7))
tooth_angle = 2*np.pi/z
for k in range(z):
    xr, yr = rotate_poly(x_tooth, y_tooth, k*tooth_angle)
    plt.plot(xr, yr, linewidth=1.2)

th = np.linspace(0, 2*np.pi, 800)
for r in [rd, rb, rp, ra]:
    plt.plot(r*np.cos(th), r*np.sin(th), linestyle=':', linewidth=0.9)

plt.gca().set_aspect('equal', adjustable='box')
ttl = "Spur gear with trochoidal root"
if fallback_arc: ttl += " (fallback arc at root)"
plt.title(ttl)
plt.xlabel("x"); plt.ylabel("y")
plt.tight_layout()
plt.show()

print(f"Join error (trochoid ↔ involute) ≈ {djoin:.3e} units;  trochoid_fallback={fallback_arc}")
