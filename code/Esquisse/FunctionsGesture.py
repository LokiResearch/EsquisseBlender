# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import bmesh
import math
from mathutils import Vector

def save_ui_state():#TODO
    ui_state = {}
    return ui_state
def set_ui_state(mode="OBJECT", selected_objects=None, active_object=None):#TODO
	_mode = None
	if bpy.context.object != None:
		_mode = bpy.context.object.mode
		if _mode != "OBJECT":
			bpy.ops.object.mode_set(mode='OBJECT')

def restore_ui_state(ui_state):#TODO
	pass


def get_screenshots(context):
	screenshots = []
	# Useful to have a python list and not an blender collection with less functions
	for screenshot in context.scene.esquisse.ghost_screenshots_list:
		screenshots.append(screenshot)

	# Sort the screenshots by their index:
	screenshots.sort(key= lambda x : x.number)
	return screenshots
