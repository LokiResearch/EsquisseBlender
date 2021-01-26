# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import re
import os
import traceback

from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.props import PointerProperty, FloatVectorProperty, CollectionProperty
from bpy.types import Panel, Operator, AddonPreferences, PropertyGroup, BlendData, Object

from .FunctionsUtils import *
from mathutils import Matrix
from math import radians, cos, sin

#————————————————————————————————    Todos    ——————————————————————————————————
# > Code comments are comming
# + Object manipulation refactor
# + 'Assign' => 'Link / Unlink'
# - Better length approx
# - Better auto
# + UI revamp (Material UI style)
# - Better state conservation
# - Multiple arrows with the same target
# - Update when parent moved
#———————————————————————————————————————————————————————————————————————————————




class Gesture(bpy.types.PropertyGroup):

	def save_ui_state(self):#TODO
		pass
	def set_ui_state(self, mode="OBJECT", selected_objects=None, active_object=None):#TODO
		_mode = None
		if bpy.context.object != None:
			_mode = bpy.context.object.mode
			if _mode != mode:
				bpy.ops.object.mode_set(mode=mode)

	def restore_ui_state(self):#TODO
		pass


	def update_name(self, context):
		if self.gesture_object != None:
			self.gesture_object.name = self.gesture_name+"_obj"
		if self.gesture_path_object != None:
			self.gesture_path_object.name = self.gesture_name

	def link_unlink(self, context):
		if not self.gesture_silent and self.gesture_linkage:
			self.gesture_silent = True
			try:
				#gesture.gesture_path_object.location = (0,0,0)
				#gesture.gesture_object.location = (0,0,0)
				#gesture.gesture_object.location = -(gesture.gesture_object.matrix_world * (0,0,0))
				#print(gesture.gesture_object.matrix_world)
				self.build_curve()
				self.build_gesture()
			except:
				self.gesture_silent = False
				traceback.print_exc()
			self.gesture_silent = False
			#self.offset_arrow(context)#?
			#self.gesture_silent = False
			self.gesture_path_object.select = True

	def hide_show(self, context):
		self.gesture_object.hide = self.gesture_visibility == False
		self.gesture_object.hide_render = self.gesture_object.hide
		self.gesture_path_object.hide = self.gesture_visibility == False
		self.gesture_path_object.hide_render = self.gesture_path_object.hide
		self.gesture_silent = self.gesture_visibility == False
		#if self.gesture_visibility == True:
		#	self.build_curve()
		#	self.build_gesture()

	def rotate_arrow(self, context):
		self.gesture_object.rotation_euler[1] = (self.gesture_rotate*2*math.pi/360)

	def update_arrow(self, context):
		if not self.gesture_silent:
			self.gesture_silent = True
			try:
				self.build_gesture()
			except:
				self.gesture_silent = False
				traceback.print_exc()
			self.gesture_silent = False
			#self.offset_arrow(context)#?
			#self.gesture_silent = False
			self.gesture_path_object.select = True


	def lock_gesture_location(self):
		self.gesture_object.lock_location[0] = True
		self.gesture_object.lock_location[1] = True
		self.gesture_object.lock_location[2] = True
	def unlock_gesture_location(self):
		self.gesture_object.lock_location[0] = False
		self.gesture_object.lock_location[1] = False
		self.gesture_object.lock_location[2] = False

	def offset_arrow(self, context):
		self.set_ui_state()
		bpy.ops.object.select_all(action='DESELECT')
		self.gesture_object.hide_select = False
		context.scene.objects.active = self.gesture_object
		self.gesture_object.select = True
		pos = bpy.context.scene.objects.active.location.y  #data.vertices[-1].co[1]
		end_pos = (-self.gesture_offset) * (self.gesture_length)  / 100
		self.unlock_gesture_location()
		bpy.ops.transform.translate(value=(0, end_pos - pos, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True, use_accurate=False)
		self.lock_gesture_location()
		context.scene.objects.active = self.gesture_path_object
		self.gesture_object.hide_select = True

	gesture_name = StringProperty(update = update_name, description="The name of the gesture")

	gesture_object = PointerProperty(type = bpy.types.Object, description="The actual Object containing the Mesh of the gesture")
	gesture_path_object = PointerProperty(type = bpy.types.Object, description="The actual Object containing the Path of the gesture")

	gesture_source_object = PointerProperty(type = bpy.types.Object, description="The object the gesture describes the movement of")
	gesture_source_object_element = StringProperty(description="The bones name the gesture describes the movement of")

	gesture_length = FloatProperty(description="The length of the gesture")

	gesture_shape_type = EnumProperty(
		items=[
			('FLAT', 'Flat', 'Flat arrow'),
			('CYLINDER', 'Cylinder', 'Round arrow body'),
			('LINE', 'Line', 'Motion line'),
		],
		name="Shape",
		description="Choose the shape of the arrow",
		default = 'FLAT',
		update = update_arrow
	)
	gesture_scale = FloatProperty(default = 1, min = 0, max = 100, name="Scale", update=update_arrow, description="The scale (length) of the gesture from the gestures end")
	gesture_offset = FloatProperty(default = 0, min = -100, max = 100, name="Offset", update=offset_arrow, description="The offset from the gesture to the end of the movement")
	gesture_width = FloatProperty(default = 0.1, min = 0.01, max = 3, step = 0.01, name="Width", update=update_arrow, description="The width of the gesture")
	gesture_rotate = FloatProperty(default = 0, min = 0, max = 360, name="Rotation", update=rotate_arrow, description="The rotation of the gesture")

	gesture_visibility = BoolProperty(default = True, name="", update = hide_show, description="Show or hide the gesture")
	gesture_linkage = BoolProperty(default = True, name="", update = link_unlink, description="Automatically update this gesture")

	gesture_silent = BoolProperty(default = False, name="", description="Avoid any automatically triggered modification of the gesture")







	def build_curve(self):
		if self.gesture_path_object != None and self.gesture_linkage != True:
			return self.gesture_path_object
		# Get the screenshots
		screenshots = []
		# Useful to have a python list and not an blender collection with less functions
		for screenshot in bpy.context.scene.esquisse.ghost_screenshots_list:
			screenshots.append(screenshot)

		# Sort the screenshots by their index:
		screenshots.sort(key= lambda x : x.number)


		length = 0
		last = None
		path = []
		for screenshot in screenshots:
			for o in screenshot['ghost_group'].objects: # object
				if o.esquisse.source_object == self.gesture_source_object:
					if self.gesture_source_object_element != "":
						bone = self.gesture_source_object_element
						path += [o.matrix_world * Vector((0,0,0)) + o.rotation_euler.to_matrix() * o.pose.bones[bone].tail]
						if last == None:
							last = o.pose.bones[bone].tail
						else:
							s = o.pose.bones[bone].tail - last
							length += math.sqrt(s.x**2 + s.y**2 + s.z**2)
							last = o.pose.bones[bone].tail
					else:
						path += [o.matrix_world * Vector((0,0,0))]
						if last == None:
							last = o.location
						else:
							s = o.location - last
							length += math.sqrt(s.x**2 + s.y**2 + s.z**2)
							last = o.location

		o = self.gesture_source_object

		if self.gesture_source_object_element != "":
			bone = self.gesture_source_object_element
			path += [o.matrix_world * Vector((0,0,0)) + o.rotation_euler.to_matrix() * o.pose.bones[bone].tail]
			if last == None:
				last = o.pose.bones[bone].tail
			else:
				s = o.pose.bones[bone].tail - last
				length += math.sqrt(s.x**2 + s.y**2 + s.z**2)
				last = o.pose.bones[bone].tail
		else:
			path += [o.matrix_world * Vector((0,0,0))]
			if last == None:
				last = o.location
			else:
				s = o.location - last
				length += math.sqrt(s.x**2 + s.y**2 + s.z**2)
				last = o.location


		self.gesture_length = length

		self.gesture_path_object.select = True
		bpy.context.scene.objects.active = self.gesture_path_object
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.curve.select_all(action = 'SELECT')
		bpy.ops.curve.delete(type='VERT')
		for pos in path: # position
			bpy.ops.curve.vertex_add(location=pos)
		bpy.ops.object.mode_set(mode='OBJECT')
		return self.gesture_path_object



	def cylinder_arrow_vert_new(self, arrow_bm, width, step_i, step_j, step_size, step_count, circle_count):
		return arrow_bm.verts.new((width * cos(step_j*math.pi*2/circle_count), step_count*step_size-step_i*step_size, width * sin(step_j*math.pi*2/circle_count)))


	def flat_arrow_vert_new(self, arrow_bm, width, step_i, step_size, step_count):
		return arrow_bm.verts.new(((-1*width)+(2*width)*(step_i%2), int(step_count/2)*step_size-int(step_i/2)*step_size, 0))

	def build_gesture(self):
		#global path_to_update#TODO?
		#if self.gesture_object != None and self.gesture_linkage != True:#when path_to_update isn't None
			#return (self.gesture_object, self.gesture_length)
		length = self.gesture_length*self.gesture_scale
		arrow_width = self.gesture_width
		count = int(length/(arrow_width))
		if count % 2 == 1:
			count -= 1
		step_size = length/((count-1)/2)

		self.gesture_object.hide_select = False
		Arrow = self.gesture_object
		ArrowM = Arrow.data
		Arrow.select = True
		bpy.context.scene.objects.active = Arrow
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action = 'SELECT')
		bpy.ops.mesh.delete(type='VERT')
		ArrowBM = bmesh.from_edit_mesh(ArrowM)

		if self.gesture_shape_type == 'FLAT':
			verts = []
			for i in range(count-2):
				verts += [self.flat_arrow_vert_new(ArrowBM, arrow_width, i, step_size, count)]

			arrow_head = []


			for i in range(count-2, count):
				arrow_head += [self.flat_arrow_vert_new(ArrowBM, arrow_width, i, step_size, count)]

			i-=1
			arrow_head += [self.flat_arrow_vert_new(ArrowBM, 2*arrow_width, i, step_size-0.001, count)]
			i+=1
			arrow_head += [self.flat_arrow_vert_new(ArrowBM, 2*arrow_width, i, step_size-0.001, count)]
			i+=1
			arrow_head += [ArrowBM.verts.new((0, int(count/2)*step_size-int(i/2)*step_size, 0))]
			ArrowBM.verts.ensure_lookup_table()

			verts += arrow_head
			for i in range(len(verts)-2):#+5
				ArrowBM.faces.new((verts[i], verts[i+1], verts[i+2]))

		elif self.gesture_shape_type == 'CYLINDER':
			verts = []
			for i in range(int(count/2)):
				vs = []
				for j in range(int((arrow_width*2*math.pi)/0.05)):
					vs += [self.cylinder_arrow_vert_new(ArrowBM, arrow_width, i, j, step_size, int(count/2), int((arrow_width*2*math.pi)/0.05))]
				verts += [vs]
			arrow_tail = [ArrowBM.verts.new((0, int(count/2)*step_size, 0))]

			arrow_head = []


			i = count/2-1
			vs = []
			for j in range(int((arrow_width*2*math.pi)/0.05)):
				vs += [self.cylinder_arrow_vert_new(ArrowBM, arrow_width*2, i, j, step_size, int(count/2), int((arrow_width*2*math.pi)/0.05))]
			verts += [vs]
			arrow_head = [ArrowBM.verts.new((0, 0, 0))]

			ArrowBM.verts.ensure_lookup_table()

			for i in range(len(verts)-1):#+5
				for j in range((len(verts[i])-1)):
					ArrowBM.faces.new((verts[i][j], verts[i][j+1], verts[i+1][j]))
					ArrowBM.faces.new((verts[i][j+1], verts[i+1][j], verts[i+1][j+1]))
				ArrowBM.faces.new((verts[i][-1], verts[i][0], verts[i+1][-1]))
				ArrowBM.faces.new((verts[i][0], verts[i+1][-1], verts[i+1][0]))
			for i in range(len(verts[0])-1):
				ArrowBM.faces.new((verts[0][i], verts[0][i+1], arrow_tail[0]))
			ArrowBM.faces.new((verts[0][-1], verts[0][0], arrow_tail[0]))
			for i in range(len(verts[-1])-1):
				ArrowBM.faces.new((verts[-1][i], verts[-1][i+1], arrow_head[0]))
			ArrowBM.faces.new((verts[-1][-1], verts[-1][0], arrow_head[0]))

			arrow_head += verts[-1]

		elif self.gesture_shape_type == 'LINE':
			verts = []
			for i in range(count+2):
				verts += [self.flat_arrow_vert_new(ArrowBM, arrow_width, i, step_size, count)]

			ArrowBM.verts.ensure_lookup_table()

			for i in range(len(verts)-2):#+5
				ArrowBM.faces.new((verts[i], verts[i+1], verts[i+2]))


		bmesh.update_edit_mesh(Arrow.data)

		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.normals_make_consistent()
		bpy.ops.mesh.select_all(action = 'DESELECT')
		if self.gesture_shape_type != 'LINE':
			for v in arrow_head:
				v.select = True



		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.ops.object.modifier_remove(modifier="Subsurf")
		bpy.ops.object.modifier_remove(modifier="Curve")


		if self.gesture_shape_type != 'CYLINDER':
			bpy.ops.object.modifier_add(type='SOLIDIFY')
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")

		if self.gesture_shape_type != 'LINE':
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.transform.edge_crease(value=0.8)
			bpy.ops.object.mode_set(mode = 'OBJECT')

		bpy.ops.object.modifier_add(type='SUBSURF')
		bpy.context.object.modifiers["Subsurf"].levels = 3
		bpy.ops.object.modifier_add(type='CURVE')
		bpy.context.object.modifiers["Curve"].object = self.gesture_path_object
		bpy.context.object.modifiers["Curve"].deform_axis = 'POS_Y'
		bpy.context.object.active_material.diffuse_color = (1, 0, 0)
		bpy.ops.object.shade_smooth()

		bpy.context.scene.objects.active = self.gesture_path_object
		self.gesture_object.hide_select = True

		return (Arrow,length)
