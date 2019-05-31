import numpy as np
import re
import base64
from . import renderData
from .FunctionsUtils import *
from mathutils import *
from .svg.parser import parse_path
from .svg.path import Path, Line, CubicBezier, QuadraticBezier

from .cv2 import cv2

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

class screenHandler():

	def __init__(self):
		self.esquisse = renderData.scene.esquisse
		self.transform_matrix = Matrix()

	def getScreen(self, screen_obj):

		print("### Generating screen interface ###")


		# Looking for screen object :
		self.screen_obj = screen_obj

		r,g,b = (255,255,255)
		if not self.screen_obj.esquisse.screen_properties.use_interface or not self.screen_obj.esquisse.screen_properties.texture_loaded:
			# Get the screen background of the material color
			if len(self.screen_obj.materials) > 0:
				r,g,b = self.screen_obj.materials[0].diffuse_color*255
			else:
				r,g,b = (124,173,242) # very light blue

		background = self.background_screen_element((r,g,b))

		# if we don't use screen interface, return just the background
		if not self.screen_obj.esquisse.screen_properties.use_interface:
			indent(background)
			return background

		elif self.screen_obj.esquisse.screen_properties.interface_path.endswith('.svg'):
			return self.getScreenSVGElement(background)
		elif self.screen_obj.esquisse.screen_properties.interface_path.endswith('.png'):
			return self.getScreenPNGElement(background)


	def getScreenSVGElement(self, background):

		# Open input file and parse it
		print("External SVG :",self.screen_obj.esquisse.screen_properties.interface_path)
		tree = et.parse(bpy.path.abspath(self.screen_obj.esquisse.screen_properties.interface_path))
		print("File parsed.")

		root = tree.getroot()
		print(root)
		root.tag = 'g' # Replace svg to only have one svg 
		view_box_str = root.get('viewBox')
		if view_box_str is not None:
			view_box = re.split(',| ',view_box_str)
			self.initTransformMatrix(float(view_box[0]),float(view_box[1]),float(view_box[2]),float(view_box[3]))
			del root.attrib['viewBox']

		SVG_namespace = "http://www.w3.org/2000/svg"

		for element in root.iter():
			if element.tag == '{%s}path' % SVG_namespace:
				raw_path = element.get('d')
				projected_path = self.project_path(raw_path)
				element.set('d', projected_path)
			elif element.tag == '{%s}polygon' % SVG_namespace:
				points = element.get('points')
				projected_polygon = self.project_polygon(points)
				element.set('points', projected_polygon)
			elif element.tag == '{%s}rect'%SVG_namespace:
				self.rect_to_polygon(element)

			elif element.tag in [	'{%s}circle'% SVG_namespace,
									'{%s}ellipse'% SVG_namespace,
									'{%s}line'% SVG_namespace,
									'{%s}polyline'% SVG_namespace]:
				element.clear()

		root.insert(0, background)

		indent(root)
		return root

	def getScreenPNGElement(self,background):

		a = self.transformPoint(Vector((0,0,1)))
		b = self.transformPoint(Vector((1,0,1)))
		c = self.transformPoint(Vector((1,1,1)))
		d = self.transformPoint(Vector((0,1,1)))

		img = cv2.imread(bpy.path.abspath(self.screen_obj.esquisse.screen_properties.interface_path),cv2.IMREAD_UNCHANGED)
		h,w,ch = img.shape

		pts_origin = np.float32([[0,0],[w,0],[w,h],[0,h]])
		pts_destination = np.float32([[a.x,a.y],[b.x,b.y],[c.x,c.y],[d.x,d.y]])

		M = cv2.getPerspectiveTransform(pts_origin,pts_destination)

		max_x = 0
		max_y = 0
		min_x = 9999999
		min_y = 9999999
		for pt in pts_destination:
			if pt[0] > max_x:
				max_x = pt[0]
			if pt[0] < min_x:
				min_x = pt[0]
			if pt[1] > max_y:
				max_y = pt[1]
			if pt[1] < min_y:
				min_y = pt[1]

		perspective_img = cv2.warpPerspective(img,M,(max_x,max_y))[int(min_y):int(max_y), int(min_x):int(max_x)]

		#perspective_img = cv2.flip(perspective_img, 0)
		cv2.imwrite("/tmp/img_esquisse_tmp.png",perspective_img)


		image_file = open("/tmp/img_esquisse_tmp.png", "rb")
		encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

		# H = renderData.render_height

		element =  et.Element('image',
			{
				'id' : 'interface',
				'x' : str(min_x),
				'y' : str(min_y),
				'width' : str(max_x-min_x),
				'height' : str(max_y-min_y),
				'xlink:href' : 'data:image/png;base64,'+encoded_string,

			})

		image_file.close()

		return element


	def rect_to_polygon(self, rect_element):
		x=0
		y=0
		w=0
		h=0

		keep_attrib = {}
		for key, value in rect_element.attrib.items():
			if key == 'x':
				x= float(value)
			elif key == 'y':
				y = float(value)
			elif key == 'height':
				h = float(value)
			elif key=='width':
				w = float(value)
			else:
				keep_attrib[key] = value

		rect_element.tag = 'polygon'
		rect_element.clear()
		for key, value in keep_attrib.items():
			rect_element.set(key, value)

		p1 = self.transformPoint(Vector((x,y,1))) 
		p2 = self.transformPoint(Vector((x+w,y,1))) 
		p3 = self.transformPoint(Vector((x+w,y+h,1))) 
		p4 = self.transformPoint(Vector((x,y+h,1))) 

		points = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f "%(p1.x,p1.y,p2.x,p2.y,p3.x,p3.y,p4.x,p4.y)

		rect_element.set('points', points)

		return rect_element




	def project_polygon(self, points_str):
		# Convert to path because it is already coded

		new_points_str = ""
		points = points_str.split()
		for p in points:
			s = p.split(",")
			x = float(s[0])
			y = float(s[1])

			projected_p = self.transformPoint(Vector((x,y,1)))

			new_points_str += "%.1f,%.1f "%(projected_p.x,projected_p.y)
		return new_points_str




	def background_screen_element(self,color):
		self.initTransformMatrix()
		a = self.transformPoint(Vector((0,0,1)))
		b = self.transformPoint(Vector((1,0,1)))
		c = self.transformPoint(Vector((1,1,1)))
		d = self.transformPoint(Vector((0,1,1)))

		return et.Element('path', {'fill':'rgb(%d,%d,%d)'%color, 'd':'M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z'%(a.x,a.y,b.x,b.y,c.x,c.y,d.x,d.y)})


	def project_path(self, str_path):


		# Parsed path is a mutable sequence of segment paths of type Line, Arc, Besiez or QuadraticBezier
		path = parse_path(str_path)
		new_path = Path()


		for i in range(0, len(path)):
			segment = path[i]

			if isinstance(segment, Line):
				segment.start = self.transformComplexPoint(segment.start)
				segment.end = self.transformComplexPoint(segment.end)
				new_path.append(segment)

			elif isinstance(segment, CubicBezier):
				segment.start = self.transformComplexPoint(segment.start)
				segment.control1 = self.transformComplexPoint(segment.control1)
				segment.control2 = self.transformComplexPoint(segment.control2)
				segment.end = self.transformComplexPoint(segment.end)
				new_path.append(segment)

			elif isinstance(segment, QuadraticBezier):
				segment.start = self.transformComplexPoint(segment.start)
				segment.control = self.transformComplexPoint(segment.control)
				segment.end = self.transformComplexPoint(segment.end)
				new_path.append(segment)
			else:
				n_cuts = 10
				step = 1.0/n_cuts
				for i in range(0,n_cuts):
					pos1 = step*i
					pos2 = step*(i+1)
					new_path.append(Line(self.transformComplexPoint(segment.point(pos1)), self.transformComplexPoint(segment.point(pos2))))

		if len(path) == 0:
			return ""

		return new_path.d()


	def transformComplexPoint(self, p):
		out_p = self.transformPoint(Vector((p.real, p.imag, 1)))
		return complex(out_p.x,out_p.y)



	def transformPoint(self,point):
		p = self.transform_matrix*point
		return p/p.z

	def initTransformMatrix(self, svg_x = 0, svg_y = 0, svg_w = 1, svg_h = 1):

		# bot_left = convertWorld3DPointTo2DScreenPoint(self.screen_obj.matrix_world * (self.screen_obj.vertices[0].co))
		# bot_right = convertWorld3DPointTo2DScreenPoint(self.screen_obj.matrix_world * (self.screen_obj.vertices[1].co))
		# top_left = convertWorld3DPointTo2DScreenPoint(self.screen_obj.matrix_world * (self.screen_obj.vertices[2].co))
		# top_right = convertWorld3DPointTo2DScreenPoint(self.screen_obj.matrix_world * (self.screen_obj.data.vertices[3].co))

		bot_left = self.screen_obj.vertices[0].planeProjectionLocation
		bot_right = self.screen_obj.vertices[1].planeProjectionLocation
		top_left = self.screen_obj.vertices[2].planeProjectionLocation
		top_right = self.screen_obj.vertices[3].planeProjectionLocation

		x1,y1 = svg_x, 			svg_y+svg_h
		x2,y2 = svg_x+svg_w, 	svg_y+svg_h
		x3,y3 = svg_x+svg_w, 	svg_y
		x4,y4 = svg_x, 			svg_y

		H = renderData.render_height
		u1,v1 = bot_left.x,	H-bot_left.y
		u2,v2 = bot_right.x,H-bot_right.y
		u3,v3 = top_right.x,H-top_right.y
		u4,v4 = top_left.x,	H-top_left.y

		self.computeTransformMatrix(x1,y1,x2,y2,x3,y3,x4,y4,u1,v1,u2,v2,u3,v3,u4,v4) 


	def computeTransformMatrix(self, x0, y0, x1, y1, x2, y2, x3, y3, u0, v0, u1, v1, u2, v2, u3, v3):
		a = [
			[x0, y0, 1, 0, 0, 0, -u0*x0, -u0*y0],
			[0, 0, 0, x0, y0, 1, -v0*x0, -v0*y0],
			[x1, y1, 1, 0, 0, 0, -u1*x1, -u1*y1],
			[0, 0, 0, x1, y1, 1, -v1*x1, -v1*y1],
			[x2, y2, 1, 0, 0, 0, -u2*x2, -u2*y2],
			[0, 0, 0, x2, y2, 1, -v2*x2, -v2*y2],
			[x3, y3, 1, 0, 0, 0, -u3*x3, -u3*y3],
			[0, 0, 0, x3, y3, 1, -v3*x3, -v3*y3]
			]
		b = [[u0],[v0],[u1],[v1],[u2],[v2],[u3],[v3]]
		m = np.linalg.solve(a, b)
		
		self.transform_matrix[0].xyz = m.item(0),m.item(1),m.item(2)
		self.transform_matrix[1].xyz = m.item(3),m.item(4),m.item(5)
		self.transform_matrix[2].xyz = m.item(6),m.item(7),1








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










