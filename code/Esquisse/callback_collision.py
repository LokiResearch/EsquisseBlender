# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md



#================================================

import bpy
import bmesh
from bpy.app.handlers import persistent
from mathutils.bvhtree import BVHTree
from Esquisse.cgal import mycgal as mycgal

#================================================

saved_states = dict()
saved_armature = dict()

#================================================

@persistent
def on_object_update(scene):
	"""
	Callback on change in the scene
	:param scene: scene context
	:return:
	"""

	# If in rendering or if the direct collision mode is not enabled
	if bpy.context.scene.esquisse.is_rendering or bpy.context.scene.esquisse.direct_collision_enable is False:
		return

	# If in pose mode : check if we are moving a bone
	if bpy.context.mode == 'POSE':
		obj = scene.objects.active
		_detect_bone_pose_change_action(obj, scene)

		if obj.is_updated == True:
			print("POSE MODE !", obj)

	# If in object mode : check if we are moving an armature or an object
	elif bpy.context.mode == 'OBJECT':
		obj = scene.objects.active
		if not obj:
			return
		elif obj.is_updated == True:

			if obj.type == 'MESH':
				_process_collision_for_mesh(obj, scene)
			elif obj.type == 'ARMATURE':
				_process_collision_for_armature(obj, scene)
			else:
				print("OTHER : ", obj.type)

#================================================

def _process_collision_for_mesh(obj1, scene):
	"""
	Check collision for a moved mesh with everything else
	:param obj1: current object
	:param scene: scene context
	:return:
	"""

	global saved_states

	# Creation of the bmesh for the object
	bmesh1 = bmesh.new()
	bmesh1.from_mesh(obj1.data)
	bmesh1.transform(obj1.matrix_world)

	# Create the BVH Tree of the bmesh
	tree1 = BVHTree.FromBMesh(bmesh1)

	# For each object which is a mesh in the scene
	for obj2 in scene.objects:
		if obj2.type == 'MESH' and obj1 != obj2:

			# Get the deformed mesh by the armature if it exist and create a bmesh
			mesh2_apply = obj2.to_mesh(bpy.context.scene, True, 'RENDER')
			bmesh2 = bmesh.new()
			bmesh2.from_mesh(mesh2_apply)
			bmesh2.transform(obj2.matrix_world)

			# Create the BVH Tree of the bmesh
			tree2 = BVHTree.FromBMesh(bmesh2)

			# Process the overlap of the two BVH Tree
			intersect = tree1.overlap(tree2)

			# Delete the mesh to prevent memory leak / mesh list flood
			bmesh.ops.delete(bmesh2)
			bpy.data.meshes.remove(mesh2_apply)

			# If intersections found rollback the object to his previous position/rotation/scale
			if len(intersect) != 0:

				print("ROLLBACK :", obj1, "to :", saved_states[obj1][0])
				obj1.location = saved_states[obj1][0]
				obj1.rotation_euler = saved_states[obj1][1]
				obj1.scale = saved_states[obj1][2]

				# Apply the rollback to the childs objects
				_apply_states_to_childs(obj1)

				# Delete the mesh to prevent memory leak / mesh list flood
				bmesh.ops.delete(bmesh1)

				return

	# Else : save the state (position/rotation/scale)
	state = (obj1.location.copy(), obj1.rotation_euler.copy(), obj1.scale.copy())
	saved_states[obj1] = state

	_save_states_of_childs(obj1)

	# Delete the bmesh to prevent memory leak / mesh list flood
	bmesh.ops.delete(bmesh1)

#================================================

def _detect_bone_pose_change_action(obj1, scene):
	"""
	Verify if a bone has been changed and process the collision
	:param obj1: current object which is an armature
	:param scene: scene context
	:return:
	"""

	# Get the active bone
	# PROBLEME : Pour les sliders ceci peut poser problème à tenir compte !!
	bone = bpy.context.scene.objects.active.data.bones.active

	# Get the indication if the bone has changed or not
	state = _has_bone_changed(obj1, bone)

	# If state == - the bone is not registered
	if state == -1:
		_save_armature_state(obj1)
	# If state == True there is a change, we have to check the collision
	elif state is True:
		_process_collision_for_bone_pose(obj1, bone, scene)

#================================================

def _process_collision_for_bone_pose(obj1, bone, scene):
	"""
	Check collision for a moved bone with everything else
	:param obj1: current object which is an armature
	:param bone: the moved bone
	:param scene: scene context
	:return:
	"""

	global saved_states
	global saved_armature

	# Get childs of the armature
	childs = _get_childs(obj1)
	if len(childs) == 0:
		return

	# Get the deformed mesh by the armature if it exist and create a bmesh
	mesh1_apply = childs[0].to_mesh(bpy.context.scene, True, 'RENDER')
	bmesh1 = bmesh.new()
	bmesh1.from_mesh(mesh1_apply)
	bmesh1.transform(childs[0].matrix_world)

	# Create the BVH Tree of the bmesh
	tree1 = BVHTree.FromBMesh(bmesh1)

	for obj2 in scene.objects:
		if obj2.type == 'MESH' and childs[0] != obj2:

			# Get the deformed mesh by the armature if it exist and create a bmesh
			mesh2_apply = obj2.to_mesh(bpy.context.scene, True, 'RENDER')

			bmesh2 = bmesh.new()
			bmesh2.from_mesh(mesh2_apply)
			bmesh2.transform(obj2.matrix_world)

			# Create the BVH Tree of the bmesh
			tree2 = BVHTree.FromBMesh(bmesh2)

			# Process the overlap of the two BVH Tree
			intersect = tree1.overlap(tree2)

			# Delete the bmesh to prevent memory leak / mesh list flood
			bmesh.ops.delete(bmesh2)
			bpy.data.meshes.remove(mesh2_apply)

			if len(intersect) != 0:

				obj1.pose.bones[bone.name].matrix = saved_armature[obj1.name][bone.name]

				# APPLICATION RECURSIF A METTRE EN PLACE !!!!!!!!!!!!!!!!!

				# Delete the bmesh to prevent memory leak / mesh list flood
				bmesh.ops.delete(bmesh1)
				bpy.data.meshes.remove(mesh1_apply)

				return

	# Save the state of the armature
	_save_armature_state(obj1)

	# Delete the bmesh to prevent memory leak / mesh list flood
	bmesh.ops.delete(bmesh1)
	bpy.data.meshes.remove(mesh1_apply)

