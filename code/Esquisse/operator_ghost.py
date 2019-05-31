import bpy
from bpy_extras import view3d_utils
import bgl
import math
from mathutils import Vector, Matrix
from bpy.app.handlers import persistent
from .FunctionsUtils import *
import bmesh




class EsquisseAddGhostScreenshotOperator(bpy.types.Operator):

	bl_idname = "esquisse.add_ghost_screenshot"
	bl_label = "Add a Ghost screenshot"
	bl_description = "Save the current state of current scene objects"

	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	def execute(self, context):

		if not context.scene.esquisse.ghost_mode_enable:
			return {'CANCELLED'}

		print("Adding Ghost screenshot")

		# Find the next number of the screenshot
		max_number = 0
		for ghost_screenshot in context.scene.esquisse.ghost_screenshots_list:
			if ghost_screenshot.number > max_number:
				max_number = ghost_screenshot.number

		# Create and set the screenshot
		ghost_screenshot = context.scene.esquisse.ghost_screenshots_list.add()
		ghost_screenshot.number = max_number+1
		context.scene.esquisse.current_screenshot_number = ghost_screenshot.number
		ghost_screenshot.ghost_group = bpy.data.groups.new("GhostScreenshot_%d_"%ghost_screenshot.number)
		ghost_screenshot.show_ghosts_in_scene = True


		# Remove the current objects in the save group
		if context.scene.esquisse.ghost_save_group:
			for obj in context.scene.esquisse.ghost_save_group.objects:
				context.scene.esquisse.ghost_save_group.objects.unlink(obj)
				bpy.data.objects.remove(bpy.data.objects[obj.name],True)
	
		# Save the current state of each object in the scene:
		save_group = bpy.data.groups.new("SaveGroup")
		copies = copy_objects(context.scene, context.scene.objects, "Save_")

		for copy in copies:
			save_group.objects.link(copy)
			copy.esquisse.isSave = True

		context.scene.esquisse.ghost_save_group = save_group

		return {'FINISHED'}



class EsquisseRemoveGhostScreenshot(bpy.types.Operator):

	bl_idname = "esquisse.remove_ghost_screenshot"
	bl_label = "Set Ghost screenshot"
	bl_description = "Set the current to the screenshot state"

	screenshot_number = bpy.props.IntProperty()

	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D' 

	def execute(self, context):
		print("Removing Ghost screenshot")

		# Get the selected screenshot
		ghost_screenshot = None
		idx = 0
		for screenshot in context.scene.esquisse.ghost_screenshots_list:
			if screenshot.number == self.screenshot_number:
				ghost_screenshot = screenshot
				break
			idx += 1

		# deselect all
		active = context.scene.objects.active
		bpy.ops.object.select_all(action='DESELECT')

		# remove it
		for obj in screenshot.ghost_group.objects:
			obj.hide_select = False
			obj.select = True
			for child in getChildren(obj):
				child.hide_select = False
				child.select = True
			if not obj.esquisse.isAnchor:
				for parent in getParent(obj):
					parent.hide_select = False
					parent.select = True

		bpy.ops.object.delete() 

		# Remove from data
		for obj in screenshot.ghost_group.objects:
			bpy.data.objects.remove(bpy.data.objects[obj.name],True)

		if active:
			context.scene.objects.active = active
			active.select = True

		bpy.data.groups.remove(screenshot.ghost_group)

		context.scene.esquisse.ghost_screenshots_list.remove(idx)

		size = len(context.scene.esquisse.ghost_screenshots_list)


		if self.screenshot_number == context.scene.esquisse.current_screenshot_number:
			context.scene.esquisse.current_screenshot_number = -1
	
		return {'FINISHED'}


@persistent
def callback_ghost(scene):

	n = len(scene.esquisse.ghost_screenshots_list)
	if (not scene.esquisse.ghost_mode_enable) or (n == 0) or (scene.esquisse.current_screenshot_number == -1):
		return

	# Get the selected object in the scene
	selected_objects = []
	for obj in scene.objects:
		if obj.select:
			selected_objects.append(obj)

	# Get the current ghost screenshot
	ghost_screenshot = None
	for s in scene.esquisse.ghost_screenshots_list:
		if s.number == scene.esquisse.current_screenshot_number:
			ghost_screenshot = s
			break

	# Check if selected objects have moved since the save state (from add screenshot button)
	objects_to_add_in_screenshot = []
	for obj in selected_objects:

		if not object_in_screenshot(obj, ghost_screenshot):

			for save_obj in scene.esquisse.ghost_save_group.objects:
				save_source = save_obj.esquisse.source_object

				if save_source == obj and object_moved(save_obj, obj):
					objects_to_add_in_screenshot.append(obj)

	# Add the objects
	copies = copy_objects(scene, objects_to_add_in_screenshot, "GhostScreenshot_%d_"%(ghost_screenshot.number))

	for copy in copies:
		copy.esquisse.isGhost = True
		scene.objects.link(copy)
		if not copy.esquisse.isAnchor:
			copy.draw_type = "WIRE"
		ghost_screenshot.ghost_group.objects.link(copy)


		print("\n Ghost screenshot:")
		for obj in ghost_screenshot.ghost_group.objects:
			print(obj.name, obj.esquisse.source_object.name)







