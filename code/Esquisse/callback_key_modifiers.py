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

from mathutils import Vector
from .FunctionsUtils import *


alt_modifier_pressed = False


class AltModifier(bpy.types.Operator):


	bl_idname = 'esquisse.getmodifier'
	bl_label = 'Esquisse Track Objects'

	@classmethod
	def poll(cls, context):
		return context.space_data.type == 'VIEW_3D'

	def invoke(self, context, event):
		global alt_modifier_pressed

		if event.type == 'LEFT_ALT' and event.value == "PRESS":
			alt_modifier_pressed = True
		elif event.type == 'LEFT_ALT' and event.value == "RELEASE":
			alt_modifier_pressed = False

		print("Alt modifier :",alt_modifier_pressed)

		return {'FINISHED'}

def register():

	wm = bpy.context.window_manager
	kc = wm.keyconfigs['Blender User']
	km = kc.keymaps['3D View']
	kmi = km.keymap_items.new(AltModifier.bl_idname, 'LEFT_ALT', 'PRESS', alt=True)
	kmi = km.keymap_items.new(AltModifier.bl_idname, 'LEFT_ALT', 'RELEASE')


	