#================================================

def _process_collision_for_armature(obj1, scene):
	global saved_states

	childs = _get_childs(obj1)
	if len(childs) == 0:
		return

	# Get the deformed mesh by the armature if it exist and create a bmesh
	mesh1_apply = childs[0].to_mesh(bpy.context.scene, True, 'RENDER')

	bmesh1 = bmesh.new()
	bmesh1.from_mesh(mesh1_apply)
	bmesh1.transform(childs[0].matrix_world)

	# Process the overlap of the two BVH Tree
	tree1 = BVHTree.FromBMesh(bmesh1)

	for obj2 in scene.objects:
		if obj2.type == 'MESH' and childs[0] != obj2:

			# Get the deformed mesh by the armature if it exist and create a bmesh
			mesh2_apply = obj2.to_mesh(bpy.context.scene, True, 'RENDER')

			bmesh2 = bmesh.new()
			bmesh2.from_mesh(mesh2_apply)
			bmesh2.transform(obj2.matrix_world)

			# Process the overlap of the two BVH Tree
			tree2 = BVHTree.FromBMesh(bmesh2)

			# Process the overlap of the two BVH Tree
			intersect = tree1.overlap(tree2)

			# Delete the bmesh to prevent memory leak / mesh list flood
			bmesh.ops.delete(bmesh2)
			bpy.data.meshes.remove(mesh2_apply)

			if len(intersect) != 0:

				# Rollback every state (position/rotation/scale)
				obj1.location = saved_states[obj1][0]
				obj1.rotation_euler = saved_states[obj1][1]
				obj1.scale = saved_states[obj1][2]

				#_apply_states_to_childs(obj)
				# APPLICATION RECURSIF A METTRE EN PLACE !!!!!!!!!!!!!!!!!

				# Delete the bmesh to prevent memory leak / mesh list flood
				bmesh.ops.delete(bmesh1)
				bpy.data.meshes.remove(mesh1_apply)

				return

	# Save the state
	state = (obj1.location.copy(), obj1.rotation_euler.copy(), obj1.scale.copy())
	saved_states[obj1] = state

	# Delete the bmesh to prevent memory leak / mesh list flood
	bmesh.ops.delete(bmesh2)
	bpy.data.meshes.remove(mesh2_apply)

	#_save_states_of_childs(obj)


#================================================

def _get_childs(parent):
	"""
	Find childs for a specific object
	:param parent: the parent
	:return: the list of the child
	"""

	childs = []

	for obj in bpy.context.scene.objects:
		if obj.type == 'MESH' and obj.parent == parent:
			childs += [obj]

	return childs

#================================================

def _save_states_of_childs(parent):
	"""
	Save state (position/rotation/scale) for each child of one parent
	:param parent:
	:return:
	"""

	for obj in bpy.context.scene.objects:
		if obj.type == 'MESH' and obj.parent == parent:
			state = (obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy())
			saved_states[obj] = state

#================================================

def _apply_states_to_childs(parent):
	"""
	Apply state (position/rotation/scale) for each child of one parent
	:param parent:
	:return:
	"""

	for obj in bpy.context.scene.objects:
		if obj.type == 'MESH' and obj.parent == parent:
			obj.location = saved_states[obj][0]
			obj.rotation_euler = saved_states[obj][1]
			obj.scale = saved_states[obj][2]

#================================================

def _save_armature_state(armature):
	"""
	Save the armature state (matrix bone)
	:param armature: the selected armature
	:return:
	"""

	global saved_armature

	saved_bones = dict()
	for bone in armature.pose.bones:
		saved_bones[bone.name] = bone.matrix.copy()
	saved_armature[armature.name] = saved_bones

#================================================

def _has_bone_changed(armature, bone):
	"""
	Check if one bone has been changed
	:param armature: the armature
	:param bone: the bone to check
	:return: True if the bone has changed, false else and -1 if the armature is not registered
	"""

	global saved_armature

	if armature.name not in saved_armature.keys():
		return -1

	previous_bone_matrix = saved_armature[armature.name][bone.name]
	current_bone_matrix = armature.pose.bones[bone.name].matrix

	return _has_diff_matrix4x4(previous_bone_matrix, current_bone_matrix)

#================================================

def _has_diff_matrix4x4(matrix1, matrix2):
	"""
	Check if there is a difference between the two matrix
	:param matrix1: matrix 1 (4x4)
	:param matrix2: matrix 2 (4x4)
	:return: True if there is a difference, false else
	"""

	n_col = len(matrix1)
	n_row = len(matrix1[0])

	for col in range(n_col):
		for row in range(n_row):
			if matrix1[col][row] - matrix2[col][row] != 0:
				return True

	return False

#================================================

def register():
	bpy.app.handlers.scene_update_post.append(on_object_update)
	
#================================================

def unregister():
	bpy.app.handlers.scene_update_post.remove(on_object_update)

#================================================
