'''
Arthur Glowacki
APS ANL
11/06/2014
'''

import numpy as np
from numpy.fft import *
import scipy.misc
import math

def distance( p1, p2):
	return math.sqrt( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 )

class Condenser:
	def __init__(self):
		print 'init condenser'

class Objective:
	def __init__(self):
		self.typeId = 0
		self.outer_nm = 0.0
		self.inner_nm = 0.0
		self.objective_array = None
		self.delta_obj_nm = 1.0 # Change this, it is in inverse microns

	def gen_dist_array(self, width, height):
		midX = width / 2
		midY = height / 2
		dist_map = np.zeros((width, height), dtype=np.float32)
		for y in range(height):
			for x in range(width):
				dist_map[x][y] = distance((x, y), (midX, midY) )
		return dist_map

	def generate_objective(self, width, height):
		max_freq = 1.0 / 2.e-3 * self.delta_obj_nm
		self.objective_array = np.zeros((width, height), dtype=np.float32)
		shift_dist_array = np.roll(self.gen_dist_array(width, height), width/2, axis=0)
		shift_dist_array = np.roll(shift_dist_array, height/2, axis=1)
		 
		for y in range(height):
			for x in range(width):
				self.objective_array[x][y] = max_freq * shift_dist_array[x][y]

	def save_array(self):
		scipy.misc.imsave('objective_array.jpg', self.objective_array)


class Optics:
	def __init__(self):
		self.numCondensers = 1
		print 'init optics'

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
	oCalc = Optics()
	obj = Objective()
	obj.generate_objective(512, 512)
	obj.save_array()
	print 'done'
