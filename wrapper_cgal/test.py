# Author: Axel Antoine
# https://axantoine.com

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

from mycgal import *

def printPoint(p):
	print("[%d,%d]"%(p.x,p.y))

def printContour(c):
	for p in c:
		printPoint(p)


s1 = Segment(Point(0,1),Point(6,1))
s2 = Segment(Point(1,0),Point(1,6))
s3 = Segment(Point(0,6),Point(6,0))

segments = VectorSegment()
segments.push_back(s1)
segments.push_back(s2)
segments.push_back(s3)


regions = computeRegions(segments)

for region in regions:
	printContour(region.contour)
	#print(region.holes)








