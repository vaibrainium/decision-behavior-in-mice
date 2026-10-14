import math

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from scipy.ndimage import zoom


def resample_stimulus_to_degrees(stimulus_array, ppd, dx_deg=0.2, dy_deg=0.2):
    """Resample (t, w_px, h_px) stimulus to (t, w_deg, h_deg) based on degree resolution."""
    t, w_px, h_px = stimulus_array.shape
    zoom_x = ppd * dx_deg
    zoom_y = ppd * dy_deg
    zoom_factors = (1, 1 / zoom_x, 1 / zoom_y)
    return zoom(stimulus_array, zoom_factors, order=1)


def get_stimulus_array_uw(screen_resolution, rdk, pars, rt_frame, ppd=10, dx_deg=0.2, dy_deg=0.2, convert_to_degrees=False, return_coords=False):
    """UW-style stimulus generation. Optionally returns deg grid or resampled stimulus."""
    w, h = screen_resolution
    stimulus_array = np.empty((rt_frame, w, h), dtype=np.uint8)
    pulses = list(pars.get("pulse", []))
    temp_img = np.zeros((rdk.stimulus_size[1], rdk.stimulus_size[0]), dtype=np.uint8)

    for i in range(rt_frame):
        if i == 0:
            rdk.new_stimulus(pars)
        elif pulses and i == pulses[0][0] - 1:
            rdk.move_dots(new_coherence=pulses[0][1])
            pulses.pop(0)
        else:
            rdk.move_dots()

        temp_img.fill(0)
        for x, y in zip(rdk.x, rdk.y):
            cv2.circle(temp_img, (int(x), int(y)), rdk.radius, 255, -1)

        stimulus_array[i] = temp_img.T

    if convert_to_degrees:
        stimulus_array = resample_stimulus_to_degrees(stimulus_array, ppd, dx_deg, dy_deg)

    if return_coords:
        if convert_to_degrees:
            w_deg, h_deg = stimulus_array.shape[1:]
            x_deg = np.linspace(-w_deg // 2, w_deg // 2, w_deg) * dx_deg
            y_deg = np.linspace(-h_deg // 2, h_deg // 2, h_deg) * dy_deg
        else:
            deg_per_pixel = 1 / ppd
            x_deg = np.linspace(-w // 2, w // 2, w) * deg_per_pixel
            y_deg = np.linspace(-h // 2, h // 2, h) * deg_per_pixel
        t_sec = np.arange(rt_frame) / 60.0
        return stimulus_array, (x_deg, y_deg, t_sec)

    return stimulus_array


def get_stimulus_array_ucla(screen_resolution, rdk, pars, rt_frame, ppd=10, dx_deg=0.2, dy_deg=0.2, convert_to_degrees=False, return_coords=False):
    """UCLA-style stimulus generation. Optionally returns deg grid or resampled stimulus."""
    w, h = screen_resolution
    stimulus_array = np.empty((rt_frame, w, h), dtype=np.uint8)
    pulses = list(pars.get("pulse", []))
    temp_img = np.zeros((rdk.stimulusSize[1], rdk.stimulusSize[0]), dtype=np.uint8)

    for i in range(rt_frame):
        if i == 0:
            rdk.newStimulus(pars["coherence"], pars["seed"])
        elif pulses and i == pulses[0][0] - 1:
            rdk.updateBurst(burstCoherence=pulses[0][1])
            pulses.pop(0)
        else:
            rdk.moveDots()

        temp_img.fill(0)
        for x, y in zip(rdk.x, rdk.y):
            cv2.circle(temp_img, (int(x), int(y)), rdk.radius, 255, -1)

        stimulus_array[i] = temp_img.T

    if convert_to_degrees:
        stimulus_array = resample_stimulus_to_degrees(stimulus_array, ppd, dx_deg, dy_deg)

    if return_coords:
        if convert_to_degrees:
            w_deg, h_deg = stimulus_array.shape[1:]
            x_deg = np.linspace(-w_deg // 2, w_deg // 2, w_deg) * dx_deg
            y_deg = np.linspace(-h_deg // 2, h_deg // 2, h_deg) * dy_deg
        else:
            deg_per_pixel = 1 / ppd
            x_deg = np.linspace(-w // 2, w // 2, w) * deg_per_pixel
            y_deg = np.linspace(-h // 2, h // 2, h) * deg_per_pixel
        t_sec = np.arange(rt_frame) / 60.0
        return stimulus_array, (x_deg, y_deg, t_sec)

    return stimulus_array


###################################################################################
# Motion Energy Filters
def create_motion_energy_filters_from_degrees(
    rf_size_deg=3.0,
    surround_width_deg=1.5,
    temporal_tuning_hz=10.0,
    x_range_deg=(-6, 6),
    y_range_deg=(-6, 6),
    t_range_s=(0, 0.6),
    dx=0.2,
    dy=0.2,
    dt=1 / 60,
    device=None,
):
    """
    Create motion energy filters (right/left selective) from biologically relevant parameters.
    Returns filters shaped for 3D conv use: (out_channels, in_channels, T, H, W).
    """

    sigma_c = rf_size_deg / 2
    sigma_g = surround_width_deg / 2
    tau_s = 1 / (2 * np.pi * temporal_tuning_hz)
    k = 1 / tau_s

    x = np.arange(x_range_deg[0], x_range_deg[1], dx)
    y = np.arange(y_range_deg[0], y_range_deg[1], dy)
    t = np.arange(t_range_s[0], t_range_s[1], dt)

    r1 = np.empty((len(t), len(x), len(y)))
    r2 = np.empty((len(t), len(x), len(y)))
    l1 = np.empty((len(t), len(x), len(y)))
    l2 = np.empty((len(t), len(x), len(y)))

    def f1(x, y, sigma_c, sigma_g):
        alpha = np.arctan(x / sigma_c)
        return (np.cos(alpha) ** 4) * np.cos(4 * alpha) * np.exp(-(y**2) / (2 * sigma_g**2))

    def f2(x, y, sigma_c, sigma_g):
        alpha = np.arctan(x / sigma_c)
        return (np.cos(alpha) ** 4) * np.sin(4 * alpha) * np.exp(-(y**2) / (2 * sigma_g**2))

    def g1(t, k):
        return ((k * t) ** 3) * np.exp(-k * t) * ((1 / math.factorial(3)) - ((k * t) ** 2) / math.factorial(5))

    def g2(t, k):
        return ((k * t) ** 5) * np.exp(-k * t) * ((1 / math.factorial(5)) - ((k * t) ** 2) / math.factorial(7))

    for ti, tt in enumerate(t):
        g1t = g1(tt, k)
        g2t = g2(tt, k)
        for xi, xx in enumerate(x):
            fx1 = f1(xx, y, sigma_c, sigma_g)
            fx2 = f2(xx, y, sigma_c, sigma_g)

            r1[ti, xi, :] = fx1 * g1t + fx2 * g2t
            r2[ti, xi, :] = fx2 * g1t - fx1 * g2t
            l1[ti, xi, :] = fx1 * g1t - fx2 * g2t
            l2[ti, xi, :] = fx2 * g1t + fx1 * g2t

    # Convert to 5D torch tensors: [out_channels=2, in_channels=1, T, H, W]
    r1 = torch.tensor(r1, dtype=torch.float32)
    r2 = torch.tensor(r2, dtype=torch.float32)
    l1 = torch.tensor(l1, dtype=torch.float32)
    l2 = torch.tensor(l2, dtype=torch.float32)

    right_filters = [r1, r2]
    left_filters = [l1, l2]

    if device is not None:
        right_filters = [f.to(device) for f in right_filters]
        left_filters = [f.to(device) for f in left_filters]

    return right_filters, left_filters, (x, y, t)


###################################################################################
# Mouse motion energy (dissemination/reports/motion-energy-methods.md, section 3)
#
# Same Adelson & Bergen / Kiani et al. (2008) filters as above, retuned for mouse vision and
# computed in a separable, causal form:
#   - filters tuned to the dot speed (~30 deg/s) inside the mouse passband:
#     preferred SF ~ 0.477 / sigma_c = 0.080 c/deg, preferred TF ~ 0.071 * k = 2.4 Hz
#   - stimulus and filters share one 0.5 deg grid; frames are rendered at native resolution and
#     area-averaged onto it (no aliasing, overlapping dots look as they did on screen)
#   - temporal filtering is causal (zero padding before stimulus onset, no future frames);
#     spatial borders are zero padded (dark surround)
#   - net energy uses the exact identity (R1^2 + R2^2) - (L1^2 + L2^2) = 4 (A11 A22 - A12 A21),
#     where A_ab = stimulus * G(y) * f_a(x) * g_b(t), so only 1-D convolutions are needed

MOUSE_ME_PARAMS = {
    "sigma_c_deg": 6.0,
    "sigma_g_deg": 3.0,
    "k_per_s": 34.0,
    "dx_deg": 0.5,
    "x_extent_deg": 18.0,  # +-3 sigma_c
    "y_extent_deg": 9.0,  # +-3 sigma_g
    "t_extent_s": 0.55,
    "dt_s": 1 / 60,
}


def render_stimulus_deg(rig, rdk, pars, n_frames, ppd, dx_deg=MOUSE_ME_PARAMS["dx_deg"]):
    """Replay a trial's RDK at native resolution and area-average each frame onto a dx_deg grid.

    Returns uint8 (n_frames, ny, nx) with the fraction of each sample covered by dots (0-255; kept
    as uint8 so it is cheap to pass between processes); axis 1 is screen y (down), axis 2 is screen
    x (right). `pars` holds seed, coherence and optional
    pulse = [(onset_frame, coherence), (offset_frame, coherence)] in 1-based frame numbers.
    """
    w, h = rdk.stimulusSize if rig == "ucla" else rdk.stimulus_size
    out_size = (round(w / (ppd * dx_deg)), round(h / (ppd * dx_deg)))
    stimulus = np.empty((n_frames, out_size[1], out_size[0]), dtype=np.uint8)
    pulses = list(pars.get("pulse", []))
    frame = np.zeros((h, w), dtype=np.uint8)

    for i in range(n_frames):
        if i == 0:
            if rig == "ucla":
                rdk.newStimulus(pars["coherence"], pars["seed"])
            else:
                rdk.new_stimulus(pars)
        elif pulses and i == pulses[0][0] - 1:
            if rig == "ucla":
                rdk.updateBurst(burstCoherence=pulses[0][1])
            else:
                rdk.move_dots(new_coherence=pulses[0][1])
            pulses.pop(0)
        elif rig == "ucla":
            rdk.moveDots()
        else:
            rdk.move_dots()

        frame.fill(0)
        for x, y in zip(rdk.x, rdk.y):
            cv2.circle(frame, (int(x), int(y)), rdk.radius, 255, -1)
        stimulus[i] = cv2.resize(frame, out_size, interpolation=cv2.INTER_AREA)

    return stimulus


def mouse_me_kernels(params=MOUSE_ME_PARAMS):
    """1-D kernels of the separable mouse filters, sampled on the shared grid.

    Returns dict with gy (Gaussian in y), fx (2, nx: even f1, odd f2) and gt (2, nt: fast n=3,
    slow n=5; gt[:, 0] is lag 0).
    """
    dx = params["dx_deg"]
    nx = round(params["x_extent_deg"] / dx)
    ny = round(params["y_extent_deg"] / dx)
    x = np.arange(-nx, nx + 1) * dx
    y = np.arange(-ny, ny + 1) * dx
    t = np.arange(0, params["t_extent_s"], params["dt_s"])

    alpha = np.arctan(x / params["sigma_c_deg"])
    kt = params["k_per_s"] * t
    return {
        "gy": np.exp(-(y**2) / (2 * params["sigma_g_deg"] ** 2)),
        "fx": np.stack([np.cos(alpha) ** 4 * np.cos(4 * alpha), np.cos(alpha) ** 4 * np.sin(4 * alpha)]),
        "gt": np.stack([kt**n * np.exp(-kt) * (1 / math.factorial(n) - kt**2 / math.factorial(n + 2)) for n in (3, 5)]),
    }


def mouse_me_kernels_torch(device, params=MOUSE_ME_PARAMS):
    """Kernels from mouse_me_kernels as float32 tensors shaped for F.conv1d (out, 1, taps)."""
    kernels = mouse_me_kernels(params)
    return {name: torch.tensor(k, dtype=torch.float32, device=device).reshape(-1, 1, k.shape[-1]) for name, k in kernels.items()}


def compute_mouse_me(stimulus, kernels):
    """Net motion energy of a (T, ny, nx) stimulus tensor; positive = rightward (+x).

    A uint8 stimulus from render_stimulus_deg is scaled to [0, 1] first. `kernels` comes from mouse_me_kernels_torch. Uses true convolution (kernels flipped for
    F.conv1d), zero padding in space and causal zero padding in time, so output frame t depends
    only on frames <= t and the output has the same shape as the input.
    """
    if stimulus.dtype == torch.uint8:
        stimulus = stimulus.float() / 255
    T, H, W = stimulus.shape
    gy, fx, gt = kernels["gy"], kernels["fx"], kernels["gt"]

    # y: Gaussian (symmetric, so no flip needed)
    s = stimulus.permute(0, 2, 1).reshape(T * W, 1, H)
    s = F.conv1d(s, gy, padding=gy.shape[-1] // 2).reshape(T, W, H).permute(0, 2, 1)
    # x: f1, f2 -> (T, H, 2, W)
    s = F.conv1d(s.reshape(T * H, 1, W), fx.flip(-1), padding=fx.shape[-1] // 2).reshape(T, H, 2, W)
    # t: g1, g2, causal -> (H, 2, W, 2, T), indexed [y, a, x, b, t]
    s = s.permute(1, 2, 3, 0).reshape(H * 2 * W, 1, T)
    s = F.conv1d(F.pad(s, (gt.shape[-1] - 1, 0)), gt.flip(-1)).reshape(H, 2, W, 2, T)

    me = 4 * (s[:, 0, :, 0] * s[:, 1, :, 1] - s[:, 0, :, 1] * s[:, 1, :, 0])
    return me.permute(2, 0, 1)


def pool_mouse_me(me):
    """Spatially averaged ME time series of a (T, ny, nx) array.

    Quadrants keep the labels of the earlier pipeline: Q1 left-top, Q2 left-bottom, Q3 right-top,
    Q4 right-bottom (screen y points down).
    """
    _, ny, nx = me.shape
    hy, hx = ny // 2, nx // 2
    return {
        "global": me.mean(dim=(1, 2)),
        "center": me[:, ny // 4 : 3 * ny // 4, nx // 4 : 3 * nx // 4].mean(dim=(1, 2)),
        "quadrants": {
            "Q1": me[:, :hy, :hx].mean(dim=(1, 2)),
            "Q2": me[:, hy:, :hx].mean(dim=(1, 2)),
            "Q3": me[:, :hy, hx:].mean(dim=(1, 2)),
            "Q4": me[:, hy:, hx:].mean(dim=(1, 2)),
        },
    }