def object_in_screenshot(obj, ghost_screenshot):

	for o in ghost_screenshot.ghost_group.objects:
		if o.esquisse.source_object == obj:
			return True
	return False


def applyPose(armature):
	# Deselect all objects:
	for obj in bpy.context.scene.objects:
		obj.select = False

	old_active_obj = bpy.context.scene.objects.active
	bpy.context.scene.objects.active = armature 

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


def copy_objects(scene, objects, prename):

	if len(objects) == 0:
		return []

	all_objects = []

	# Get the object and its hierarchy
	for obj in objects:
		all_objects.append(obj)
		all_objects+=getChildren(obj)

		#if the object is an anchor, then also add the constrained hand if it has
		if obj.esquisse.isAnchor and obj.esquisse.anchor_properties.constrained_object is not None:
			all_objects.append(obj.esquisse.anchor_properties.constrained_object)
			all_objects+=getAnchors(scene, obj.esquisse.anchor_properties.constrained_object)
			all_objects+=getChildren(obj.esquisse.anchor_properties.constrained_object)

		#all_objects+=getParent(obj)

		# if the object in an armature, check if there is anchors linked
		if obj.type == 'ARMATURE':
			all_objects+=getAnchors(scene, obj)

	all_objects = set(all_objects)


	print("All objects")
	print(all_objects)

	new_objs_dictionnary = {}
	new_objs = []

	# Duplicate each object in the scene
	for obj in all_objects:
		if obj.type in ['ARMATURE', 'MESH'] and not obj.esquisse.isGhost:
			
			copy = obj.copy()
			#copy.data = obj.data.copy()

			copy.name = prename + obj.name
			# scene.objects.link(copy)
			# copy.draw_type = 'WIRE'
			copy.esquisse.source_object = obj
			new_objs.append(copy)
			new_objs_dictionnary[obj] = copy


	
	for obj in new_objs:
		# ghost_screenshot.ghost_group.objects.link(obj)
		obj.select = False
		obj.esquisse.isGhost = True
		if obj.parent is not None and obj.parent in new_objs_dictionnary.keys():
			mw = obj.matrix_world
			obj.parent = new_objs_dictionnary[obj.parent]
			obj.matrix_world = mw

		# Check the modifiers for armature
		for modifier in obj.modifiers:
			if modifier.type == 'ARMATURE':
				modifier.object = new_objs_dictionnary[modifier.object]

		# Check the anchor targets of the copy bone armature
		if obj.type == 'ARMATURE':
			for bone in obj.pose.bones:
				for constraint in bone.constraints:
					if constraint.type == 'IK' and constraint.target is not None:
						if constraint.target in new_objs_dictionnary.keys():
							constraint.target = new_objs_dictionnary[constraint.target]

		# if obj.esquisse.isAnchor:
		# 	obj.esquisse.anchor_properties.constrained_object = new_objs_dictionnary[obj.esquisse.anchor_properties.constrained_object]


	return new_objs


def object_moved(obj1, obj2):
	delta = 0.01

	# Check if the object matrix has changed
	for i in range(0,4):
		for j in range(0,4):
			if abs(obj1.matrix_world[i][j]-obj2.matrix_world[i][j]) > delta:
				return True

	# Check if the armature bone has moved
	if obj1.type == 'ARMATURE' and obj2.type == 'ARMATURE':
		for obj1_bone in obj1.pose.bones:
			obj2_bone = obj2.pose.bones.get(obj1_bone.name)
			for i in range(0,4):
				for j in range(0,4):				
					if abs(obj1_bone.matrix[i][j]-obj2_bone.matrix[i][j]) > delta:
						return True
	return False


def getChildren(obj):
	objs = []
	if len(obj.children)==0:
		return objs
	
	for child in obj.children:
		if not child.esquisse.isAnchor:
			objs.append(child)
			objs+=getChildren(child)

	return objs

def getParent(obj):
	objs = []
	
	if obj.parent is not None:
		objs.append(obj.parent)
		objs+=getParent(obj.parent)

	return objs


def getAnchors(scene, obj):
	anchors = []
	for o in scene.objects:
		if o.esquisse.isAnchor and o.esquisse.anchor_properties.constrained_object == obj:
			anchors.append(o) 
	return anchors




def register():
	bpy.app.handlers.scene_update_pre.append(callback_ghost)


def unregister():

	bpy.app.handlers.scene_update_pre.remove(callback_ghost)





