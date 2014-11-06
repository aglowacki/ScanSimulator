'''
Arthur Glowacki
APS ANL
11/06/2014
'''

import numpy as np
from numpy.fft import *
from scipy.ndimage.interpolation import shift



class Optics:
	def __init__(self):
		self.numCondensers = 1
		self.delta_obj_nm = 1.0 # Change this, it is in inverse microns
		print 'init optics'

	def generate_objective(self, width, height):
		max_freq = 1.0 / 2.e-3 * self.delta_obj_nm
		objective_array = np.zeros((width, height), dtype=np.float32)
		for y in range(height):
			for x in range(width):
				objective_array[x][y] = max_freq * shift_dist_array
		scipy.misc.imsave('objective_array.jpg', objective_array)

	def coherent(self, image_array, objective_array):
		shift_objective = shift(objective_array)
		fft_image = fft(image_array, axis=1)
		for i in range(fft_image):
			fft_image[i] = fft_image[i] * shift_objective[i]
		fft_image = fft(image_array, axis=-1)
		return fft_image

	def incoherent(self, image_array, object_array):
		print 'coherent'


if __name__ == '__main__':
	print 'test save objective_array'
	o = Optics()
	o.generate_objective(512, 512)
	print 'done'
