# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import bmesh
import math
from mathutils import Vector
from .FunctionsGesture import *

#================================================
#   Gesture generation operator
#================================================

class EsquisseGenerateGesturesAutoOperator(bpy.types.Operator):

	bl_idname = "esquisse.generate_gestures_auto"
	bl_label = "Auto"
	bl_description = "Auto generates gesture representations"

	#============================================

	def execute(self, context):
		gm = GestureManipulation()
		done = gm.new_gestures(context, 'AUTO')
		if done:
			self.report({'INFO'}, "gestures have been generated.")
		else:
			self.report({'INFO'}, "No gestures have been generated.")

		return {'FINISHED'}


#================================================
#   Gesture generation operator
#================================================

class EsquisseGenerateGesturesAnchorsOperator(bpy.types.Operator):

	bl_idname = "esquisse.generate_gestures_anchors"
	bl_label = "Anchors"
	bl_description = "Generates gesture representations based on the existing anchors"

	#============================================

	def execute(self, context):
		gm = GestureManipulation()
		done = gm.new_gestures(context, 'ANCHOR')
		if done:
			self.report({'INFO'}, "gestures have been generated.")
		else:
			self.report({'INFO'}, "No gestures have been generated.")
		return {'FINISHED'}

#================================================
#   Gesture generation operator
#================================================

class EsquisseGenerateGestureOperator(bpy.types.Operator):

	bl_idname = "esquisse.generate_gesture"
	bl_label = "Esquisse generate a gesture"
	bl_description = "Generate gestures for the selected moving Objects or bones."

	#============================================

	def execute(self, context):

		gm = GestureManipulation()
		done = gm.new_gestures(context, 'MANUAL')
		if done:
			self.report({'INFO'}, "gestures have been generated.")
		else:
			self.report({'INFO'}, "No object or bone selected.")


		return {'FINISHED'}



class EsquisseDeleteGestureOperator(bpy.types.Operator):
	bl_idname = "esquisse.delete_gesture"
	bl_label = "Esquisse delete the gesture"
	bl_description = "Delete the gesture"

	#============================================

	def execute(self, context):
		g = GestureManipulation()
		g.delete_gesture(context)
		return {'FINISHED'}

class EsquisseAssignToGestureOperator(bpy.types.Operator):
	bl_idname = "esquisse.assign_to_gesture"
	bl_label = "Esquisse assign element to the gesture"
	bl_description = "Assign element to the gesture"

	#============================================

	def execute(self, context):
		gm = GestureManipulation()
		gm.assign_source(context)
		return {'FINISHED'}






