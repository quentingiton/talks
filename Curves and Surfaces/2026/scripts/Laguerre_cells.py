import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.integrate import quad
from scipy.optimize import minimize

# --- 1. SETUP PARAMETERS ---
c1, c2, c3 = -2, 0.0, 1  # Centers of the Gaussians

def unnormalized_density(x, t1, t2, t3):
    u1 = np.exp(t1 - (x - c1)**2)
    u2 = np.exp(t2 - (x - c2)**2)
    u3 = np.exp(t3 - (x - c3)**2)
    return np.maximum(np.maximum(u1, u2), u3)

def unnormalized_moment(x, t1, t2, t3):
    return x * unnormalized_density(x, t1, t2, t3)

def exact_boundaries(t1, t2, t3):
    b12 = (t2 - t1) / (2 * (c1 - c2)) + (c1 + c2) / 2
    b23 = (t3 - t2) / (2 * (c2 - c3)) + (c2 + c3) / 2
    return b12, b23

# --- 2. SETUP THE PLOT ---
fig, (ax_plot, ax_bar) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, figsize=(12, 6))
plt.subplots_adjust(bottom=0.35)

x = np.linspace(-4, 3.5, 500)

line, = ax_plot.plot(x, np.zeros_like(x), color='purple', lw=2)
fill1 = ax_plot.fill_between(x, 0, 0, color='purple', alpha=0.2)
fill2 = ax_plot.fill_between(x, 0, 0, color='purple', alpha=0.4)
fill3 = ax_plot.fill_between(x, 0, 0, color='purple', alpha=0.2)

vline1 = ax_plot.axvline(x=0, color='purple', linestyle='--')
vline2 = ax_plot.axvline(x=0, color='purple', linestyle='--')

center_line1, = ax_plot.plot([], [], color='gray', linestyle=':', lw=2, zorder=4)
center_line2, = ax_plot.plot([], [], color='gray', linestyle=':', lw=2, zorder=4)
center_line3, = ax_plot.plot([], [], color='gray', linestyle=':', lw=2, zorder=4)

t_gen1 = ax_plot.text(c1, 0, r'$\hat{x}_1^{(n)}$', color='#d77e62', ha='center', va='bottom', fontsize=12)
t_gen2 = ax_plot.text(c2, 0, r'$\hat{x}_2^{(n)}$', color='#d77e62', ha='center', va='bottom', fontsize=12)
t_gen3 = ax_plot.text(c3, 0, r'$\hat{x}_3^{(n)}$', color='#d77e62', ha='center', va='bottom', fontsize=12)

# Changed to 'purple' to match the density curve
bary_points, = ax_plot.plot([], [], 'o', color='purple', markersize=8, zorder=6)
t_bary1 = ax_plot.text(0, -0.03, r'$\hat{x}_1^{(n+1)}$', color='purple', ha='center', va='top', fontsize=12)
t_bary2 = ax_plot.text(0, -0.03, r'$\hat{x}_2^{(n+1)}$', color='purple', ha='center', va='top', fontsize=12)
t_bary3 = ax_plot.text(0, -0.03, r'$\hat{x}_3^{(n+1)}$', color='purple', ha='center', va='top', fontsize=12)

ax_plot.set_xlim(-4, 3.5)
ax_plot.set_ylim(-0.15, 0.8) 
ax_plot.set_title(r"Probability density $\tilde{\rho}_K$")
ax_plot.axhline(0, color='black', linewidth=1) 

bars = ax_bar.bar(['Cell 1', 'Cell 2', 'Cell 3'], [0, 0, 0], color=['#dcbfe8', '#dcbfe8', '#dcbfe8'])
ax_bar.axhline(y=1/3, color='#d77e62', linestyle='--', label='Target (1/3)')
ax_bar.set_ylim(0, 0.6)
ax_bar.set_title("Mass Distribution")
ax_bar.legend()

