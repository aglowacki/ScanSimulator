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

def gen_dist_circle_array(max_freq, outer_cutoff_freq, inner_cutoff_freq, width, height):
	midX = width / 2
	midY = height / 2
	dist_map = np.zeros((width, height), dtype=np.float32)
	for y in range(height):
		for x in range(width):
			d = distance((x, y), (midX, midY) ) 
			d2 = (d / midX) * max_freq #change  from pixels to freq
			if d2 < outer_cutoff_freq and d > inner_cutoff_freq:
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
		self.otf = None
		self.numPhotons = 0.0

	def generate(self, max_freq, width, height, outer_nm, inner_nm, bShifted):
		self.outer_nm = outer_nm
		self.inner_nm = inner_nm
		self.outer_cutoff_freq = 1./(2.e-3 * outer_nm) # in inverse microns
		#self.inner_cutoff_freq = 1./(2.e-3 * inner_nm)
		#if self.type:
		#	self.inner_cutoff_freq = .44/(2.e-3*outer_nm)

		#self.objective_array = np.zeros((width, height), dtype=np.float32)
		#shift_dist_array = shift(gen_dist_array(width, height))
		#self.objective_array = max_freq * shift_dist_array
		#print 'max', max_freq, 'out', self.outer_cutoff_freq, 'in', self.inner_cutoff_freq
		if bShifted:
			self.objective_array = shift(gen_dist_circle_array(max_freq, self.outer_cutoff_freq, self.inner_cutoff_freq, width, height ))
			psf = ifft2(self.objective_array) # already shifted
		else:
			self.objective_array = gen_dist_circle_array(max_freq, self.outer_cutoff_freq, self.inner_cutoff_freq, width, height )
			psf = shift(ifft2(self.objective_array))
		psf *= np.conj(psf)
		self.otf = fft2(psf)
		self.otf = self.otf / abs(self.otf).max()

######################### OPTICS ###################################


def coherent(image_array, objective):
	shift_objective = objective.objective_array #already shifted
	fft_image = fft2(image_array)
	fft_image *= shift_objective
	image_array = ifft2(fft_image)
	image_array *= np.conj(image_array)
	image_array = image_array.astype(np.float32)
	if objective.numPhotons > 0.0:
		image_array *= objective.numPhotons
		#image_array[:] = np.random.normal(image_array[:])
	return image_array

def incoherent(image_array, objective):
	#done in objective.generate()
	#psf = ifft2(objective.objective_array) # already shifted
	#psf *= np.conj(psf)
	#otf = fft2(psf)
	#otf = otf / abs(otf).max()
	image_array = image_array * np.conj(image_array)
	image_array = shift(image_array)
	fft_image = fft2(image_array)
	fft_image = fft_image * objective.otf
	image_array = ifft2(fft_image)
	image_array = shift(image_array)
	image_array = image_array.astype(np.float32)
	if objective.numPhotons > 0.0:
		image_array *= objective.numPhotons
		#image_array[:] = np.random.normal(image_array[:])
	return image_array


if __name__ == '__main__':
	print 'test save objective_array'
	image = scipy.misc.lena()
	imageSize = image.shape[0]
	delta_obj_nm = 1.0
	max_freq = 1.0 / 2.e-3 * delta_obj_nm

	lenses = [4., 30., 100.]
	#lenses = [1., 30., 100.]

	objs = []
	for i in range(3):
		obj = Objective()
		obj.generate(max_freq, imageSize, imageSize, lenses[i], 500., True)
		objs += [obj]

	#condenser = Condenser()
	#condenser.outer_nm = 10.
	#condenser.generate(max_freq, imageSize, imageSize)

	for i in range(3):
		new_image = coherent(image, objs[i])
		save_array('shifted_objective'+str(i)+'.jpg', objs[i].objective_array)
		save_array('new_image'+str(i)+'.jpg', new_image)
	print 'done'
