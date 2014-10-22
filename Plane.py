import numpy as np

class Plane:
	def __init__( self, vecN, D ):
		self.planeN = vecN
		self.planeD = D
	
	def DistFromPlane( self, P ):
		# if N is not normalized this is *not* really the distance, 
		# but the computations work just the same.
		return np.dot(self.planeN, P) + self.planeD;
	
	def GetSegmentPlaneIntersection( self, P1, P2 ):
		outSegTips = []
		eps = 0.000001
		d1 = self.DistFromPlane(P1)
		d2 = self.DistFromPlane(P2)
		bP1OnPlane = (abs(d1) < eps)
		bP2OnPlane = (abs(d2) < eps)
	
		if bP1OnPlane:
			outSegTips += [P1]
	
		if bP2OnPlane:
			outSegTips += [P2]
	
		if bP1OnPlane and bP2OnPlane:
			return outSegTips
	
		if (d1*d2) > eps: # points on the same side of plane
			return outSegTips
	
		t = d1 / (d1 - d2) # 'time' of intersection point on the segment
		#P3 = ( P2[0] - P1[0], P2[1] - P1[1], P2[2] - P1[2] )
		P3 = ( ((P2[0] - P1[0]) * t) + P1[0], ((P2[1] - P1[1]) * t) + P1[1], ((P2[2] - P1[2]) * t) + P1[2] )
		#outSegTips += [ P1 + t * (P2 - P1) ]
		#outSegTips += [ P1 + t * P3 ]
		outSegTips += [P3]
		return outSegTips
	
	def TrianglePlaneIntersection( self, triA, triB, triC ):
		outSegTips = []
		outSegTips += self.GetSegmentPlaneIntersection(triA, triB)
		outSegTips += self.GetSegmentPlaneIntersection(triB, triC)
		outSegTips += self.GetSegmentPlaneIntersection(triC, triA)
		#RemoveDuplicates(outSegTips);  // not listed here - obvious functionality 
		return outSegTips
	
if __name__ == '__main__':
	triA = (1.0, -1.0, 0.0)
	triB = (1.0, 1.0, 0.0)
	triC = (-1.0, 1.0, 0.0)
	n = Plane( (0.0, 1.0, 0.0), 0.5)
	print n.TrianglePlaneIntersection(triA, triB, triC)

