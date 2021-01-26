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
def add_material(dummy):
	if bpy.context.scene.esquisse.is_rendering:
		return
		
	for obj in bpy.context.scene.objects:
		if obj.type == 'MESH' and len(obj.data.materials) == 0:
			obj.data.materials.append(bpy.data.materials.new(name=obj.name+"_Material"))


def register():	
	bpy.app.handlers.scene_update_post.append(add_material)


def unregister():
	bpy.app.handlers.scene_update_post.remove(add_material)

	
