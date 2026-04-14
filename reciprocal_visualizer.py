import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons

def calc_real_vectors(a, b, c, alpha, beta, gamma):
    # Convert angles from degrees to radians
    alpha, beta, gamma = np.radians([alpha, beta, gamma])
    
    cg, sg = np.cos(gamma), np.sin(gamma)
    cb, ca = np.cos(beta), np.cos(alpha)
    
    # Calculate volume-related terms for triclinic cell
    c1 = (ca - cb * cg) / sg
    c2 = np.sqrt(1 - cb**2 - c1**2)
    
    # Real space vectors in Cartesian coordinates
    v_a = np.array([a, 0, 0])
    v_b = np.array([b * cg, b * sg, 0])
    v_c = np.array([c * cb, c * c1, c * c2])
    
    return v_a, v_b, v_c

def calc_reciprocal_vectors(v_a, v_b, v_c):
    # Physics convention: including the 2*pi factor
    V = np.dot(v_a, np.cross(v_b, v_c))
    v_a_star = 2 * np.pi * np.cross(v_b, v_c) / V
    v_b_star = 2 * np.pi * np.cross(v_c, v_a) / V
    v_c_star = 2 * np.pi * np.cross(v_a, v_b) / V
    return v_a_star, v_b_star, v_c_star

def rotate_y(vectors, theta_deg):
    # Rotation matrix around the Y-axis
    theta = np.radians(theta_deg)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    R = np.array([[cos_t, 0, sin_t], [0, 1, 0], [-sin_t, 0, cos_t]])
    return np.dot(vectors, R.T)

# --- Initial Parameters & Global State ---
init_a, init_b, init_c = 5.0, 5.0, 5.0
init_alpha, init_beta, init_gamma = 90.0, 90.0, 90.0
init_radius = 4.0 
init_rot = 0.0

current_view_range = 10.0 

# --- Setup Plot Window ---
fig = plt.figure(figsize=(16, 10))
ax = fig.add_subplot(111, projection='3d')
# Adjusted right margin to leave more room for the UI text labels
plt.subplots_adjust(left=0.0, bottom=0.05, right=0.75, top=0.95)

def update_limits():
    """Applies the current zoom level."""
    radius = s_rad.val
    show_ewald = check_ewald.get_status()[0]
    offset = -radius / 2 if show_ewald else 0
    
    ax.set_xlim([offset - current_view_range, offset + current_view_range])
    ax.set_ylim([-current_view_range, current_view_range])
    ax.set_zlim([-current_view_range, current_view_range])
    ax.set_box_aspect([1, 1, 1])

def on_scroll(event):
    """Smooth scroll-to-zoom."""
    global current_view_range
    if event.button == 'up':
        current_view_range *= 0.8  
    elif event.button == 'down':
        current_view_range *= 1.25 
        
    update_limits()
    fig.canvas.draw_idle() 

def update(val):
    elev = ax.elev
    azim = ax.azim
    ax.clear()
    
    a, b, c = s_a.val, s_b.val, s_c.val
    alpha, beta, gamma = s_alpha.val, s_beta.val, s_gamma.val
    radius = s_rad.val
    rot = s_rot.val
    show_ewald = check_ewald.get_status()[0]
    
    # 1. Calculate Both Sets of Vectors
    v_a, v_b, v_c = calc_real_vectors(a, b, c, alpha, beta, gamma)
    v_as, v_bs, v_cs = calc_reciprocal_vectors(v_a, v_b, v_c)
    
    # 2. Setup Grids
    grid_extent = 3 if show_ewald else 5
    h, k, l = np.meshgrid(np.arange(-grid_extent, grid_extent+1), 
                          np.arange(-grid_extent, grid_extent+1), 
                          np.arange(-grid_extent, grid_extent+1))
    
    # Generate Real Lattice Points
    real_points = h[..., np.newaxis] * v_a + k[..., np.newaxis] * v_b + l[..., np.newaxis] * v_c
    real_points = real_points.reshape(-1, 3)
    real_points = rotate_y(real_points, rot)
    RX, RY, RZ = real_points[:, 0], real_points[:, 1], real_points[:, 2]
    
    # Generate Reciprocal Lattice Points
    recip_points = h[..., np.newaxis] * v_as + k[..., np.newaxis] * v_bs + l[..., np.newaxis] * v_cs
    recip_points = recip_points.reshape(-1, 3)
    recip_points = rotate_y(recip_points, rot)
    X, Y, Z = recip_points[:, 0], recip_points[:, 1], recip_points[:, 2]
    
    # 3. Plotting Real Lattice (ALWAYS VISIBLE)
    ax.scatter(RX, RY, RZ, c='orange', s=20, alpha=0.3, label="Real Lattice")
    
    # 4. Plotting Reciprocal Lattice & Sphere
    if show_ewald:
        # Ewald Sphere Calculations
        center = np.array([-radius, 0, 0]) 
        distances = np.linalg.norm(recip_points - center, axis=1)
        tolerance = 0.2
        diffracting = np.abs(distances - radius) < tolerance
        
        # Reciprocal Lattice (Non-intersecting)
        ax.scatter(X[~diffracting], Y[~diffracting], Z[~diffracting], c='#1f77b4', s=25, alpha=0.5, label="Reciprocal Lattice")
        
        # Intersecting Points (Diffracting - 3rd Color)
        ax.scatter(X[diffracting], Y[diffracting], Z[diffracting], c='red', s=90, edgecolors='black', depthshade=False, label="Diffracting (Bragg)")
        
        # Draw Sphere
        u, v = np.mgrid[0:2*np.pi:25j, 0:np.pi:15j]
        xs = center[0] + radius * np.cos(u) * np.sin(v)
        ys = center[1] + radius * np.sin(u) * np.sin(v)
        zs = center[2] + radius * np.cos(v)
        ax.plot_wireframe(xs, ys, zs, color='green', alpha=0.15)
    else:
        # Plot the full reciprocal lattice normally (same color as toggle on)
        ax.scatter(X, Y, Z, c='#1f77b4', s=25, alpha=0.5, label="Reciprocal Lattice")
    
    # Origin Marker
    ax.scatter(0, 0, 0, c='black', s=150, marker='x', label="Origin")
    
    # Formatting
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Add Legend to keep track of colors
    ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.0), fontsize=10)
    
    update_limits()
    ax.view_init(elev=elev, azim=azim)

