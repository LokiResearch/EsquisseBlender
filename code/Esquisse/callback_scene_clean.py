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
def actions_on_scene(dummy):
	if bpy.context.scene.esquisse.is_rendering:
		return


	###########
	# CLEAN EMPTY CONSTRAINTS
	###########

	# We want to clean bones constraints where the anchor (the IK constraint target) has been deleted 
	for obj in bpy.context.scene.objects:
		if obj.esquisse.isHand:
			for bone in obj.pose.bones:
				for constraint in bone.constraints:
					if constraint.type == 'IK': # Inverse Kinematics
						if constraint.target and constraint.target.name not in bpy.context.scene.objects.keys():
							bone.constraints.remove(constraint)

	###########
	#	REMOVE ANCHORS WITHOUT SCREEN
	###########

	for obj in bpy.context.scene.objects:
		if obj.esquisse.isAnchor and (not obj.esquisse.anchor_properties.screen or obj.esquisse.anchor_properties.screen.name not in bpy.context.scene.objects.keys()):
			bpy.data.objects.remove(bpy.data.objects[obj.name],True)

	for obj in bpy.context.scene.objects:
		if obj.esquisse.isScreen:
			for child in obj.children:
				if child.esquisse.isAnchor and child.name not in bpy.context.scene.objects.keys():
					bpy.data.objects.remove(bpy.data.objects[child.name],True)


def register():	
	bpy.app.handlers.scene_update_post.append(actions_on_scene)


def unregister():
	bpy.app.handlers.scene_update_post.remove(actions_on_scene)

	



