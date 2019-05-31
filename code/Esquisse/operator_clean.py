import bpy

from bpy.props import PointerProperty, IntProperty
from bpy.types import Object


class EsquisseCleanData(bpy.types.Operator):

	bl_idname = "esquisse.clean_data"
	bl_label = "Clean data not used in the current scene"

	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	def execute(self, context):

		for obj in bpy.data.objects:
			if obj.name not in context.scene.objects.keys():
				bpy.data.objects.remove(obj, True)

		return {'FINISHED'}






