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

def shift(array):
	return np.roll( np.roll(array, array.shape[0]/2, axis=0), array.shape[1]/2, axis=1)

def save_array(imgname, array):
	scipy.misc.imsave(imgname, array)

def gen_dist_array(width, height):
	midX = width / 2
	midY = height / 2
	dist_map = np.zeros((width, height), dtype=np.float32)
	for y in range(height):
		for x in range(width):
			dist_map[x][y] = distance((x, y), (midX, midY) )
	return dist_map

def gen_dist_circle_array(width, height, in_dist):
	midX = width / 2
	midY = height / 2
	dist_map = np.zeros((width, height), dtype=np.float32)
	for y in range(height):
		for x in range(width):
			if in_dist > distance((x, y), (midX, midY) ):
				dist_map[x][y] = 1.
	return dist_map

######################## CONDENSER ################################

class Condenser:
	def __init__(self):
		self.typeId = 0
		self.outer_nm = 0.0
		self.inner_nm = 0.0
		self.condenser_array = None

	def generate(self, max_freq, width, height):
		self.condenser_array = np.zeros((width, height), dtype=np.float32)

######################### OBJECTIVE ################################

class Objective:
	def __init__(self):
		self.typeId = 0
		self.outer_nm = 0.0
		self.inner_nm = 0.0
		self.objective_array = None
		self.outer_cutoff_freq = 0.
		self.inner_cutoff_freq = 0.

	def generate(self, max_freq, width, height, outer_nm, inner_nm, bShifted):
		self.outer_nm = outer_nm
		self.inner_nm = inner_nm
		self.outer_cutoff_freq = 1./(2.e-3 * outer_nm) # in inverse microns
		self.inner_cutoff_freq = 1./(2.e-3 * inner_nm)
		#if self.type:
		#	self.inner_cutoff_freq = .44/(2.e-3*outer_nm)

		#self.objective_array = np.zeros((width, height), dtype=np.float32)
		#shift_dist_array = shift(gen_dist_array(width, height))
		#self.objective_array = max_freq * shift_dist_array
		if bShifted:
			self.objective_array = shift(gen_dist_circle_array(width, height, width /10))
		else:
			self.objective_array = gen_dist_circle_array(width, height, width /2)

######################### OPTICS ###################################

class Optics:
	def __init__(self):
		self.numCondensers = 1

	def coherent(self, image_array, objective):
		#shift_objective = shift(objective.objective_array)
		shift_objective = objective.objective_array #already shifted
		fft_image = fft2(image_array)
		fft_image *= shift_objective
		image_array = ifft2(fft_image)
		image_array *= np.conj(image_array)
		return image_array.astype(np.float32)

	def incoherent(self, image_array, objective):
		#psf = shift(objective.objective_array)
		psf = ifft2(objective.objective_array) # already shifted
		psf *= np.conj(psf)
		otf = fft2(psf)
		otf = otf /max(abs(otf))
		image_array = image_array * conj(image_array)
		image_array = shift(image_array)
		fft_image = fft2(image_array)
		fft_image = fft_image * otf
		image_array = ifft2(fft_image)
		image_array = shift(image_array)
		return image_array.astype(np.float32)


if __name__ == '__main__':
	print 'test save objective_array'
	image = scipy.misc.lena()
	imageSize = image.shape[0]
	delta_obj_nm = 1.0
	max_freq = 1.0 / 2.e-3 * delta_obj_nm

	obj = Objective()
	obj.generate(max_freq, imageSize, imageSize, 4., 500., True)

	condenser = Condenser()
	condenser.outer_nm = 10.
	condenser.generate(max_freq, imageSize, imageSize)

	oCalc = Optics()
	new_image = oCalc.coherent(image, obj)
	save_array('shifted_objective.jpg', obj.objective_array)
	save_array('new_image.jpg', new_image)
	save_array('lena.jpg', image)
	print 'done'
