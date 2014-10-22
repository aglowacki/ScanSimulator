'''
Arthur Glowacki
APS ANL
10/17/2014
'''

import sys
import numpy as np
import h5py

class H5Struct:
	def __init__(self):
		self.dset = None
		self.dims = None
		self.space = None
		self.count = None
		self.fid = None

class H5Exporter:
	def __init__(self):
		print 'init'
		self.datasetName = 'DS1'
		self.dimZ = 100
		self.dimX = 2000
		self.dimY = 2000
	def H5_CreateSample(self, filename):
		print 'saving sample file ',filename
    	# Initialize the data.
		wdata = np.zeros((self.dimX, self.dimY), dtype=np.float32)
		# Create a new file using the default properties.
		fid = h5py.h5f.create(filename)
		# Create the dataspace.  No maximum size parameter needed.
		dims = (self.dimZ, self.dimX, self.dimY)
		space = h5py.h5s.create_simple(dims)
		# automatically converts between different floating point types.
		dset = h5py.h5d.create(fid, self.datasetName, h5py.h5t.IEEE_F32LE, space)
		count = (1, self.dimX, self.dimY)
		for i in range(self.dimZ):
			print 'saving slice', i
			start = (i, 0, 0)
			space.select_hyperslab(start, count, None, None, h5py.h5s.SELECT_SET)
			dset.write(h5py.h5s.ALL, space, wdata)
		# Explicitly close and release resources.
		del space
		del dset
		del fid
		print 'done'
	def H5_Start(self, filename, dimX, dimY, dimZ):
		print 'starting file ',filename
		# Create a new file using the default properties.
		h5st = H5Struct()
		h5st.fid = h5py.h5f.create(filename)
		h5st.dims = (dimZ, dimX, dimY)
		h5st.space = h5py.h5s.create_simple(h5st.dims)
		#h5st.dset = h5py.h5d.create(h5st.fid, self.datasetName, h5py.h5t.IEEE_F64LE, h5st.space)
		h5st.dset = h5py.h5d.create(h5st.fid, self.datasetName, h5py.h5t.IEEE_F32LE, h5st.space)
		h5st.count = (1, dimX, dimY)
		return h5st
	def H5_SaveSlice(self, h5st, wdata, i):
		print 'saving slice', i
		start = (i, 0, 0)
		h5st.space.select_hyperslab(start, h5st.count, None, None, h5py.h5s.SELECT_SET)
		h5st.dset.write(h5py.h5s.ALL, h5st.space, wdata)
	def H5_End(self, h5st):
		del h5st.space
		del h5st.dset
		h5st.fid.close()
		del h5st.fid
		print 'done'

if __name__ == '__main__':
	#HdfWidget.show()
	dimX = 2000
	dimY = 2000
	dimZ = 100
	wdata = np.zeros((dimZ, dimX, dimY), dtype=np.uint16)
	saver = H5Exporter()
	#saver.H5_CreateSample('test.h5')
	h5st = saver.H5_Start('test.h5', dimX, dimY, dimZ)
	for i in range(dimZ):
		saver.H5_SaveSlice(h5st, wdata, i)
	saver.H5_End(h5st)

