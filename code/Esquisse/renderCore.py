from . import renderData
from .meshObject import MeshObject
from .objectHandler import ObjectHandler
from .svgExporter import SVGExporter
from .occlusionHandler import OcclusionHandler
from Esquisse.cgal.mycgal import *
from  Esquisse.Polygon.cPolygon import *
from bgl import *
import time
import blf
import math
import bpy
import os
import random
from mathutils import Matrix
from mathutils import Vector


class RenderCore():

	def __init__(self, context):
		self.context = context
		self.object_handler = []
		self.rendereringStep = 'INIT'
		renderData.reset()


	def renderStillImage(self):
		print("Starting Esquisse render still image.")

		# Don't select the ghosts object for the still rendering

		objects_to_render = []
		for obj in self.context.scene.objects:
			if not obj.esquisse.isGhost:
				objects_to_render.append(obj)

		# ##### TEST BOOLEAN INTERSECTION #####
		# meshes = []
		# for obj in context.scene.objects:

		# 	if obj.type == 'MESH':
		# 		meshes.append(obj)

		# size = len(meshes)
		# for i in range(0,size-1):
		# 	obj = meshes[i]
		# 	for j in range(i+1,size):
		# 		next_obj = meshes[j]

		# 		obj_copy = obj.copy()
		# 		obj_copy.data = obj.data.copy()
		# 		next_obj_copy = next_obj.copy()
		# 		next_obj_copy.data = next_obj.data.copy()

		# 		print('obj:%s -> next_obj:%s'%(obj.name, next_obj.name))
		# 		# Intersection Boolean modifier
		# 		modifier = obj.modifiers.new("IntersectionBool", 'BOOLEAN')
		# 		modifier.object = next_obj_copy
		# 		modifier.solver = 'BMESH'
		# 		modifier.operation = 'DIFFERENCE'
		# 		modifier.double_threshold = 0.0

				#context.scene.objects.active = obj
				# bpy.ops.object.modifier_apply(modifier="IntersectionBool")

				# modifier = next_obj.modifiers.new("IntersectionBool", 'BOOLEAN')
				# modifier.object = obj_copy
				# modifier.solver = 'BMESH'
				# modifier.operation = 'DIFFERENCE'
				# modifier.double_threshold = 0.0

				#context.scene.objects.active = next_obj
				# bpy.ops.object.modifier_apply(modifier="IntersectionBool")


		##### TEST BOOLEAN INTERSECTION #####

		# Get the lines
		object_handlers = self.render_with_Freestyle(objects_to_render)
		# object_handlers = self.render_with_opengl()

		# Export SVG files
		print("### Creating SVG file ###")
		exp = SVGExporter()
		exp.exportStillImage(self.context, object_handlers)



		####### INTERSECTION TEST #########



		# for obj in self.context.scene.objects:
		# 	# Remove current modifiers
		# 	modifiers_to_remove = []
		# 	for modifier in obj.modifiers:
		# 		if modifier.name == "IntersectionBool":
		# 			modifiers_to_remove.append(modifier)
		# 	for modifier in modifiers_to_remove:
		# 		obj.modifiers.remove(modifier)


		######### INTERSECTION TEST ##########

		print("Finished.")

		return True

	def renderGhostEffectImage(self):

		if self.rendereringStep == 'INIT':
			print("Starting Esquisse Ghost render [using Freestyle].")

			# Get the screenshots
			self.screenshots = []
			# Useful to have a python list and not an blender collection with less functions
			for screenshot in self.context.scene.esquisse.ghost_screenshots_list:
				self.screenshots.append(screenshot)

			# Sort the screenshots by their index:
			self.screenshots.sort(key= lambda x : x.number)

			size = len(self.screenshots)
			print("Found %d screenshots"%size)

			self.currentScreenshotIdx = 0

			self.rendereringStep = 'OBJECTS'

			self.all_scene_objects = []
			for obj in self.context.scene.objects:
				self.all_scene_objects.append(obj)


		elif self.rendereringStep == 'OBJECTS':

			# Hide the ghost objects:
			objects_to_render = []
			for obj in self.context.scene.objects:
				if not obj.esquisse.isGhost:
					objects_to_render.append(obj)

			self.context.scene.update()

			self.object_handlers = self.render_with_Freestyle(objects_to_render)

			if len(self.screenshots) > 0:
				self.rendereringStep = 'GHOSTS'
			else:
				self.rendereringStep = 'SVG'

			
		elif self.rendereringStep == 'GHOSTS':

		
			screenshot = self.screenshots[self.currentScreenshotIdx]

			self.renderGhostScreenshot(screenshot)

			self.currentScreenshotIdx += 1

			if self.currentScreenshotIdx == len(self.screenshots):
				self.rendereringStep = 'SVG'
				for obj in self.all_scene_objects:
					if obj.name not in self.context.scene.objects:
						self.context.scene.objects.link(obj)

			self.context.scene.update()


		elif self.rendereringStep == 'SVG':

			print("### Creating SVG file ###")
			exp = SVGExporter()

			exp.exportGhostEffectImage(self.context, self.object_handlers, self.screenshots)

			print("Finished")
			return True


		return False


	def renderGhostScreenshot(self, screenshot):
		print("### Rendering Screenshot %d ###"%screenshot.number)


		objects_to_render = []
		for obj in self.context.scene.objects:
			if obj.name in screenshot.ghost_group.objects or not obj.esquisse.isGhost:
				objects_to_render.append(obj)

		# Hide the source objects of the ghost_objects (Not the source of the copies which are the ghosts themselves ;))
		for obj in screenshot.ghost_group.objects:
			if obj.esquisse.source_object in objects_to_render:
				objects_to_render.remove(obj.esquisse.source_object)
		
		
		self.context.scene.update()
			
		# Render
		ghost_handlers = self.render_with_Freestyle(objects_to_render)

		# Only add the handlers of the ghosts computed
		for ghost_handler in ghost_handlers:
			if ghost_handler.mesh_object.blender_obj.esquisse.isGhost:
				for object_handler in self.object_handlers:
					if object_handler.mesh_object.blender_obj == ghost_handler.mesh_object.blender_obj.esquisse.source_object:
						object_handler.ghost_handlers[screenshot] = ghost_handler
						break


		if screenshot.use_interpolation:
			# get the next screenshot concerned by the 
			idx = self.screenshots.index(screenshot)
			next_screenshot = None
			if idx < len(self.screenshots)-1:
				next_screenshot = self.screenshots[idx + 1]

			# Create a copie of the object in the screenshot:
			print("Screeenshot objects:")
			for obj in screenshot.ghost_group.objects:
				print("\t",obj)

			interpolated_copies = copy_ghosts(self.context, screenshot.ghost_group.objects, "Interpolation_")

			# Put the copies in the scene and enable their render by freestyle
			for copy in interpolated_copies:
				copy.esquisse.isGhost = True
				copy.hide_render = False
				if copy.name not in self.context.scene.objects:
					self.context.scene.objects.link(copy)


				print("Copy:",copy, "\tsource:",copy.esquisse.source_object, "\tghost source:",copy.esquisse.ghost_source_object)

			self.context.scene.update()

			# Find the tuple copy, source, destination
			interpolation_objects = []

			for copy in interpolated_copies:
				source = copy.esquisse.ghost_source_object # Point to ghost object copied
				destination = source.esquisse.source_object # Point to the real object of the ghost object
				if next_screenshot is not None:
					for obj in next_screenshot.ghost_group.objects:
						if obj.esquisse.source_object == copy.esquisse.source_object:
							destination = obj
							break

				interpolation_objects.append((copy, source, destination))
				objects_to_render.remove(copy.esquisse.ghost_source_object)
				objects_to_render.append(copy)


			# Iterate on the number of interpolation wanted:
			for i in range(1,screenshot.number_of_interpolation+1): 
				step = i * 1/(screenshot.number_of_interpolation+1)

				# Inpolate the objects matrix
				for obj, source, destination in interpolation_objects:
					self.interpolateObjFromSourceToDestinationWithDelta(obj, source, destination, step)
				self.context.scene.update()

				# Render
				interpolation_handlers = self.render_with_Freestyle(objects_to_render)

				# Store the regions of the interpolated objects:
				for interpolation_handler in interpolation_handlers:
					if interpolation_handler.mesh_object.blender_obj.esquisse.isGhost:
						for object_handler in self.object_handlers:
							if object_handler.mesh_object.blender_obj == interpolation_handler.mesh_object.blender_obj.esquisse.source_object:
								object_handler.ghost_handlers[screenshot].ghost_interpolations[i] = interpolation_handler		 	


			# Remove the copies from the scene
			for copy in interpolated_copies:
				if copy.name in self.context.scene.objects:
					self.context.scene.objects.unlink(copy)

			self.context.scene.update()


	def interpolateObjFromSourceToDestinationWithDelta(self, obj, source, destination, delta):

		print("Interpolated object:",obj, "\tsource:",source, "\tdestination:",destination)
		obj.matrix_world = source.matrix_world.lerp(destination.matrix_world, delta)

		# Check if the objects are armatures
		if obj.type == 'ARMATURE' and source.type == 'ARMATURE' and destination.type == 'ARMATURE':
			for bone in obj.pose.bones:
				source_bone = source.pose.bones.get(bone.name)
				destination_bone = destination.pose.bones.get(bone.name)

				bone.matrix_basis = source_bone.matrix_basis.lerp(destination_bone.matrix_basis, delta)


	def initCameraRender(self):

		print("### Init Render Data ###")
		
		renderData.scene = self.context.scene

		### FORCE FULL RENDER ### [Optional]
		self.context.scene.render.resolution_percentage = 100
		###

		scale = self.context.scene.render.resolution_percentage/100.0
		renderData.render_width = self.context.scene.render.resolution_x * scale
		renderData.render_height = self.context.scene.render.resolution_y * scale	

		camera = None
		for obj in renderData.scene.objects:
			if obj.type == 'CAMERA':
				camera = obj
				break

		if camera:
			renderData.camera = camera
			renderData.modelViewMatrix = camera.matrix_world.inverted()
			renderData.projectionMatrix = camera.calc_matrix_camera(
				self.context.scene.render.resolution_x,
				self.context.scene.render.resolution_y,
				self.context.scene.render.pixel_aspect_x,
				self.context.scene.render.pixel_aspect_y)
			renderData.modelViewProjectionMatrix = renderData.projectionMatrix * renderData.modelViewMatrix


	def initObjectHandlers(self, objects_to_render):

		print("### Scaning scene objects ###")

		handled_objects = []
		for obj in self.context.scene.objects:
			handled = 'X'
			if obj.type == 'MESH' and obj in objects_to_render:
				handled_objects.append(obj)
				handled = u'\u2713'

			if obj.type == 'MESH':
				print('[%s] Object: %s \t Type: %s'%(handled,obj.name,obj.type))


		print("### Generate Objects Structure ###")

		object_handlers = []
		for obj in handled_objects:
			# try:
			mesh_obj = MeshObject(self.context, obj)
			object_handler = ObjectHandler(mesh_obj)
			object_handlers.append(object_handler)
			# except:
			# 	print("Error found for object %s, ignoring object"%obj.name)


		# print("### Computing edges occlusions for each mesh object ###")

		# occlusionHandler = OcclusionHandler()
		# occlusionHandler.drawOffscreenBuffer(object_handlers)
		# for obj_handler in object_handlers:
		# 	# occlusionHandler.send_occlusions_queries_for_edges(mesh_obj)
		# 	# occlusionHandler.get_occlusions_queries_results_for_edges()
		# 	occlusionHandler.occlusions_queries_for_edges(obj_handler)

		return object_handlers




	def render_with_opengl(self):

		print("### Init camera settings ###")
		self.initCameraRender()

		print("### Generate objects structure ###")
		object_handlers = self.initObjectHandlers([])


		print("### Getting the visible edges")
		segments = []
		for object_handler in object_handlers:
			for edge in object_handler.mesh_object.edges:
				if (edge.betweenFrontAndBackFaces or edge.is_boundary) and not edge.is_occluded :
					v1 = edge.vertices[0].planeProjectionLocation
					v2 = edge.vertices[1].planeProjectionLocation
					s = Segment(Point(v1.x, v1.y),Point(v2.x,v2.y))
					segments.append(s)

		regions = computeRegions(segments)

		print("### Assigning regions to objects ###")
		self.assignRegions(regions, object_handlers)

		return object_handlers


		print("Finished.")

	def render_with_Freestyle(self, objects_to_render):

		self.context.scene.esquisse.is_rendering = True


		# Remove hide_render objects:
		tmp = []
		for obj in objects_to_render:
			if not obj.hide_render:
				tmp.append(obj)

		objects_to_render = tmp


		print("### Init camera settings ###")
		self.initCameraRender()

		
		print("### Generate objects structure ###")
		object_handlers = self.initObjectHandlers(objects_to_render)

	
		self.context.scene.render.use_freestyle = True

		#change to script mode
		render_layer = self.context.scene.render.layers.active
		render_layer.freestyle_settings.mode = 'SCRIPT'
		render_layer.freestyle_settings.use_view_map_cache = True
		render_layer.freestyle_settings.use_material_boundaries = True
		render_layer.freestyle_settings.crease_angle = 2.44346 # 140° 


		# print("### Mark edges from bmesh structures for Freestyle ###")
		# cpt = 0
		# for mesh_object in mesh_objects:
		# 	for edge in mesh_object.edges:
		# 		take = False

		# 		# Take the edge if it is between front and back faces
		# 		take = take or edge.betweenFrontAndBackFaces

		# 		# take = take or (not edge.is_boundary and 
		# 		# 		(edge.faces[0].isFrontFace or edge.faces[1].isFrontFace) and
		# 		# 		((edge.faces[0].vvDotProduct >= 0.7 and edge.faces[1].vvDotProduct < 0.7) or
		# 		# 		(edge.faces[1].vvDotProduct >= 0.7 and edge.faces[0].vvDotProduct < 0.7)))

		# 		#Take the edge if
		# 		if take:
		# 			cpt += 1
		# 			edge.setFreestyleMark(True)
		# 		else:
		# 			edge.setFreestyleMark(False)
		# print("%d mark edges"%cpt)


		print("### Giving style modules to Freestyle ###")
		# Get the style module
		current_dir = os.path.dirname(os.path.abspath(__file__))	
		visible_strokes_script = bpy.data.texts.load(current_dir+"/Freestyle_visible_lines.py")
		hidden_strokes_script = bpy.data.texts.load(current_dir+"/Freestyle_hidden_lines.py")
		all_strokes_script = bpy.data.texts.load(current_dir+"/Freestyle_all_lines.py")
		# Remove old style modules
		for module in render_layer.freestyle_settings.modules:
			render_layer.freestyle_settings.modules.remove(module)
		
		# Add the new style modules
		freestyle_module = render_layer.freestyle_settings.modules.new()
		freestyle_module.script = visible_strokes_script
		freestyle_module = render_layer.freestyle_settings.modules.new()
		freestyle_module.script = hidden_strokes_script
		freestyle_module = render_layer.freestyle_settings.modules.new()
		freestyle_module.script = all_strokes_script


		objects_to_unlink = []
		for obj in self.context.scene.objects:
			if obj not in objects_to_render:
				objects_to_unlink.append(obj)

		for obj in objects_to_unlink:
			self.context.scene.objects.unlink(obj)

		
		print("### Freestyle rendering ###")
		bpy.ops.render.render()

		print("### Computing cgal regions ###")
		regions = computeRegions(renderData.freestyle_visible_lines)

		print("### Assigning regions to objects ###")
		self.assignRegions(regions, object_handlers)


		for obj in objects_to_unlink:
			self.context.scene.objects.link(obj)

		self.context.scene.update()

		self.context.scene.esquisse.is_rendering = False

		return object_handlers















	def assignRegions(self, regions, object_handlers):

		for region in regions:

			hit_object, hit_polygon = self.ray_cast_region(region)

			for object_handler in object_handlers:
				if hit_object == object_handler.mesh_object.blender_obj:
					color = [1,1,1,0]
					if hit_polygon.material_index >= 0:
						r,g,b = hit_object.data.materials[hit_polygon.material_index].diffuse_color
						color = [r,g,b,1]
					region.color = color
					object_handler.regions.append(region)

	def getPointInsideRegion(self, region):
		# print("Inside in")

		poly = Polygon()
		tuple_contour = []
		# print("Region contour size:",len(region.contour))
		# print("Region contour:", region.contour)
		for i in range(0,len(region.contour)):
			p = region.contour[i]
			# print("Contour p:",p.x,p.y)
			tuple_contour.append((p.x,p.y))
			# print(tuple_contour)
		if len(tuple_contour) >2:
			# print("Bug here")
			poly.addContour(tuple_contour, 0)
			# print("Yep")

		# print("Hole ?")
		for i in range(0,len(region.holes)):
			hole = region.holes[i]
			tuple_contour = []
			for j in range(0,len(hole.contour)):
				p = hole.contour[j]
				tuple_contour.append((p.x, p.y))
			if len(tuple_contour) >2:
				poly.addContour(tuple_contour, 1)
			
		# print("Inside out")
		return poly.sample(random.random)


	def ray_cast_region(self, region):

		# print("color in")

		# get the context arguments
		scene = self.context.scene

		x_region,y_region = self.getPointInsideRegion(region)
		region.point_x = x_region
		region.point_y = y_region

		x_ndc = (2* x_region / renderData.render_width) - 1
		y_ndc = (2* y_region / renderData.render_height) - 1

		# print("### Region Raycasting ###")
		# print("NDC x:%f y:%f"%(x_ndc,y_ndc))

		ray_clip = Vector((x_ndc, y_ndc, -1, 1))
		ray_eye =  renderData.projectionMatrix.inverted() *  ray_clip
		ray_eye = Vector((ray_eye.x, ray_eye.y, -1, 0))

		ray_world = renderData.camera.matrix_world * ray_eye
		ray_world = ray_world.to_3d()
		ray_world = ray_world.normalized()

		best_length_squared = -1.0
		best_obj = None
		best_face_index = None

		for obj in self.context.scene.objects:
			if obj.type == "MESH":

				# get the ray relative to the object
				matrix_inv = obj.matrix_world.inverted()

				ray_origin_obj = (matrix_inv * renderData.camera.location.to_4d()).to_3d()
				ray_direction_obj = (matrix_inv * Vector((ray_world.x, ray_world.y, ray_world.z, 0))).to_3d().normalized()

				# cast the ray
				success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

				if success:

					hit_world = obj.matrix_world * location
					length_squared = (hit_world - renderData.camera.location).length_squared
					# print(obj.name," : ", length_squared)
					if best_obj is None or length_squared < best_length_squared:
						best_length_squared = length_squared
						best_obj = obj
						best_face_index = face_index
		
		# print("color out")
		if best_obj is not None:
			return (best_obj,best_obj.data.polygons[best_face_index])
		return (None,None)




