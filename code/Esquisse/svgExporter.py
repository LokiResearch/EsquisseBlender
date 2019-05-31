import bpy
import os
from bpy_extras import view3d_utils
from Esquisse.svg.path import Path, Line
from Esquisse import renderData
from Esquisse.screenHandler import *
from . import renderData
import math
import bmesh

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

class SVGExporter():

	def exportStillImage(self, context, object_handlers):
		self.screenHandler = screenHandler()

		svg = et.Element('svg', {'id' : 'root'})
		svg.set('xmlns','http://www.w3.org/2000/svg')
		svg.set('xmlns:xlink','http://www.w3.org/1999/xlink')
		svg.set('width',str(renderData.render_width))
		svg.set('height',str(renderData.render_height))

		self.esquisse = context.scene.esquisse



		if len(object_handlers) == 0:
			return

		layer = et.Element('g', {'id' : 'Objects'})
		for object_handler in object_handlers:
			object_layer = et.Element('g', {'id' : object_handler.mesh_object.name})
			if self.esquisse.render_fills:
				object_layer.append(self.fills_element(object_handler))
			object_layer.append(self.visible_strokes_element(object_handler))
			layer.append(object_layer)
		svg.append(layer)


		# # Layer 1 : Fills
		# if self.esquisse.render_fills:
		# 	layer = self.SVG_fills_layer(object_handlers) 
		# 	svg.append(layer)

		# # Layer 2 : Visibles Lines
		# if self.esquisse.render_visible_strokes:
		# 	layer = self.SVG_visible_strokes_layer(object_handlers) 
		# 	svg.append(layer)

		# Layer 3 : Hidden Lines
		if self.esquisse.render_hidden_strokes:
			layer = self.SVG_hidden_strokes_layer(object_handlers)
			svg.append(layer)

		# debug_region = et.Element('g', {'id' : 'raycasting_locations'})
		# for object_handler in object_handlers:
		# 	for region in object_handler.regions:
		# 		debug_region.append(self.drawPointInRegion(region))
		# svg.append(debug_region)
				
		indent(svg)
		tree = et.ElementTree(element=svg)
		tree.write(open(context.scene.esquisse.SVG_output_path, 'w'),encoding="unicode", xml_declaration=True)


	def exportGhostEffectImage(self, context, object_handlers, screenshots):
		self.screenHandler = screenHandler()

		svg = et.Element('svg')
		svg.set('xmlns','http://www.w3.org/2000/svg')
		svg.set('width',str(renderData.render_width))
		svg.set('height',str(renderData.render_height))

		self.esquisse = context.scene.esquisse

		if len(object_handlers) == 0:
			return

		layer = self.SVG_object_with_ghost(object_handlers, screenshots) 
		svg.append(layer)

		# Layer 3 : Hidden Lines
		if self.esquisse.render_hidden_strokes:
			layer = self.SVG_hidden_strokes_layer(object_handlers)
			svg.append(layer)

		indent(svg)
		tree = et.ElementTree(element=svg)
		tree.write(open(context.scene.esquisse.SVG_output_path, 'w'),encoding="unicode", xml_declaration=True)


	def SVG_object_with_ghost(self, object_handlers, screenshots):
		print("Writing fills layer")

		layer = et.Element('g', {'id' : 'Objects'})

		# Compute the draw order of the different handlers:
		for object_handler in object_handlers:
			if len(object_handler.ghost_handlers) == 0:
				# Object handler has no ghost handlers
				object_handler.index_of_draw = -1
			else:
				# Get the index of the last screenshots
				object_handler.index_of_draw = screenshots.index(max(object_handler.ghost_handlers.keys(), key=lambda screenshot: screenshots.index(screenshot)))


		object_handlers.sort(key=lambda handler: handler.index_of_draw)
		for handler in object_handlers:
			print(handler.mesh_object.name, ' draw index:', handler.index_of_draw)



		# Write handlers in order:
		for object_handler in object_handlers:
			print("Drawing: ",object_handler.mesh_object.name)
			object_layer = et.Element('g', {'id' : object_handler.mesh_object.name})
			if len(object_handler.ghost_handlers) == 0:
				# Write an object without ghosts
				if self.esquisse.render_fills:
					object_layer.append(self.fills_element(object_handler))
				object_layer.append(self.visible_strokes_element(object_handler))
			else:
				# Write object handler with ghosts
				# Step 1: Write the ghosts:
				object_layer.append(self.ghosts_layer(object_handler))

				# Step 2: Write the real object:
				real_layer = et.Element('g', {'id' : 'Real'})
				if self.esquisse.render_fills:
					real_layer.append(self.fills_element(object_handler))
				real_layer.append(self.visible_strokes_element(object_handler))
				object_layer.append(real_layer)

			layer.append(object_layer)
		return layer


	def ghosts_layer(self, object_handler):
		
		base_opacity = 0.2
		ghosts_layer = et.Element('g', {'id' : 'Ghosts'})
		
		# Compute the total of ghosts for the object (including interpolations)
		n_ghosts = 0
		screenshots = []
		for screenshot, ghost_handler in object_handler.ghost_handlers.items():
			n_ghosts += 1 # Add the ghost itself
			n_ghosts += len(ghost_handler.ghost_interpolations) # Add the number of interpolated ghosts
			screenshots.append(screenshot)

		idx = 0
		screenshots.sort(key= lambda x : x.number)
		#for screenshot, ghost_handler in object_handler.ghost_handlers.items():
		for screenshot in screenshots:
			ghost_handler = object_handler.ghost_handlers[screenshot]

			# Add the base ghost
			ghost_layer = et.Element('g', {'id' : "Ghost__%d"%idx})
			opacity = base_opacity + (1-2*base_opacity)*(idx/n_ghosts)
			if self.esquisse.render_fills:
				ghost_layer.append(self.fills_element(ghost_handler, opacity = opacity))
			ghost_layer.append(self.visible_strokes_element(ghost_handler, opacity = opacity))
			idx +=1

			# if the ghost screenshot has interpolated ghosts:
			if len(ghost_handler.ghost_interpolations) > 0:

				# Add the interpolated ghosts layer
				ghost_interpolations_layer = et.Element('g', {'id' : "Interpolated_Ghosts"})

				# Iterate on each interpolation
				for number, interpolated_ghost_handler in ghost_handler.ghost_interpolations.items():
					print("Interpolated_Ghost_%d"%number)
					ghost_interpolation_layer = et.Element('g', {'id' : "Interpolated_Ghost_%d"%number})
					opacity = base_opacity + (1-2*base_opacity)*(idx/n_ghosts)
					if self.esquisse.render_fills:
						ghost_interpolation_layer.append(self.fills_element(interpolated_ghost_handler, opacity = opacity))
					ghost_interpolation_layer.append(self.visible_strokes_element(interpolated_ghost_handler, opacity = opacity))
					idx +=1
					ghost_interpolations_layer.append(ghost_interpolation_layer)
				ghost_layer.append(ghost_interpolations_layer)

			ghosts_layer.append(ghost_layer)


		return ghosts_layer
















	def SVG_hidden_strokes_layer(self, object_handlers):
		print("Writing hidden strokes")

		layer = et.Element('g', {'id' : 'Hidden Strokes'})
		
		r,g,b,a = self.esquisse.hidden_strokes_color
		
		dasharray = None
		if self.esquisse.hidden_strokes_style in 'DASHED':
			dasharray = [self.esquisse.plain_dashed_value_hidden_strokes, self.esquisse.space_dashed_value_hidden_strokes]


		layer.append(self.path_element(renderData.freestyle_hidden_lines, 
			color = [r,g,b,a], 
			width = self.esquisse.hidden_strokes_width,
			dasharray = dasharray,
			fill = False
			))

		return layer


	def fills_element(self, object_handler, opacity = 1):
		fill_element = et.Element('g', {'id' : "Fills", 'opacity' : str(opacity)})

		if object_handler.mesh_object.esquisse.isScreen:
			# Create and add the clip path
			clipPath_id = object_handler.mesh_object.name.replace(" ", "")+'-clipPath'
			clipPath_element = et.Element('clipPath', {'id' : clipPath_id})
			clipPath_element.append(self.path_element_for_regions(object_handler.regions, fill = True))
			fill_element.append(clipPath_element)

			# Add the screen and refers to the clip path
			screen_element = et.Element('g', {'id' : 'screens'})
			screen_element.set('clip-path','url(#%s)'%clipPath_id)
			screen_element.append(self.screenHandler.getScreen(object_handler.mesh_object))
			fill_element.append(screen_element)

		else:
			# Get the group of regions by color:
			for regions in object_handler.group_regions_per_color():
				fill_element.append(self.path_element_for_regions(regions, color = regions[0].color, fill = True))	
		
		return fill_element	


	def visible_strokes_element(self, object_handler, opacity = 1):
		r,g,b,a = self.esquisse.visible_strokes_color
		dasharray = None
		if self.esquisse.visible_strokes_style in 'DASHED':
			dasharray = [self.esquisse.plain_dashed_value_visible_strokes, self.esquisse.space_dashed_value_visible_strokes]

		stroke_element = et.Element('g', {'id' : 'Strokes', 'opacity' : str(opacity)})
		stroke_element.append(self.path_element_for_regions(object_handler.regions, 
				color = [r,g,b,a], 
				width = self.esquisse.visible_strokes_width,
				dasharray = dasharray,
				fill = False))
		return stroke_element


	
	def drawPointInRegion(self, region):

		element = et.Element('circle', 
			{
				'cx'	: 	str(region.point_x),
				'cy'	: 	str(renderData.render_height-region.point_y),
				'r'	: '10',
				'fill' : 'red',
				'stroke' : 'black',
				})

		return element


	
	def path_element_for_regions(self, regions, color = [0,0,0,1], width = 1, dasharray = None, fill = False, closed = True):
		stroke_path_str = ''
		for region in regions:
			stroke_path_str += ' '+self.get_region_path(region)

		element = et.Element('path', 
			{
				'stroke-width' : str(width),
				'fill' : 'rgb(%d,%d,%d)'%(color[0]*255, color[1]*255, color[2]*255) if fill else 'none',
				'stroke' : 'rgb(%d,%d,%d)'%(color[0]*255, color[1]*255, color[2]*255),
				'stroke-width' : '%d'%width,
				'stroke-linecap' : 'round',
				'stroke-linejoin' : 'round',
				'stroke-opacity' : '%0.3f'%color[3],
				'fill-opacity' : '%0.3f'%color[3],
				'stroke-dasharray' : '%d,%d'%(dasharray[0], dasharray[1]) if dasharray else 'none',
				'fill-rule' : 'nonzero',
				'd' : stroke_path_str
				})

		return element


	def get_region_path(self, region):
		p = Path()
		n = len(region.contour)
		if n > 0:
			for i in range(0,n):		
				p.append(Line(complex(region.contour[i-1].x,renderData.render_height-region.contour[i-1].y),
					complex(region.contour[i].x,renderData.render_height-region.contour[i].y)))


			n_holes = len(region.holes)
			for i in range(0, n_holes):
				n = len(region.holes[i].contour)
				if n>0:
					for j in range(0,n):
						p.append(Line(complex(region.holes[i].contour[j-1].x,renderData.render_height-region.holes[i].contour[j-1].y),
							complex(region.holes[i].contour[j].x,renderData.render_height-region.holes[i].contour[j].y)))

			return p.d()
		else:
			return ""
	



	def path_element(self, paths, color = [0,0,0,1], width = 2, dasharray = None, fill = False, closed = False):
		stroke_path_str = ""
		for path in paths:
			stroke_path_str+= self.get_path_str(path, closed)

		element = et.Element('path', 
			{
				'stroke-width' : str(width),
				'fill' : 'rgb(%d,%d,%d)'%(color[0]*255, color[1]*255, color[2]*255) if fill else 'none',
				'stroke' : 'rgb(%d,%d,%d)'%(color[0]*255, color[1]*255, color[2]*255),
				'stroke-width' : '%d'%width,
				'stroke-linecap' : 'round',
				'stroke-linejoin' : 'round',
				'stroke-opacity' : '%0.3f'%color[3],
				'fill-opacity' : '%0.3f'%color[3],
				'stroke-dasharray' : '%d,%d'%(dasharray[0], dasharray[1]) if dasharray else 'none',
				'fill-rule' : 'nonzero',
				'd' : stroke_path_str
				})
		return element


	def get_path_str(self, path, closed = True):
		p = Path()
		n = len(path)
		if n > 1:
			for i in range(1,n):
				x1,y1 = path[i-1]
				x2,y2 = path[i]
				p.append(Line(complex(x1,renderData.render_height-y1),complex(x2,renderData.render_height-y2)))

			p.closed = closed
			return p.d()
		else:
			return ""




def indent(elem, level=0):
    indent_str = '\t'
    i = "\n" + level*indent_str
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent_str
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i













