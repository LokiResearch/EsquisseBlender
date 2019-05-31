import bpy
import bmesh
from . import renderData 
from .FunctionsUtils import *
from .occlusionHandler import OcclusionHandler

class MeshObject():

	def __init__ (self, context, blender_obj):

		self.blender_obj = blender_obj

		self.bm = bmesh.new()
		self.bm.from_object(blender_obj, context.scene)
		self.bm.edges.ensure_lookup_table()
		
		self.bm.normal_update()

		self.generateStructure()

		print("%s [F:%d E:%d V:%d]"%(self.name, len(self.faces), len(self.edges), len(self.vertices)))

	@property
	def name(self):
		return self.blender_obj.name

	@property
	def esquisse(self):
		return self.blender_obj.esquisse

	@property
	def materials(self):
		return self.blender_obj.data.materials

	@property
	def color(self):
		if len(self.blender_obj.data.materials) > 0:
			r,g,b = self.blender_obj.data.materials[0].diffuse_color
			return [r,g,b,1]
		return [1,1,1,1] # Black default color

	@property
	def matrix_world(self):
		return self.blender_obj.matrix_world

	@property
	def children(self):
		return self.blender_obj.children

	def generateStructure(self):

		self.faces = []
		self.edges = []
		self.vertices = []


		self.bmface_face_map = {}
		self.bmedge_edge_map = {}
		self.bmvertex_vertex_map = {}


		#####################
		#					#
		#   	FACES	    # 
		#					#
		#####################

		for bmface in self.bm.faces:
			
			face = Face(bmface, self)

			self.bmface_face_map[bmface] = face
			self.faces.append(face)

		#####################
		#					#
		#   	EDGES	    # 
		#					#
		#####################


		for bmedge in self.bm.edges:
			
			edge = Edge(bmedge,self)

			for bmface in bmedge.link_faces:
				face = self.bmface_face_map[bmface]
				edge.faces.append(face)
				face.edges.append(edge)

			self.edges.append(edge)
			self.bmedge_edge_map[bmedge] = edge


		#####################
		#					#
		#      VERTICES	    # 
		#					#
		#####################


		for bmvertex in self.bm.verts:
			vertex = Vertex(bmvertex, self)

			vertex.faces = []
			vertex.edges = []		

			for bmedge in bmvertex.link_edges:
				edge = self.bmedge_edge_map[bmedge]
				vertex.edges.append(edge)
				edge.vertices.append(vertex)

			for bmface in bmvertex.link_faces:
				face = self.bmface_face_map[bmface]
				vertex.faces.append(face)
				face.vertices.append(vertex)

		
			self.vertices.append(vertex)
			self.bmvertex_vertex_map[bmvertex] = vertex

class Face():

	def __init__ (self, bmface, obj):


		self.material_index = bmface.material_index
		self.local_normal = bmface.normal
		self.local_center = bmface.calc_center_median()
		self.world_normal = localDirectionToWorldDirection(obj, bmface.normal)
		self.world_center = localLocationToWorldLocation(obj, self.local_center)
		self.vvDotProduct = viewVectorDotProduct(self.world_center, self.world_normal)
		self.isFrontFace = isFrontFace(self)
		self.vertices = []
		self.edges = []

	@property
	def color(self):
		if len(self._blender_obj.data.materials) > 0:
			r,g,b = self._blender_obj.data.materials[self.material_index].diffuse_color
			return [r,g,b,1]
		return [1,1,1,1]

class Edge():

	def __init__ (self, bmedge, obj):

		self.vertices = []
		self.faces = []
		self.is_boundary = bmedge.is_boundary
		self.is_occluded = False
		self.bmedge = bmedge
		self.obj = obj

	def otherVertex(self,vertex):
		if vertex == self.vertices[0]:
			return self.vertices[1]
		return self.vertices[0]

	@property
	def materialBoundary(self):
		return (len(self.faces) > 1) and (self.faces[0].material_index != self.faces[1].material_index)

	@property
	def occluded(self):
		return self.vertices[0].occluded or self.vertices[1].occluded

	@property
	def betweenFrontAndBackFaces(self):
		if self.is_boundary:
			return False
		return self.faces[0].isFrontFace ^self.faces[1].isFrontFace

	def setFreestyleMark(self, value):
		self.obj.blender_obj.data.edges[self.bmedge.index].use_freestyle_mark = value

	@property
	def world_normal(self):
		if self.is_boundary:
			return self.faces[0].world_normal
		else :
			return (self.faces[0].world_normal + self.faces[1].world_normal).normalized()

class Vertex(): 

	def __init__ (self, bmvertex, obj):

		self.local_normal = bmvertex.normal
		self.local_location = bmvertex.co
		self.world_normal = localDirectionToWorldDirection(obj, bmvertex.normal)
		self.world_location = localLocationToWorldLocation(obj, bmvertex.co)
		# self.link_edges_CCW = []
		# self.link_vertices_CCW = []
		self.faces = []
		self.edges = []
		self.camera_dotProduct = viewVectorDotProduct(self.world_location,self.world_normal)
		self.planeProjectionLocation = convertWorld3DPointTo2DScreenPoint(self.world_location)
		self.is_occluded = False


# import bpy
# from . import renderData 
# from .FunctionsUtils import *
# from .occlusionHandler import OcclusionHandler

# class MeshObject():

# 	def __init__ (self, context, blender_obj):

