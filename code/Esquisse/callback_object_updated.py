import bpy
from bpy.app.handlers import persistent

from . import callback_key_modifiers
from mathutils import Vector, Matrix
from .FunctionsUtils import *

        

last_active_object_updated = None
last_pos = Vector((0,0,0))


def on_hand_update(hand):

		
	global last_active_object_updated
	global last_pos

	if last_active_object_updated == hand:
		if callback_key_modifiers.alt_modifier_pressed:

			# Move attached anchors:
			for obj in bpy.context.scene.objects:
				if obj.esquisse.isAnchor and obj.esquisse.anchor_properties.constrained_object == hand:
					
					anchor_screen = obj.esquisse.anchor_properties.screen
					screen_normal = localDirectionToWorldDirection(anchor_screen,anchor_screen.data.vertices[0].normal)
					screen_loc = obj.esquisse.anchor_properties.screen.matrix_world.to_translation()

					# Compute the projected current location of the hand on the screen
					v =  hand.matrix_world.to_translation() - screen_loc
					p_v = hand.matrix_world.to_translation() - v.dot(screen_normal)*screen_normal
					p_v = obj.matrix_world.inverted() * p_v

					# Compute the projected old location of the hand on the screen
					v_old =  last_pos - screen_loc
					p_v_old = last_pos - v_old.dot(screen_normal)*screen_normal
					p_v_old = obj.matrix_world.inverted() * p_v_old

					# Compute the difference of positions on the projected plane (the screen)
					delta = p_v - p_v_old

					# Taking account the parent scale 
					delta.x /= anchor_screen.scale[0]
					delta.y /= anchor_screen.scale[1]
					delta.z /= anchor_screen.scale[2]

					obj.location += delta
	
	last_pos = hand.matrix_world.to_translation()


def on_anchor_update(anchor):

	##### NOT WOKING 
	#
	#	Changing the scale of the anchor moves the object along the mesh
	######

	global last_active_object_updated
	global last_pos	

	parent = anchor.parent

	if parent is None:
		return

	delta_obj = 0.02
	delta_mesh = 0.01

	result, local_pos, local_normal, index = parent.ray_cast(anchor.location, (anchor.matrix_local*(-anchor.data.polygons[0].normal)).normalized())

	if result:	
		rotation_matrix = (parent.matrix_world.to_3x3()* Vector((0,0,1)).rotation_difference(local_normal).to_matrix()).normalized()
		translation_matrix = Matrix.Translation(parent.matrix_world*(local_pos + delta_obj*local_normal)).normalized()
		#scale_matrix = Matrix.Scale(anchor.scale.x, 4, Vector((1,0,0)))*Matrix.Scale(anchor.scale.y, 4, Vector((0,1,0)))*Matrix.Scale(anchor.scale.z, 4, Vector((0,0,1)))
		anchor.matrix_local = parent.matrix_world.inverted()* translation_matrix * rotation_matrix.to_4x4() 
		#anchor.location = local_pos + delta_obj*local_normal


@persistent
def main_obj_updated(scene):
	if bpy.context.scene.esquisse.is_rendering:
		return


	global last_active_object_updated

	obj = scene.objects.active
	if not obj:
		return
	elif obj.is_updated:

		if obj.esquisse.isHand:
			on_hand_update(obj)
		# elif obj.esquisse.isAnchor:
		# 	on_anchor_update(obj)



	last_active_object_updated = obj






def register():
	bpy.app.handlers.scene_update_post.append(main_obj_updated)


def unregister():

	bpy.app.handlers.scene_update_post.remove(main_obj_updated)


















# old_obj_loc = Vector((0,0,0))
# old_active_obj = None
# def move_hand_depencies(dummy):
# 	global old_obj_loc
# 	global old_active_obj

# 	if bpy.context.scene.objects.active:
# 		obj = bpy.context.scene.objects.active

# 		if obj.esquisse.isHand and alt_modifier_pressed:

# 			if obj != old_active_obj:
# 				old_obj_loc = obj.matrix_world.to_translation()
# 				old_active_obj = obj
# 				return


# 			# Move attached anchors:
# 			for obj2 in bpy.context.scene.objects:
# 				if obj2.esquisse.isAnchor and obj2.esquisse.constrained_hand == obj:
					
# 					screen_normal = localDirectionToWorldDirection(obj2.esquisse.screen_properties,obj2.esquisse.screen_properties.data.vertices[0].normal)
# 					screen_loc = obj2.esquisse.screen_properties.matrix_world.to_translation()

# 					# Compute the projected current location of the hand on the screen
# 					v =  obj.matrix_world.to_translation() - screen_loc
# 					p_v = obj.matrix_world.to_translation() - v.dot(screen_normal)*screen_normal
# 					p_v = obj2.matrix_world.inverted() * p_v

# 					# Compute the projected old location of the hand on the screen
# 					v_old =  old_obj_loc - screen_loc
# 					p_v_old = old_obj_loc - v_old.dot(screen_normal)*screen_normal
# 					p_v_old = obj2.matrix_world.inverted() * p_v_old

# 					# Compute the difference of positions on the projected plane (the screen)
# 					delta = p_v - p_v_old


# 					# Taking account the parent scale 
# 					delta.x /= obj2.esquisse.screen_properties.scale[0]
# 					delta.y /= obj2.esquisse.screen_properties.scale[1]
# 					delta.z /= obj2.esquisse.screen_properties.scale[2]

# 					obj2.location += delta

# 			old_obj_loc = obj.matrix_world.to_translation()
# 			old_active_obj = obj




	# bpy.app.handlers.scene_update_pre.append(move_hand_depencies)


# def unregister():
	# bpy.app.handlers.scene_update_pre.remove(move_hand_depencies)



