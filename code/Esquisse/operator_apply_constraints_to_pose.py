import bpy

class EsquisseApplyConstraintsToPose(bpy.types.Operator):

	bl_idname = "esquisse.apply_constraints_to_pose"
	bl_label = "Apply the constraints on a Esquisse compatible armature to its pose"
	bl_description = "Apply the current constraints on the armature to the pose. This allows removing the anchors and keeping the armature pose."

	obj_name = bpy.props.StringProperty()

	def execute(self, context):
		if self.obj_name in bpy.context.scene.objects.keys():
			self.obj = bpy.context.scene.objects[self.obj_name]
		else:
			return {'CANCELLED'}


		# Check the object is Esquisse compatible
		if not (self.obj.esquisse.isHand or self.obj.esquisse.isCharacter):
			return {'CANCELLED'}

		# Deselect all objects:
		for obj in bpy.context.scene.objects:
			obj.select = False

		old_active_obj = bpy.context.scene.objects.active
		bpy.context.scene.objects.active = self.obj 

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