# 		self.blender_obj = blender_obj


# 		self.generateStructure()

# 		print("%s [F:%d E:%d V:%d]"%(self.name, len(self.faces), len(self.edges), len(self.vertices)))

# 	@property
# 	def name(self):
# 		return self.blender_obj.name

# 	@property
# 	def esquisse(self):
# 		return self.blender_obj.esquisse

# 	@property
# 	def color(self):
# 		if len(self.blender_obj.data.materials) > 0:
# 			r,g,b = self.blender_obj.data.materials[0].diffuse_color
# 			return [r,g,b,1]
# 		return [1,1,1,1] # Black default color

# 	@property
# 	def matrix_world(self):
# 		return self.blender_obj.matrix_world

# 	@property
# 	def children(self):
# 		return self.blender_obj.children

# 	def generateStructure(self):

# 		self.faces = []
# 		self.edges = []
# 		self.vertices = []


# 		self.meshface_face_map = {}
# 		self.meshedge_edge_map = {}
# 		self.meshvertex_vertex_map = {}

		
# 		#####################
# 		#					#
# 		#      VERTICES	    # 
# 		#					#
# 		#####################

# 		for mesh_vertex in self.blender_obj.data.vertices:
# 			vertex = Vertex(mesh_vertex, self)
# 			self.vertices.append(vertex)
# 			self.meshvertex_vertex_map[mesh_vertex] = vertex


# 		#####################
# 		#					#
# 		#   	EDGES	    # 
# 		#					#
# 		#####################

# 		for mesh_edge in self.blender_obj.data.edges:
# 			edge = Edge(mesh_edge, self)
# 			self.edges.append(edge)
# 			self.meshedge_edge_map[mesh_edge] = edge

# 			for mesh_vertex_idx in mesh_edge.vertices:
# 				mesh_vertex = self.blender_obj.data.vertices[mesh_vertex_idx]
# 				vertex = self.meshvertex_vertex_map[mesh_vertex]
# 				edge.vertices.append(vertex)


# 		#####################
# 		#					#
# 		#   	Polygons	# 
# 		#					#
# 		#####################


# 		for poly in self.blender_obj.data.polygons:

# 			face = Face(poly, self)
# 			self.faces.append(face)
# 			self.meshface_face_map[poly] = face

# 			for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
# 				loop = self.blender_obj.data.loops[loop_index]
# 				mesh_vertex = self.blender_obj.data.vertices[loop.vertex_index]
# 				mesh_edge = self.blender_obj.data.edges[loop.edge_index]

# 				vertex = self.meshvertex_vertex_map[mesh_vertex]
# 				edge = self.meshedge_edge_map[mesh_edge]

# 				edge.faces.append(face)
# 				face.edges.append(edge)
# 				face.vertices.append(vertex)


# class Face():

# 	def __init__ (self, poly, obj):


# 		self.material_index = poly.material_index
# 		self.local_normal = poly.normal
# 		self.local_center = poly.center
# 		self.world_normal = localDirectionToWorldDirection(obj, poly.normal)
# 		self.world_center = localLocationToWorldLocation(obj, self.local_center)
# 		self.isFrontFace = isFrontFace(self)
# 		self.vertices = []
# 		self.edges = []

# 	@property
# 	def color(self):
# 		if len(self.blender_obj.data.materials) > 0:
# 			r,g,b = self.blender_obj.data.materials[self.material_index].diffuse_color
# 			return [r,g,b,1]
# 		return [1,1,1,1]

# class Edge():

# 	def __init__ (self, mesh_edge, obj):

# 		self.vertices = []
# 		self.faces = []
# 		self.is_occluded = False
# 		self.mesh_edge = mesh_edge
# 		self.obj = obj

# 	def otherVertex(self,vertex):
# 		if vertex == self.vertices[0]:
# 			return self.vertices[1]
# 		return self.vertices[0]

# 	@property
# 	def materialBoundary(self):
# 		return (len(self.faces) > 1) and (self.faces[0].material_index != self.faces[1].material_index)

# 	@property
# 	def occluded(self):
# 		return self.vertices[0].occluded or self.vertices[1].occluded

# 	@property
# 	def betweenFrontAndBackFaces(self):
# 		print(len(self.faces))
# 		if len(self.faces) < 2:
# 			return False
# 		print(self.faces[0].isFrontFace ^self.faces[1].isFrontFace)
# 		return self.faces[0].isFrontFace ^self.faces[1].isFrontFace

# 	def setFreestyleMark(self, value):
# 		self.mesh_edge.use_freestyle_mark = value

# 	@property
# 	def is_boundary(self):
# 		return len(self.faces) == 1




# class Vertex(): 

# 	def __init__ (self, mesh_vertex, obj):

# 		self.local_normal = mesh_vertex.normal
# 		self.local_location = mesh_vertex.co
# 		self.world_normal = localDirectionToWorldDirection(obj, mesh_vertex.normal)
# 		self.world_location = localLocationToWorldLocation(obj, mesh_vertex.co)
# 		# self.link_edges_CCW = []
# 		# self.link_vertices_CCW = []
# 		self.faces = []
# 		self.edges = []
# 		self.camera_dotProduct = viewVectorDotProduct(self.world_location,self.world_normal)
# 		self.planeProjectionLocation = convertWorld3DPointTo2DScreenPoint(self.world_location)
# 		self.is_occluded = False

































