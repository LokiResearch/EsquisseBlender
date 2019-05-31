import os
import re
import bpy
from freestyle import *
from freestyle.functions import *
from freestyle.predicates import *
from freestyle.types import *
from freestyle.shaders import *
from parameter_editor import *
from freestyle.chainingiterators import *
from Esquisse import renderData
from Esquisse.cgal.mycgal import *

class GetEdgesShader(StrokeShader):
	
	def shade(self, stroke):
		n = len(stroke)
		for i in range(1,n):
			xa, ya = stroke[i-1].point
			xb, yb = stroke[i].point
			s = Segment(Point(xa,ya),Point(xb,yb))
			renderData.freestyle_visible_lines.append(s)

# Operators.select(AndUP1D(QuantitativeInvisibilityUP1D(0),pyNatureUP1D(Nature.EDGE_MARK)))
Operators.select(
	AndUP1D(
		QuantitativeInvisibilityUP1D(0),
		OrUP1D(pyNatureUP1D(Nature.SILHOUETTE),pyNatureUP1D(Nature.CREASE),pyNatureUP1D(Nature.MATERIAL_BOUNDARY),ContourUP1D())))
# Operators.select(pyNatureUP1D(Nature.EDGE_MARK))
#Operators.bidirectional_chain(ChainSilhouetteIterator())
#Operators.sort(pyZBP1D())

shaders_list = [
	GetEdgesShader(),
	]

Operators.create(TrueUP1D(), shaders_list)
