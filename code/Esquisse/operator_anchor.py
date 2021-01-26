# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
from bpy_extras import view3d_utils
import bgl
import math
from mathutils import Vector, Matrix
from bpy.app.handlers import persistent
from .FunctionsUtils import *


modal_operator_running = False

class EsquisseAddAnchorOperator(bpy.types.Operator):

	bl_idname = "esquisse.add_anchor"
	bl_label = "Esquisse Anchors Operator"
	bl_description = "Entering in anchor mode. Left Mouse button to attach an anchor to a screen object. [ESC to quit]"

	def __init__(self):
		self.mouse_infos = None

	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	@staticmethod
	def preview_contact_points_3DView(self, context):

		if not self.mouse_infos:
			return

		# Draw contact point under the mouse coor
		touched_screen, local_pos, local_normal = self.mouse_infos

		if touched_screen:
			bgl.glEnable(bgl.GL_DEPTH_TEST)
			bgl.glEnable(bgl.GL_BLEND)

			bgl.glColor4f(1,0,0,0.5)

			delta_normal = 0.03
			center = touched_screen.matrix_world * (local_pos)

			world_normal = localDirectionToWorldDirection(touched_screen, local_normal)

			center += delta_normal * world_normal
			
			n = 15
			points = getCircleArountCenterAndDirection(center, world_normal, 0.1, n)



			for i in range(0,len(points)):
				bgl.glBegin(bgl.GL_TRIANGLES)

				bgl.glVertex3f(center.x, center.y, center.z)
				bgl.glVertex3f(points[i].x,points[i].y,points[i].z)
				bgl.glVertex3f(points[i-1].x,points[i-1].y,points[i-1].z)

				bgl.glEnd()

			bgl.glDisable(bgl.GL_DEPTH_TEST)
			bgl.glDisable(bgl.GL_BLEND)


	def getScreenUnderMouse(self, context, event):
		# get the context arguments
		scene = context.scene
		region = context.region
		rv3d = context.region_data
		coord = event.mouse_region_x, event.mouse_region_y

		# get the ray from the viewport and mouse
		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
		ray_target = ray_origin + view_vector

		closest_touched_screen = None
		closest_touched_screen_dist = -1
		touched_local_pos = None
		touched_local_normal = None
		for obj in context.scene.objects:
			# if obj.esquisse.isScreen:
			if obj.type == 'MESH':
				matrix_world_obj = obj.matrix_world.inverted()
				ray_target_obj = matrix_world_obj*ray_target
				ray_origin_obj = matrix_world_obj*ray_origin
				touched, location, normal, _ = obj.ray_cast(ray_origin_obj, ray_target_obj - ray_origin_obj)
				if touched:
					hit_world = obj.matrix_world * location
					dist = (hit_world - ray_origin).length_squared
					if closest_touched_screen is None or dist < closest_touched_screen_dist:
						closest_touched_screen_dist = dist
						closest_touched_screen = obj
						touched_local_pos = location
						touched_local_normal = normal

		return (closest_touched_screen, touched_local_pos, touched_local_normal)


	def add_contact_point(self):

		if not self.mouse_infos:
			return

		delta_obj = 0.02
		delta_mesh = 0.003

		touched_screen, local_pos, local_normal = self.mouse_infos

		# parent = touched_screen
		# while parent is not None:
		# 	bpy.context.scene.objects.active = parent
		# 	touched_screen.select = True
		# 	bpy.ops.object.transform_apply(scale = True)
		# 	parent = parent.parent
		# bpy.context.scene.update()

		# Create a circle
		bpy.ops.mesh.primitive_circle_add(vertices=32, radius=0.1, fill_type='NGON')


		# Get a ref to the circle object
		anchor = bpy.context.scene.objects.active
		bpy.ops.object.mode_set(mode = 'EDIT')
		bpy.ops.transform.translate(value=(0,0,-(delta_obj-delta_mesh)), constraint_axis=(False,False,True), constraint_orientation='GLOBAL')
		bpy.ops.object.mode_set(mode = 'OBJECT')

		# Define the object as an Esquisse Screen Anchor
		anchor.esquisse.isAnchor = True
		anchor.esquisse.anchor_properties.screen = touched_screen
		anchor.esquisse.anchor_properties.anchor = anchor

		# Set the screen as the parent of the object (Local space is then the screen space)
		anchor.parent = touched_screen
		anchor.name = 'anchor'

		#local_pos = Vector((local_pos.x*touched_screen.scale.x, local_pos.y*touched_screen.scale.y, local_pos.z*touched_screen.scale.z))
	
		# rotation_matrix = touched_screen.matrix_world.to_3x3()* Vector((0,0,1)).rotation_difference(local_normal).to_matrix()
		# translation_matrix = Matrix.Translation(touched_screen.matrix_world*(local_pos + delta_obj*local_normal.normalized()))
		# anchor.matrix_local = touched_screen.matrix_world.inverted()* translation_matrix * rotation_matrix.to_4x4()

		rotation_matrix = touched_screen.matrix_world.to_3x3()* Vector((0,0,1)).rotation_difference(local_normal).to_matrix()
		world_normal = localDirectionToWorldDirection(touched_screen, local_normal)
		world_pos = touched_screen.matrix_world*local_pos
		translation_matrix = Matrix.Translation(world_pos + delta_obj*world_normal)
		anchor.matrix_world = translation_matrix * rotation_matrix.to_4x4()


		anchor.lock_scale = (True,True,True) 
		anchor.lock_rotation = (True,True,True)

		# Constraint anchor scale in world space
		constraint = anchor.constraints.new('LIMIT_SCALE')
		constraint.use_min_x = True
		constraint.min_x = 1
		constraint.use_max_x = True
		constraint.max_x = 1

		constraint.use_min_y = True
		constraint.min_y = 1
		constraint.use_max_y = True
		constraint.max_y = 1

		constraint.use_min_z = True
		constraint.min_z = 1
		constraint.use_max_z = True
		constraint.max_z = 1
		
		constraint.use_transform_limit = True
		constraint.owner_space = 'WORLD'

	
		# Add a new material to the object
		if len(anchor.data.materials) == 0:		
			material = bpy.data.materials.new(name="AnchorColor")
		else:
			material = anchor.data.materials[0]
		material.diffuse_color = (1,0,0)
		material.diffuse_intensity = 1

		# Chnage the manipulator to LOCAL:
		views = [area.spaces.active for area in  bpy.context.screen.areas if area.type == 'VIEW_3D']
		for view in views:
			view.transform_orientation = 'LOCAL'


	def modal(self, context, event):
		if event.type == 'ESC':
			self.stopOperator(context)
			return {'CANCELLED'}

		elif event.type in ['MOUSEMOVE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE']:
			self.mouse_infos = self.getScreenUnderMouse(context, event)
			bpy.context.area.tag_redraw()

		elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
			self.mouse_infos = self.getScreenUnderMouse(context, event)

			touched_screen, _, _ = self.mouse_infos
			if touched_screen:
				self.add_contact_point()

			self.stopOperator(context)
			return {'FINISHED'}


		return {'PASS_THROUGH'}

	def execute(self, context):
		global modal_operator_running
		if modal_operator_running:
			print("You are already in contact point mode")
			return{'CANCELLED'}

		print("Anchors mode enabled")
		modal_operator_running = True
		context.window_manager.modal_handler_add(self)

		self.preview_handler = bpy.types.SpaceView3D.draw_handler_add(self.preview_contact_points_3DView, (self, context), 'WINDOW', 'PRE_VIEW')

		return {'RUNNING_MODAL'}

	def stopOperator(self,context):
		print("Anchors mode disabled")
		
		context.area.tag_redraw()
		global modal_operator_running
		modal_operator_running = False


		if self.preview_handler is not None:
			bpy.types.SpaceView3D.draw_handler_remove(self.preview_handler, 'WINDOW')

		self.preview_handler = None



class EsquisseRemoveAnchorOperator(bpy.types.Operator):

	bl_idname = "esquisse.remove_anchor"
	bl_label = "Esquisse Remove Anchors Operator"
	bl_description = "Click to delete the anchor"

	anchor_name = bpy.props.StringProperty()


	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	def execute(self, context):
		print("Removing anchor")

		anchor = context.scene.objects[self.anchor_name]

		if anchor.esquisse.anchor_properties.constrained_object:
			bpy.ops.esquisse.apply_constraints_to_pose(obj_name = anchor.esquisse.anchor_properties.constrained_object.name)

		context.scene.objects.unlink(anchor)
		bpy.data.objects.remove(anchor,True)
		context.scene.update()

		return {'FINISHED'}









