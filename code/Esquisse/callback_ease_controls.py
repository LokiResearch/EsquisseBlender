# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
from bpy.app.handlers import persistent



@persistent
def ease_controls(scene):
	if bpy.context.scene.esquisse.is_rendering:
		return

	if not scene.esquisse.ease_blender_controls:
		return

	ease_selection(scene)
	ease_manipulation_camera_preview(scene)

	

def ease_manipulation_camera_preview(scene):

	view3d = get_3d_view()
	if view3d:
		view3d.lock_camera = True



def ease_selection(scene):
	selected_obj = scene.objects.active
	
	# In case the selected object was deleted
	if selected_obj is None:
		return

	# Check if the selected object if a mesh of an armature
	# If it is, change the selection to the armature instead
	parent = selected_obj.parent
	if parent is not None:
		if parent.type == 'ARMATURE':
			selected_obj.select = False
			parent.select = True
			parent.hide = False # In case the armature is hidden, can't be selected, so make it visible
			scene.objects.active = parent

			# Be sure to be in object mode for the armature manipulation
			try:
				bpy.ops.object.mode_set(mode = 'OBJECT')
			except:
				pass

		elif selected_obj.esquisse.isScreen:
			selected_obj.select = False
			parent.select = True
			parent.hide = False
			scene.objects.active = parent

	view3d = get_3d_view()
	if view3d:
		if selected_obj.esquisse.isHand:
			view3d.pivot_point='CURSOR'
			view3d.cursor_location = selected_obj.matrix_world*selected_obj.pose.bones.get('Wrist').tail

		else:
			view3d.pivot_point='ACTIVE_ELEMENT'




def register():
	bpy.app.handlers.scene_update_post.append(ease_controls)


def unregister():

	bpy.app.handlers.scene_update_post.remove(ease_controls)



def area_of_type(type_name):
	for area in bpy.context.screen.areas:
		if area.type == type_name:
			return area
	return None

def get_3d_view():
	area = area_of_type('VIEW_3D')
	if area:
		return area.spaces[0]
	else :
		return None