def copy_ghosts(context, objects, prename):

	new_objs_dictionnary = {}
	new_objs = []

	# Duplicate each object in the scene
	for obj in objects:
		if obj.type in ['ARMATURE', 'MESH']:
			
			copy = obj.copy()
			#copy.data = obj.data.copy()
			copy.name = prename + obj.name
			# scene.objects.link(copy)
			# copy.draw_type = 'WIRE'
			copy.esquisse.ghost_source_object = obj
			copy.esquisse.source_object = obj.esquisse.source_object
			new_objs.append(copy)
			new_objs_dictionnary[obj] = copy
	
	for obj in new_objs:
		# ghost_screenshot.ghost_group.objects.link(obj)
		obj.select = False
		obj.esquisse.isGhost = True
		if obj.parent is not None and obj.parent in new_objs_dictionnary.keys():
			mw = obj.matrix_world
			obj.parent = new_objs_dictionnary[obj.parent]
			obj.matrix_world = mw

		# Check the modifiers for armature
		for modifier in obj.modifiers:
			if modifier.type == 'ARMATURE':
				modifier.object = new_objs_dictionnary[modifier.object]

		# Check the anchor targets of the copy bone armature
		if obj.type == 'ARMATURE':
			for bone in obj.pose.bones:
				for constraint in bone.constraints:
					if constraint.type == 'IK' and constraint.target is not None:
						if constraint.target in new_objs_dictionnary.keys():
								constraint.target = new_objs_dictionnary[constraint.target]
	
	return new_objs

