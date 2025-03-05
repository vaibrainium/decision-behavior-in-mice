def get_gpu_info():
	"""Gathers GPU information using Numba package
	Returns:
	num_sm: Number of total Streaming Multiprocessors on GPU
	num_cores_per_sm: Number of total SMs on GPU.
	"""
	from numba import cuda

	cc_cores_per_SM_dict = {
		(2, 0): 32,
		(2, 1): 48,
		(3, 0): 192,
		(3, 5): 192,
		(3, 7): 192,
		(5, 0): 128,
		(5, 2): 128,
		(6, 0): 64,
		(6, 1): 128,
		(7, 0): 64,
		(7, 5): 64,
		(8, 0): 64,
		(8, 6): 128,
	}

	device = cuda.get_current_device()
	num_sm = device.MULTIPROCESSOR_COUNT
	my_cc = device.compute_capability
	num_cores_per_sm = cc_cores_per_SM_dict.get(my_cc)
	total_cores = num_cores_per_sm * num_sm

	return num_sm, num_cores_per_sm


def get_device():
	if numba.cuda.is_available():
		device = "GPU"
		num_sm, num_cores_per_sm = get_gpu_info()
		blockdim = 2 * 32 * (num_cores_per_sm // 32)  # num_blocks should be 2x - 4x times number of threads and should be multiplier of 32
		return [device, blockdim]
	device = "CPU"
	return [device]
