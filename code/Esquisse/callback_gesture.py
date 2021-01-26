# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md


#================================================
import traceback
import bpy
import bmesh
from bpy.app.handlers import persistent
import mathutils
import math
#================================================

gestures_previous_positions = {}
running = False
path_to_update = None

def distance_equal(v1, v2):
	l = 0.001
	r = v1.x < v2.x + l and v1.x > v2.x - l and v1.y < v2.y + l and v1.y > v2.y - l and v1.z < v2.z + l and v1.z > v2.z - l
	return r

def interact(scene, gesture):
	if gesture.gesture_silent == False:
		gesture.gesture_silent = True
		try:
			length = 0
			last = gesture.gesture_path_object.data.splines[0].bezier_points[0]
			for ctrl_point in gesture.gesture_path_object.data.splines[0].bezier_points[1:]:
				s = ctrl_point.co - last.co
				length += math.sqrt(s.x**2 + s.y**2 + s.z**2)
				last = ctrl_point

			bpy.ops.object.mode_set(mode='OBJECT')
			gesture.gesture_length = length
			gesture.build_gesture()
		except:
			gesture.gesture_silent = False
			traceback.print_exc()
		gesture.gesture_silent = False

@persistent
def on_object_update(scene):
	"""
	Callback on change in the scene
	:param scene: scene context
	:return:
	"""
	global gestures_previous_positions
	global running
	global path_to_update

	if running:
		return

	if path_to_update and bpy.context.active_object.mode == 'OBJECT':
		interact(scene, path_to_update)
		path_to_update = None
	running = True
	for gesture in scene.esquisse.gesture_list:

		#interact(scene, gesture)
		if path_to_update == None and bpy.context.active_object != None and bpy.context.active_object.mode == 'EDIT' and bpy.context.scene.objects.active == gesture.gesture_path_object:
			path_to_update = gesture

		if not scene.esquisse.gesture_auto_update:
			continue
		if gesture.gesture_silent == False:
			source_object = gesture.gesture_source_object
			source_element = gesture.gesture_source_object_element


			if source_object not in gestures_previous_positions.keys():
				gestures_previous_positions[source_object] = {}

			if source_object.type == 'ARMATURE':

				if source_element not in gestures_previous_positions[source_object].keys():
					gestures_previous_positions[source_object][source_element] = {}

			elif "" not in gestures_previous_positions[source_object].keys():
				gestures_previous_positions[source_object][""] = {}

			# Get the screenshots
			screenshots = []
			# Useful to have a python list and not an blender collection with less functions
			for screenshot in scene.esquisse.ghost_screenshots_list:
				screenshots.append(screenshot)

			# Sort the screenshots by their index:
			screenshots.sort(key= lambda x : x.number)

			outdated = False

			for s in screenshots:
				for o in s['ghost_group'].objects: # object
					if o.esquisse.source_object == source_object:
						if source_object.type == 'ARMATURE':
							position = o.location + o.rotation_euler.to_matrix() * o.pose.bones[source_element].tail
							if o not in gestures_previous_positions[source_object][source_element].keys():
								gestures_previous_positions[source_object][source_element][o] = position
								outdated = True
							elif not distance_equal(gestures_previous_positions[source_object][source_element][o], position):
								gestures_previous_positions[source_object][source_element][o] = position
								outdated = True
						else:

							position = o.location + mathutils.Vector((0,0,0))
							if o not in gestures_previous_positions[source_object][""].keys():
								gestures_previous_positions[source_object][""][o] = position
								outdated = True
							elif not distance_equal(gestures_previous_positions[source_object][""][o], position):
								gestures_previous_positions[source_object][""][o] = position
								outdated = True

			o = source_object
			if source_object.type == 'ARMATURE':
				position = o.location + o.rotation_euler.to_matrix() * o.pose.bones[source_element].tail
				if o not in gestures_previous_positions[source_object][source_element].keys():
					gestures_previous_positions[source_object][source_element][o] = position
					outdated = True
				elif not distance_equal(gestures_previous_positions[source_object][source_element][o], position):
					gestures_previous_positions[source_object][source_element][o] = position
					outdated = True
			else:

				position = o.location + mathutils.Vector((0,0,0))
				if o not in gestures_previous_positions[source_object][""].keys():
					gestures_previous_positions[source_object][""][o] = position
					outdated = True
				elif not distance_equal(gestures_previous_positions[source_object][""][o], position):
					gestures_previous_positions[source_object][""][o] = position
					outdated = True



			if outdated:
				if gesture.gesture_visibility == True:
					gesture.gesture_silent = True
					try:
						#if gesture.gesture_path_object.location != (0,0,0) or gesture.gesture_source_object.matrix_world.translation != (0,0,0):
							#gesture.gesture_path_object.location = (0,0,0)
							#gesture.gesture_object.matrix_world.translation = (0,0,0)
							#pass
						gesture.build_curve()
						gesture.build_gesture()
					except:
						gesture.gesture_silent = False
						traceback.print_exc()
					gesture.gesture_silent = False



	running = False
#================================================

def register():
	bpy.app.handlers.scene_update_post.append(on_object_update)

#================================================

def unregister():
	bpy.app.handlers.scene_update_post.remove(on_object_update)

#================================================