def handle_toggle(label):
    """Automatically zoom out when the massive lattice is enabled so it isn't clipped."""
    global current_view_range
    show_ewald = check_ewald.get_status()[0]
    if show_ewald:
        current_view_range = 10.0  
    else:
        current_view_range = 25.0  # Zoomed out further to accommodate both lattices
    update(None)

fig.canvas.mpl_connect('scroll_event', on_scroll)

# --- UI Sliders (Right Column Layout) ---
axcolor = 'yellow'
special_color = 'blue'

# SHIFTED LEFT to 0.80 and WIDENED to 0.14 so text doesn't get squished off-screen
slider_left = 0.80
slider_width = 0.14
slider_height = 0.02
vertical_spacing = 0.06
start_y = 0.85

ax_a  = plt.axes([slider_left, start_y - 0*vertical_spacing, slider_width, slider_height], facecolor=axcolor)
ax_b  = plt.axes([slider_left, start_y - 1*vertical_spacing, slider_width, slider_height], facecolor=axcolor)
ax_c  = plt.axes([slider_left, start_y - 2*vertical_spacing, slider_width, slider_height], facecolor=axcolor)
ax_al = plt.axes([slider_left, start_y - 3*vertical_spacing, slider_width, slider_height], facecolor=axcolor)
ax_be = plt.axes([slider_left, start_y - 4*vertical_spacing, slider_width, slider_height], facecolor=axcolor)
ax_ga = plt.axes([slider_left, start_y - 5*vertical_spacing, slider_width, slider_height], facecolor=axcolor)

ax_rad = plt.axes([slider_left, start_y - 7*vertical_spacing, slider_width, slider_height], facecolor=special_color)
ax_rot = plt.axes([slider_left, start_y - 8*vertical_spacing, slider_width, slider_height], facecolor=special_color)

# Toggle Switch
ax_ewald = plt.axes([slider_left, start_y - 10*vertical_spacing, slider_width, 0.04])
check_ewald = CheckButtons(ax_ewald, ['Show Ewald Sphere'], [True])

# Expanded Angle Range (10 to 170 degrees)
s_a = Slider(ax_a, 'a', 2.0, 10.0, valinit=init_a)
s_b = Slider(ax_b, 'b', 2.0, 10.0, valinit=init_b)
s_c = Slider(ax_c, 'c', 2.0, 10.0, valinit=init_c)
s_alpha = Slider(ax_al, 'α', 10.0, 170.0, valinit=init_alpha)
s_beta = Slider(ax_be, 'β', 10.0, 170.0, valinit=init_beta)
s_gamma = Slider(ax_ga, 'γ', 10.0, 170.0, valinit=init_gamma)
s_rad = Slider(ax_rad, 'Radius', 1.0, 10.0, valinit=init_radius)
s_rot = Slider(ax_rot, 'Rotation', 0.0, 360.0, valinit=init_rot)

# Links
sliders = [s_a, s_b, s_c, s_alpha, s_beta, s_gamma, s_rad, s_rot]
for s in sliders:
    s.on_changed(update)

check_ewald.on_clicked(handle_toggle)

update(None)
plt.show()