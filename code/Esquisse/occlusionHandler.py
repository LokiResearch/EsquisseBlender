# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import gpu
from . import renderData
import bgl

class OcclusionHandler():

	def drawOffscreenBuffer(self, object_handlers):
		"""
			Initializes an Open GL Frame Buffer Object using
			offscreen object from blender and draws parem object in it

			param:
			tacked_object : 

		"""
		self.offscreenBuffer = gpu.offscreen.new(int(renderData.render_width), int(renderData.render_height))


		# Translate mathutils.Matrix to bgl.Buffer for projection matrix
		m = []
		for i in (0,1,2,3):
			for j in (0,1,2,3):
				m.append(renderData.projectionMatrix[j][i])
		self.proj_matrix_buffer = bgl.Buffer(bgl.GL_FLOAT, 16, m)

		# Translate mathutils.Matrix to blg.Buffer for model view matrix
		m = []
		for i in (0,1,2,3):
			for j in (0,1,2,3):
				m.append(renderData.modelViewMatrix[j][i])
		self.model_view_matrix_buffer = bgl.Buffer(bgl.GL_FLOAT, 16, m)

		self.offscreenBuffer.bind()

		# Put both matrices in Open GL stack
		bgl.glMatrixMode(bgl.GL_PROJECTION)
		bgl.glPushMatrix()
		bgl.glLoadMatrixf(self.proj_matrix_buffer)

		bgl.glMatrixMode(bgl.GL_MODELVIEW)
		bgl.glPushMatrix()
		bgl.glLoadMatrixf(self.model_view_matrix_buffer)
		
		# Enable Depth test for drawing
		bgl.glEnable(bgl.GL_DEPTH_TEST)

		# Clean fragments and depth 
		bgl.glClearColor(1,1,1,1)
		bgl.glClear(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_DEPTH_BUFFER_BIT)

		# glPolygonMode (GL_FRONT_AND_BACK, GL_LINES)
		bgl.glEnable (bgl.GL_POLYGON_OFFSET_FILL)
		bgl.glPolygonOffset(1,1)

		# Pick random color to draw (Here only depth matters)
		bgl.glColor4f(1,0,0,0.3)
		bgl.glViewport(0,0,int(renderData.render_width), int(renderData.render_height))

		for obj_handler in object_handlers:
			for face in obj_handler.mesh_object.faces:
				bgl.glBegin(bgl.GL_POLYGON)
				for vertex in face.vertices:
					world_loc = vertex.world_location 
					bgl.glVertex3f(world_loc.x,world_loc.y,world_loc.z)
				bgl.glEnd()

		bgl.glDisable(bgl.GL_DEPTH_TEST)
		bgl.glDisable(bgl.GL_POLYGON_OFFSET_FILL)

		bgl.glMatrixMode(bgl.GL_PROJECTION)
		bgl.glPopMatrix()

		bgl.glMatrixMode(bgl.GL_MODELVIEW)
		bgl.glPopMatrix()

		self.offscreenBuffer.unbind()

	# def send_occlusions_queries_for_edges(self, mesh_object):

	# 	self.edges_for_occlusion_queries = mesh_object.edges



	# 	self.offscreenBuffer.bind()

	# 	glColorMask(False, False, False, False)
	# 	glDepthMask(False)

	# 	glMatrixMode(GL_PROJECTION)
	# 	glPushMatrix()
	# 	glLoadMatrixf(self.proj_matrix_buffer)

	# 	glMatrixMode(GL_MODELVIEW)
	# 	glPushMatrix()
	# 	glLoadMatrixf(self.model_view_matrix_buffer)

	# 	glEnable(GL_DEPTH_TEST)

	# 	glViewport(0,0,int(renderData.render_width), int(renderData.render_height))

	# 	n = len(self.edges_for_occlusion_queries)
	# 	self.occlusion_queries_ids = glGenQueriesARB(n)

	# 	glClearColor(0,1,0,1)
	# 	glLineWidth(5)

	# 	for i in range(0,n):
	# 		edge = self.edges_for_occlusion_queries[i]
	# 		glBeginQueryARB(GL_SAMPLES_PASSED_ARB, self.occlusion_queries_ids[i])
	# 		glBegin(GL_LINES)
	# 		for vertex in edge.vertices:
	# 			world_loc = vertex.world_location + 1*vertex.world_normal.normalized()
	# 			glVertex3f(world_loc.x,world_loc.y,world_loc.z)
	# 		glEnd()
	# 		glEndQuery(GL_SAMPLES_PASSED_ARB)

	# 	glColorMask(True, True, True, True)
	# 	glDepthMask(True)

	# 	glDisable(GL_DEPTH_TEST)

	# 	glMatrixMode(GL_PROJECTION)
	# 	glPopMatrix()

	# 	glMatrixMode(GL_MODELVIEW)
	# 	glPopMatrix()

	# 	self.offscreenBuffer.unbind()

	# def get_occlusions_queries_results_for_edges(self):

	# 	self.offscreenBuffer.bind()

	# 	n = len(self.edges_for_occlusion_queries)

	# 	for i in range(0,n):
	# 		nb_fragments = glGetQueryObjectuivARB(self.occlusion_queries_ids[i], GL_QUERY_RESULT_ARB)
	# 		self.edges_for_occlusion_queries[i].is_occluded = (nb_fragments == 0)

	# 	glDeleteQueriesARB(n, self.occlusion_queries_ids)

	# 	self.offscreenBuffer.unbind()



	# def occlusions_queries_for_edges(self, object_handler):

	# 	self.edges_for_occlusion_queries = object_handler.mesh_object.edges

	# 	self.offscreenBuffer.bind()

	# 	bgl.glColorMask(False, False, False, False)
	# 	bgl.glDepthMask(False)

	# 	bgl.glMatrixMode(bgl.GL_PROJECTION)
	# 	bgl.glPushMatrix()
	# 	bgl.glLoadMatrixf(self.proj_matrix_buffer)

	# 	bgl.glMatrixMode(bgl.GL_MODELVIEW)
	# 	bgl.glPushMatrix()
	# 	bgl.glLoadMatrixf(self.model_view_matrix_buffer)

	# 	bgl.glEnable(bgl.GL_DEPTH_TEST)

	# 	bgl.glViewport(0,0,int(renderData.render_width), int(renderData.render_height))

	# 	n = len(self.edges_for_occlusion_queries)
	# 	mybuffer = bgl.Buffer(bgl.GL_INT, n)
	# 	self.occlusion_queries_ids = bgl.glGenQueries(n, mybuffer)

	# 	bgl.glClearColor(0,1,0,1)
	# 	bgl.glLineWidth(50)

	# 	for i in range(0,n):
	# 		edge = self.edges_for_occlusion_queries[i]
	# 		bgl.glBeginQuery(bgl.GL_SAMPLES_PASSED, mybuffer[i])
	# 		bgl.glBegin(bgl.GL_LINES)
	# 		for vertex in edge.vertices:
	# 			world_loc = vertex.world_location #+ 0.001*edge.world_normal#+ 1*vertex.world_normal.normalized()
	# 			bgl.glVertex3f(world_loc.x,world_loc.y,world_loc.z)
	# 		bgl.glEnd()
	# 		bgl.glEndQuery(bgl.GL_SAMPLES_PASSED)

	# 	bgl.glColorMask(True, True, True, True)
	# 	bgl.glDepthMask(True)

	# 	bgl.glDisable(bgl.GL_DEPTH_TEST)

	# 	bgl.glMatrixMode(bgl.GL_PROJECTION)
	# 	bgl.glPopMatrix()

	# 	bgl.glMatrixMode(bgl.GL_MODELVIEW)
	# 	bgl.glPopMatrix()

	# 	n = len(self.edges_for_occlusion_queries)

	# 	for i in range(0,n):
	# 		result = bgl.Buffer(bgl.GL_INT, 1)
	# 		nb_fragments = bgl.glGetQueryObjectuiv(mybuffer[i], bgl.GL_QUERY_RESULT, result)
	# 		self.edges_for_occlusion_queries[i].is_occluded = result[0] == 0

	# 	bgl.glDeleteQueries(n, mybuffer)

	# 	self.offscreenBuffer.unbind()


	def occlusions_queries_for_edges(self, object_handler):

		faces = []
		for face in object_handler.mesh_object.faces:
			if face.isFrontFace:
				faces.append(face)
			
		self.offscreenBuffer.bind()

		bgl.glColorMask(False, False, False, False)
		bgl.glDepthMask(False)

		bgl.glMatrixMode(bgl.GL_PROJECTION)
		bgl.glPushMatrix()
		bgl.glLoadMatrixf(self.proj_matrix_buffer)

		bgl.glMatrixMode(bgl.GL_MODELVIEW)
		bgl.glPushMatrix()
		bgl.glLoadMatrixf(self.model_view_matrix_buffer)

		bgl.glEnable(bgl.GL_DEPTH_TEST)

		bgl.glViewport(0,0,int(renderData.render_width), int(renderData.render_height))

		n = len(faces)
		mybuffer = bgl.Buffer(bgl.GL_INT, n)
		occlusion_queries_ids = bgl.glGenQueries(n, mybuffer)

		bgl.glClearColor(0,1,0,1)

		bgl.glEnable(bgl.GL_POLYGON_OFFSET_FILL)
		bgl.glPolygonOffset(-1,-1)

		for i in range(0,n):
			face = faces[i]
			bgl.glBeginQuery(bgl.GL_SAMPLES_PASSED, mybuffer[i])
			bgl.glBegin(bgl.GL_POLYGON)
			for vertex in face.vertices:
				world_loc = vertex.world_location 
				bgl.glVertex3f(world_loc.x,world_loc.y,world_loc.z)
			bgl.glEnd()
			bgl.glEndQuery(bgl.GL_SAMPLES_PASSED)

		bgl.glDisable(bgl.GL_POLYGON_OFFSET_FILL)

		bgl.glColorMask(True, True, True, True)
		bgl.glDepthMask(True)

		bgl.glDisable(bgl.GL_DEPTH_TEST)

		bgl.glMatrixMode(bgl.GL_PROJECTION)
		bgl.glPopMatrix()

		bgl.glMatrixMode(bgl.GL_MODELVIEW)
		bgl.glPopMatrix()

		for face in faces:
			for edge in face.edges:
				edge.is_occluded = True

		for i in range(0,n):
			result = bgl.Buffer(bgl.GL_INT, 1)
			nb_fragments = bgl.glGetQueryObjectuiv(mybuffer[i], bgl.GL_QUERY_RESULT, result)
			is_occluded = result[0] == 0
			print(is_occluded)
			face = faces[i]
			for edge in face.edges:
				edge.is_occluded = edge.is_occluded and is_occluded

		bgl.glDeleteQueries(n, mybuffer)

		self.offscreenBuffer.unbind()