class GestureManipulation:
	gesture = None

	ui_state = None

	def __init__(self):
		pass


	def append_to_elements(self, screenshots, so, elements, bone=None):
		path = []
		length = 0
		last = None
		for screenshot in screenshots:
			for o in screenshot['ghost_group'].objects: # object
				if o.esquisse.source_object == so.esquisse.source_object:
					bone_pos = Vector((0,0,0))
					bone_name = ""
					obj = o.location
					if bone != None:
						bone_pos = o.rotation_euler.to_matrix() * o.pose.bones[bone.name].tail
						bone_name = bone.name
						obj = o.pose.bones[bone.name].tail

					path += [o.matrix_world * Vector((0,0,0)) + bone_pos]
					if last == None:
						last = obj
					else:
						s = obj - last
						length += math.sqrt(s.x**2 + s.y**2 + s.z**2)
						last = obj
		elements += [{"object":so.esquisse.source_object, "element":bone_name, "path":path, "length":length}]


	def extract_elements(self, screenshots):
		elements = []
		ets = []

		for screenshot in screenshots:
			for so in screenshot['ghost_group'].objects: # object
				if so.esquisse.source_object not in ets:
					ets += [so.esquisse.source_object]
					if so.esquisse.source_object.type == "ARMATURE":
						for bone in so.pose.bones:
							self.append_to_elements(screenshots, so, elements, bone)
					else:
						self.append_to_elements(screenshots, so, elements)

		return elements

	def lock_gesture(self, gesture):
		gesture.gesture_path_object.lock_location[0] = True
		gesture.gesture_path_object.lock_location[1] = True
		gesture.gesture_path_object.lock_location[2] = True
		gesture.gesture_path_object.lock_rotation[0] = True
		gesture.gesture_path_object.lock_rotation[1] = True
		gesture.gesture_path_object.lock_rotation[2] = True
		gesture.gesture_path_object.lock_scale[0] = True
		gesture.gesture_path_object.lock_scale[1] = True
		gesture.gesture_path_object.lock_scale[2] = True
		gesture.gesture_object.lock_location[0] = True
		gesture.gesture_object.lock_location[1] = True
		gesture.gesture_object.lock_location[2] = True
		gesture.gesture_object.lock_rotation[0] = True
		gesture.gesture_object.lock_rotation[1] = True
		gesture.gesture_object.lock_rotation[2] = True
		gesture.gesture_object.lock_scale[0] = True
		gesture.gesture_object.lock_scale[1] = True
		gesture.gesture_object.lock_scale[2] = True

	def generate_gesture_objects(self, context, object, bone=""):
		#: cancel if object invalid
		if object == None or object.esquisse.isGesture:
			return None

		## New Gesture
		gesture = context.scene.esquisse.gesture_list.add()
		gesture.gesture_silent = True
		gesture.gesture_name = "NewArrow" + str(len(context.scene.esquisse.gesture_list))


		#: assign source objects to the gesture
		if object.esquisse.source_object != None:
			gesture.gesture_source_object = object.esquisse.source_object
		else:
			gesture.gesture_source_object = object
		gesture.gesture_source_object_element = bone

		## New Path
		bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
		gesture.gesture_path_object = bpy.context.scene.objects.active
		gesture.gesture_path_object.esquisse.isGesture = True
		gesture.gesture_path_object.name = gesture.gesture_name
		#: build the curve
		gesture.build_curve()

		## New Object
		ArrowM = bpy.data.meshes.new('ArrowM')
		gesture.gesture_object = bpy.data.objects.new(gesture.gesture_name+"_obj", ArrowM)
		gesture.gesture_object.esquisse.isGesture = True
		bpy.context.scene.objects.link(gesture.gesture_object)
		#: set default values
		gesture.gesture_shape_type = 'FLAT'
		gesture.gesture_width = 0.1
		gesture.gesture_scale = 1
		gesture.gesture_offset = 0
		gesture.gesture_rotate = 0
		# build the object
		gesture.build_gesture()

		context.scene.objects.active = gesture.gesture_path_object
		gesture.gesture_path_object.select = True
		gesture.gesture_object.hide_select = True
		self.lock_gesture(gesture)
		gesture.gesture_silent = False
		return gesture


	def new_gestures(self, context, generation_type):
		if generation_type == 'AUTO':
			save_ui_state()
			set_ui_state()
			# Get the screenshots
			screenshots = get_screenshots(context)
			elements = []
			ets = []

			elements = self.extract_elements(screenshots)

			elements.sort(key= lambda x : x["length"], reverse = True)

			delta = 0.2#(elements[0]["length"] * len(elements[0]["path"]))

			selected = [elements[0]]
			min_length = 0.2#80*selected[0]["length"]/100
			for element in elements:
				if element not in selected and element["length"] > min_length:
					avg = 0
					closest_dev = None
					for s in selected:
						pts_count = min(len(element["path"]),len(s["path"]))
						for point_i in range(pts_count):
							l = s["path"][point_i] - element["path"][point_i]
							avg += l.x**2 + l.y**2 + l.z**2
						avg /= pts_count
					dev = 0
					for s in selected:
						pts_count = min(len(element["path"]),len(s["path"]))
						for point_i in range(pts_count):
							l = (s["path"][point_i] - element["path"][point_i])
							d = l.x**2 + l.y**2 + l.z**2
							dev = (avg - d)**2
						if closest_dev == None or dev < closest_dev:
							closest_dev = dev
					if closest_dev > delta:
						selected += [element]

			ok = True
			gestures = []
			g = None
			for object in selected:
				g = [self.generate_gesture_objects(context, object["object"], object["element"])]
				if g == None:
					ok = False
				else:
					gestures += g

		elif generation_type == 'ANCHOR':
			save_ui_state()
			set_ui_state()
			# Get the screenshots
			screenshots = get_screenshots(context)
			anchors = []

			for screenshot in screenshots:
				for o in screenshot['ghost_group'].objects: # object
					if o.esquisse.source_object.esquisse.isAnchor and o.esquisse.source_object not in anchors:
						anchors += [o.esquisse.source_object]

			ok = True
			gestures = []
			g = None
			for object in anchors:
				g = [self.generate_gesture_objects(context, object)]
				if g == None:
					ok = False
				else:
					gestures += g


		elif generation_type == 'MANUAL':
			if bpy.context.selected_pose_bones != None and len(bpy.context.selected_pose_bones) > 0:
				if bpy.context.scene.objects.active.esquisse.source_object != None:
					object = bpy.context.scene.objects.active.esquisse.source_object
				else:
					object = bpy.context.scene.objects.active

				ok = True
				gestures = []
				g = None
				for bone in bpy.context.selected_pose_bones:
					g = [self.generate_gesture_objects(context, object, bone.name)]
					if g == None:
						ok = False
					else:
						gestures += g
			else:
				objects = []

				for o in bpy.context.scene.objects:
					if o.select:
						objects += [o]

				if len(objects) == 0:
					return False

				ok = True
				gestures = []
				g = None
				for object in objects:
					g = [self.generate_gesture_objects(context, object)]
					if g == None:
						ok = False
					else:
						gestures += g



		return True
		#bpy.ops.object.mode_set(mode=_mode)

	def modify_gesture(self, context):
		pass


	def assign_source(self, context):#TODO Should _replace_ instead of remove & create
		self.delete_gesture(context)
		self.new_gestures(context, 'MANUAL')





	def delete_gesture(self, context):
		if bpy.context.scene.esquisse.gesture_selected >= len(bpy.context.scene.esquisse.gesture_list):
			return
		_mode = None
		if bpy.context.object != None:
			_mode = bpy.context.object.mode
			if _mode != "OBJECT":
				bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action = 'DESELECT')
		if bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_visibility == False:
			bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_visibility = True
		if bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_object != None:
			bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_object.select = True
			bpy.ops.object.delete()
			bpy.data.meshes.remove(bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_object.data)
		if bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_path_object != None:
			bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_path_object.select = True
			bpy.ops.object.delete()
			bpy.data.curves.remove(bpy.context.scene.esquisse.gesture_list[bpy.context.scene.esquisse.gesture_selected].gesture_path_object.data)
		bpy.context.scene.esquisse.gesture_list.remove(bpy.context.scene.esquisse.gesture_selected)