def getAnchors(scene, obj):
	anchors = []
	for o in scene.objects:
		if o.esquisse.isAnchor and o.esquisse.anchor_properties.constrained_object == obj:
			anchors.append(o) 
	return anchors


def getChildren(obj):
	objs = []
	if len(obj.children)==0:
		return objs
	
	for child in obj.children:
		if not child.esquisse.isAnchor:
			objs.append(child)
			objs+=getChildren(child)

	return objs

def getParent(obj):
	objs = []
	
	if obj.parent is not None:
		objs.append(obj.parent)
		objs+=getParent(obj.parent)

	return objs

def applyPose(armature):
	# Deselect all objects:
	for obj in bpy.context.scene.objects:
		obj.select = False

	old_active_obj = bpy.context.scene.objects.active
	bpy.context.scene.objects.active = armature 

	# Go in pose mode :
	bpy.ops.object.mode_set(mode='POSE') 

	# Select all bones:
	bpy.ops.pose.select_all(action='SELECT')

	# Apply the visual transform to the pose
	bpy.ops.pose.visual_transform_apply()

	# Go back to object mode :
	bpy.ops.object.mode_set(mode='OBJECT') 

	old_active_obj.select = True
	bpy.context.scene.objects.active = old_active_obj 

	return {'FINISHED'}


