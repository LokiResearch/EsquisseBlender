import bpy
import re
import os

from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.props import PointerProperty, FloatVectorProperty, CollectionProperty
from bpy.types import Panel, Operator, AddonPreferences, PropertyGroup, BlendData, Object

from .FunctionsUtils import *
from mathutils import Matrix
from math import radians, cos, sin

class GhostScreenshot(bpy.types.PropertyGroup):

	def show_ghosts_update_func(self, context):
		
		for obj in self.ghost_group.objects:
			obj.hide = not self.show_ghosts_in_scene

	show_ghosts_in_scene = BoolProperty(update = show_ghosts_update_func)

	ghost_group = PointerProperty(type = bpy.types.Group)

	number = IntProperty(name = "Index")

	use_interpolation = BoolProperty(default = False)

	number_of_interpolation = IntProperty(default = 1, min = 0, max = 100)

	def getGhostObjectForBlenderObj(self, source):
		for ghost_object in self.ghost_objects:
			if source == ghost_object.object_source:
				return ghost_object
		return None




