# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy

from mathutils import Matrix

class EsquisseResetPose(bpy.types.Operator):

	bl_idname = "esquisse.reset_pose_operator"
	bl_label = "Reset Hand Pose"
	bl_description = "Set the hand pose to a rest pose"

	obj_name = bpy.props.StringProperty()

	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	def execute(self, context):
		if self.obj_name in context.scene.objects.keys():
			self.obj = context.scene.objects[self.obj_name]
		else:
			return {'CANCELLED'}


		# Check the object is an Esquisse armature
		if self.obj.esquisse.isHand:

			# Reset the bone matrix
			for bone in self.obj.pose.bones:
				bone.matrix_basis = Matrix()

			# Reset the fingers opening to 1:
			self.obj.esquisse.hand_properties.thumb_opening = 1
			self.obj.esquisse.hand_properties.index_opening = 1
			self.obj.esquisse.hand_properties.middle_opening = 1
			self.obj.esquisse.hand_properties.ring_opening = 1
			self.obj.esquisse.hand_properties.pinky_opening = 1

			# Update the scene
			context.scene.update()

		elif self.obj.esquisse.isCharacter:
			
			# Disable all rotations
			for bone in self.obj.pose.bones:
				bone.matrix_basis = Matrix()

			#Reset panel values
			self.obj.esquisse.character_properties.L_thumb_opening = 1
			self.obj.esquisse.character_properties.L_index_opening = 1
			self.obj.esquisse.character_properties.L_middle_opening = 1
			self.obj.esquisse.character_properties.L_ring_opening = 1
			self.obj.esquisse.character_properties.L_pinky_opening = 1

			self.obj.esquisse.character_properties.R_thumb_opening = 1
			self.obj.esquisse.character_properties.R_index_opening = 1
			self.obj.esquisse.character_properties.R_middle_opening = 1
			self.obj.esquisse.character_properties.R_ring_opening = 1
			self.obj.esquisse.character_properties.R_pinky_opening = 1

			self.obj.esquisse.character_properties.head_top_bottom = 0
			self.obj.esquisse.character_properties.head_left_right = 0
			self.obj.esquisse.character_properties.back_upward_backward = 0

			# Update the scene
			context.scene.update()


		return {'FINISHED'}
