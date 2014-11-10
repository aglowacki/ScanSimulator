'''
Arthur Glowacki
APS ANL
11/07/2014
'''

import numpy as np
from Optics import *
import h5py
import sys

def init_objectives(lenses, photons, imageSize):
	objs = []
	for i in range(len(lenses)):
		obj = Objective()
		obj.generate(max_freq, imageSize, imageSize, lenses[i], 500., True)
		obj.numPhotons = photons[i]
		objs += [obj]
	return objs

def convert_dset(f, objs, oCalc, dset):
	ndset = f.create_dataset('/exchange/'+dset[0], dset[1].shape, chunks=(1, dset[1].shape[1], dset[1].shape[2]), compression='gzip', compression_opts=6 )
	for j in range(dset[1].shape[0]):
		#ndset[j] = oCalc.coherent(dset[1][j], objs)
		ndset[j] = oCalc.incoherent(dset[1][j], objs)
		#print 'finished',j,'of',180

def iter_grp(f, grp, objs, oCalc):
	for d in grp.iteritems():
		if len(d[1].shape) == 3:
			print 'converting',d[0]
			convert_dset(f, objs, oCalc, d)
		else:
			ndset = f.create_dataset('/exchange/'+d[0], d[1].shape)
			ndset[:] = d[1][:]
	
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print 'app.py Filename.h5 [inc or co] delta_nm objective_outter_1 photons_1 ... objective_outter_n photons_n'
		print '[inc or co]: inc = incoherent, co = coherent'
		sys.exit(0)

	print 'opening file',sys.argv[1]
	hf = h5py.File(sys.argv[1], 'r')
	cotype = sys.argv[2]
	delta_obj_nm = float(sys.argv[3])
	lenses = []
	photons = []
	for i in range(4, len(sys.argv), 2):
		lenses += [float(sys.argv[i]) ]
		photons += [float(sys.argv[i+1]) ]
	print 'delta nm',delta_obj_nm
	print 'lenses',lenses
	print 'photons',photons
	max_freq = 1.0 / 2.e-3 * delta_obj_nm

	print 'init objectives'
	d = hf['/exchange/data']
	objs = init_objectives(lenses, photons, d.shape[1])

	oCalc = Optics()
	grp = hf['/exchange']
	for i in range(len(lenses)):
		fname = sys.argv[1]+'_lens'+str(lenses[i])+'_ph'+str(photons[i])+'.h5'
		print 'saving',fname
		f = h5py.File(fname, 'w')
		iter_grp(f, grp, objs[i], oCalc)
		f.close()
	hf.close()
	'''
	for i in range(3):
		save_array('shifted_objective'+str(i)+'.jpg', objs[i].objective_array)
		save_array('new_image'+str(i)+'.jpg', new_image)
	'''
	print 'done'