def update(val):
    if is_animating and not is_gliding: return
    
    t1, t2, t3 = s_t1.val, s_t2.val, s_t3.val
    
    Z, _ = quad(unnormalized_density, -10, 10, args=(t1, t2, t3), limit=100)
    b12, b23 = exact_boundaries(t1, t2, t3)
    
    y = unnormalized_density(x, t1, t2, t3) / Z
    line.set_ydata(y)
    
    global fill1, fill2, fill3
    fill1.remove(); fill2.remove(); fill3.remove()
    
    mask1 = x <= b12
    mask2 = (x > b12) & (x <= b23)
    mask3 = x > b23
    
    fill1 = ax_plot.fill_between(x[mask1], y[mask1], color='#dcbfe8')
    fill2 = ax_plot.fill_between(x[mask2], y[mask2], color='#dcbfe8')
    fill3 = ax_plot.fill_between(x[mask3], y[mask3], color="#dcbfe8")
    
    vline1.set_xdata([b12, b12])
    vline2.set_xdata([b23, b23])
    
    peak1, peak2, peak3 = np.exp(t1)/Z, np.exp(t2)/Z, np.exp(t3)/Z
    center_line1.set_data([c1, c1], [0, peak1])
    center_line2.set_data([c2, c2], [0, peak2])
    center_line3.set_data([c3, c3], [0, peak3])
    t_gen1.set_position((c1, peak1 + 0.02))
    t_gen2.set_position((c2, peak2 + 0.02))
    t_gen3.set_position((c3, peak3 + 0.02))
    
    m1, _ = quad(unnormalized_density, -10, b12, args=(t1, t2, t3), limit=100)
    m2, _ = quad(unnormalized_density, b12, b23, args=(t1, t2, t3), limit=100)
    m3, _ = quad(unnormalized_density, b23, 10, args=(t1, t2, t3), limit=100)
    
    mom1, _ = quad(unnormalized_moment, -10, b12, args=(t1, t2, t3), limit=100)
    mom2, _ = quad(unnormalized_moment, b12, b23, args=(t1, t2, t3), limit=100)
    mom3, _ = quad(unnormalized_moment, b23, 10, args=(t1, t2, t3), limit=100)
    
    bary1 = mom1 / m1 if m1 > 1e-6 else np.nan
    bary2 = mom2 / m2 if m2 > 1e-6 else np.nan
    bary3 = mom3 / m3 if m3 > 1e-6 else np.nan
    
    bary_points.set_data([bary1, bary2, bary3], [0, 0, 0])
    if not np.isnan(bary1): t_bary1.set_position((bary1, -0.04))
    if not np.isnan(bary2): t_bary2.set_position((bary2, -0.04))
    if not np.isnan(bary3): t_bary3.set_position((bary3, -0.04))
    
    masses = [m1/Z, m2/Z, m3/Z]
    for bar, m in zip(bars, masses):
        bar.set_height(m)
        if abs(m - 1/3) < 0.005:
            bar.set_color('#d77e62')
        else:
            bar.set_color('#dcbfe8')
            
    fig.canvas.draw_idle()

is_animating = False
is_gliding = False

def optimize_thetas(event):
    global is_animating, is_gliding
    if is_animating: return
    is_animating = True 
    is_gliding = False
    
    btn_opt.label.set_text("Computing...")
    plt.pause(0.01) # Force UI flush
    
    # Temporarily mute sliders so minimize doesn't trigger UI updates
    s_t1.eventson = False; s_t2.eventson = False; s_t3.eventson = False
    
    t1_fixed = s_t1.val
    
    def objective(vars):
        t2, t3 = vars
        b12, b23 = exact_boundaries(t1_fixed, t2, t3)
        if b12 >= b23: return 1000.0 # Prevent cells from getting totally crushed
        
        m1, _ = quad(unnormalized_density, -10, b12, args=(t1_fixed, t2, t3), limit=50)
        m2, _ = quad(unnormalized_density, b12, b23, args=(t1_fixed, t2, t3), limit=50)
        m3, _ = quad(unnormalized_density, b23, 10, args=(t1_fixed, t2, t3), limit=50)
        
        Z = m1 + m2 + m3
        return (m1/Z - 1/3)**2 + (m2/Z - 1/3)**2 + (m3/Z - 1/3)**2

    res = minimize(objective, [s_t2.val, s_t3.val], method='Nelder-Mead')
    
    s_t1.eventson = True; s_t2.eventson = True; s_t3.eventson = True
    
    t2_start, t3_start = s_t2.val, s_t3.val
    t2_opt, t3_opt = res.x[0], res.x[1]
    
    is_gliding = True
    frames_per_phase = 40
    
    btn_opt.label.set_text("Theta 2...")
    for i in range(1, frames_per_phase + 1):
        alpha = i / frames_per_phase
        ease = alpha * alpha * (3 - 2 * alpha) 
        s_t2.set_val(t2_start + (t2_opt - t2_start) * ease)
        plt.pause(0.015) 
        
    plt.pause(0.2)

    btn_opt.label.set_text("Theta 3...")
    for i in range(1, frames_per_phase + 1):
        alpha = i / frames_per_phase
        ease = alpha * alpha * (3 - 2 * alpha) 
        s_t3.set_val(t3_start + (t3_opt - t3_start) * ease)
        plt.pause(0.015) 
    
    btn_opt.label.set_text("Optimise!")
    is_animating = False
    is_gliding = False

axcolor = 'lightgoldenrodyellow'

ax_t1 = plt.axes([0.10, 0.20, 0.55, 0.03], facecolor=axcolor)
ax_t2 = plt.axes([0.10, 0.13, 0.55, 0.03], facecolor=axcolor)
ax_t3 = plt.axes([0.10, 0.06, 0.55, 0.03], facecolor=axcolor)

s_t1 = Slider(ax_t1, 'Theta 1', -4.0, 4.0, valinit=0.0, valstep=0.05, color='#dd9ea4')
s_t2 = Slider(ax_t2, 'Theta 2', -4.0, 4.0, valinit=0.0, valstep=0.05, color='#dd9ea4')
s_t3 = Slider(ax_t3, 'Theta 3', -4.0, 4.0, valinit=0.0, valstep=0.05, color='#dd9ea4')

s_t1.on_changed(update)
s_t2.on_changed(update)
s_t3.on_changed(update)

ax_opt = plt.axes([0.76, 0.10, 0.14, 0.10])
btn_opt = Button(ax_opt, 'Optimise!', color='#dd9ea4', hovercolor='#eecacc')
btn_opt.on_clicked(optimize_thetas)

update(0)
plt.show()