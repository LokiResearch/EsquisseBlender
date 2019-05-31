import os
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
import math

class GetEdgesShader(StrokeShader):

	def shade(self, stroke):
		n = len(stroke)

		path = []
		for i in range(0,n):
			x, y = stroke[i].point
			path.append((x,y))
		
		renderData.freestyle_hidden_lines.append(path)


# Operators.select(AndUP1D(QuantitativeInvisibilityUP1D(0),pyNatureUP1D(Nature.EDGE_MARK)))
Operators.select(AndUP1D(NotUP1D(QuantitativeInvisibilityUP1D(0)), OrUP1D(pyNatureUP1D(Nature.SILHOUETTE),pyNatureUP1D(Nature.CREASE),ContourUP1D())))
# Operators.select(OrUP1D(pyNatureUP1D(Nature.SILHOUETTE),pyNatureUP1D(Nature.CREASE),ContourUP1D()))
# Operators.select(pyNatureUP1D(Nature.EDGE_MARK))
Operators.bidirectional_chain(ChainSilhouetteIterator())
Operators.sort(pyZBP1D())

shaders_list = [
	GetEdgesShader(),
	]

Operators.create(TrueUP1D(), shaders_list)


