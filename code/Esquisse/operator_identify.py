# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy

from bpy.props import PointerProperty, IntProperty
from bpy.types import Object


class EsquisseIdentifyObject(bpy.types.Operator):

	bl_idname = "esquisse.identify_object"
	bl_label = "Identify Scene Object"
	bl_description = "Identify and select the object in the scene"

	obj_name = bpy.props.StringProperty()

	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	def execute(self, context):
		if self.obj_name in context.scene.objects.keys():
			self.obj = context.scene.objects[self.obj_name]
		else:
			return {'CANCELLED'}

		for obj in bpy.data.objects:
			obj.select = False

		# If the object to identify is a screen, then if it has a parent, select the parent, else select the screen
		if self.obj.esquisse.isScreen and self.obj.parent:
			self.obj.parent.select = True
			bpy.context.scene.objects.active = self.obj.parent
		else:
			self.obj.select = True
			bpy.context.scene.objects.active = self.obj

		context.area.tag_redraw()

		return {'FINISHED'}
