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






