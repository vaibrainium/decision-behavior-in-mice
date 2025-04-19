import math

import cv2
import numpy as np
import torch
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
