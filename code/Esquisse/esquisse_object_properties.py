import bpy
import re
import os

from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.props import PointerProperty, FloatVectorProperty, CollectionProperty
from bpy.types import Panel, Operator, AddonPreferences, PropertyGroup, BlendData, Object

from .FunctionsUtils import *
from mathutils import Matrix
from math import radians, cos, sin

class EsquisseAnchor(bpy.types.PropertyGroup):



	def constrained_object_poll(self, obj):
		'''		
		Function used to restrict the type object displayed in the constrain list
		'''
		return (not obj.esquisse.isSave) and (obj.esquisse.isHand or obj.esquisse.isCharacter) and (obj.name in bpy.context.scene.objects)

	def radius_update(self, context):

		# Save and get the selected objects and the active
		save_selected_objects = bpy.context.selected_objects
		save_active_object = context.scene.objects.active

		# Deselect all the objects in the scene
		for ob in bpy.context.selected_objects:
			ob.select = False

		# Select the anchor
		self.id_data.select = True

		# Set the anchor as the active object
		context.scene.objects.active = self.id_data

		# Change the scale of the anchor (can't be 0, so add delta)
		delta = 0.001
		self.id_data.dimensions = (self.radius+delta, self.radius+delta, 0)

		# Apply the new scale as a scale of 1 (Needed for size constraints)
		bpy.ops.object.transform_apply(scale = True)

		# Deselect the anchor
		self.id_data.select = False

		# Restaure selected objects and the active
		for ob in save_selected_objects:
			ob.select = True
		context.scene.objects.active = save_active_object


	def constrained_object_updated(self, context):

		if not self.constrained_object:
			self.constrained_finger = 'none'
			return

		if not (self.constrained_object.esquisse.isHand or self.constrained_object.esquisse.isCharacter):
			self.constrained_object = None
		
		self.old_constrained_object = self.constrained_object


	def get_fingers_items(self, context):


		items=[('none', 'none', '')]

		if not self.constrained_object:
			return items

		elif self.constrained_object.esquisse.isHand:
			items.append(('Finger_01', 'Thumb', ''))
			items.append(('Finger_11', 'Index', ''))
			items.append(('Finger_21', 'Middle', ''))
			items.append(('Finger_31', 'Ring', ''))
			items.append(('Finger_41', 'Pinky', ''))
			
		elif self.constrained_object.esquisse.isCharacter:
			items.append(('thumb_R', 'R_Thumb', ''))
			items.append(('index_R', 'R_Index', ''))
			items.append(('middle_R', 'R_Middle', ''))
			items.append(('ring_R', 'R_Ring', ''))
			items.append(('pinky_R', 'R_Pinky', ''))
			items.append(('thumb_L', 'L_Thumb', ''))
			items.append(('index_L', 'L_Index', ''))
			items.append(('middle_L', 'L_Middle', ''))
			items.append(('ring_L', 'L_Ring', ''))
			items.append(('pinky_L', 'L_Pinky', ''))

		return items


	def get_constraint_types_items(self, context):

		if not self.constrained_object:
			return []

		elif self.constrained_object.esquisse.isHand:
			return [
			('onhand', 'All Hand', '' ),
			('onfinger', 'Finger Only','')]
		elif self.constrained_object.esquisse.isCharacter:
			return [
			('onarm', 'All Arm', '' ),
			('onfinger', 'Finger Only','')]

		return []

	def constraint_type_update(self, context):

		# Be sure a constrained finger has been chosen
		if 'none' in self.constrained_finger:
			return

		# get the constrained bone of the finger
		constrained_finger_bone = self.constrained_object.pose.bones[self.constrained_finger]
		while constrained_finger_bone.child:
			constrained_finger_bone = constrained_finger_bone.child
		
		if self.constrained_object.esquisse.isHand:
			constraint_size = 0
			if self.constraint_type == 'onhand':
				constraint_size = 0
			elif self.constraint_type == 'onfinger':
				constraint_size = 3
				if self.constrained_finger == 'thumb':
					constraint_size = 4
		elif self.constrained_object.esquisse.isCharacter:
			constraint_size = 6
			if self.constraint_type == 'onarm':
				constraint_size = 6
			elif self.constraint_type == 'onfinger':
				constraint_size = 3
				# if self.constrained_finger == 'thumb':
				# 	constraint_size = 4

		for constraint in constrained_finger_bone.constraints:
			if constraint.type == 'IK': 
				constraint.chain_count = constraint_size



	def constrained_finger_update(self, context):

		'''
		Here we want to add a constraint to a finger
		Steps:
		1. Remove the constraint of the previous finger chosen (if it exists, i.e. old != none) 
		2. If the new finger chosen is not none continue
		3. If the constraint of the finger is the first of all constraints of the hand, move the finger tail 
			(a Blender PoseBone has a head and a tail), to the anchor position
		4. Create the constraint between the finger and the anchor

		'''
	
		# Step 1 : Remove the constraint of the previous finger

		if 'none' not in self.old_constrained_finger:
			# get the root bone of the finger
			bone = self.old_constrained_object.pose.bones[self.old_constrained_finger]
			while bone.child:
				bone = bone.child

			# Remove constraint of type Inverse Kinematics
			for constraint in bone.constraints:
				if constraint.type == 'IK': 
					bone.constraints.remove(constraint)

		
		self.old_constrained_finger = self.constrained_finger


		# Step 2 : No Finger has been chosen
		if 'none' in self.constrained_finger:
			return


		# get the constrained bone of the finger
		constrained_finger_bone = self.constrained_object.pose.bones[self.constrained_finger]
		while constrained_finger_bone.child:
			constrained_finger_bone = constrained_finger_bone.child


		# Step 3 : Check if the anchor is the first anchor of the hand
		# If it is, move the hand finger tail to the anchor

		# if self.constrained_object.esquisse.isHand:
			
		# 	found_another_anchor = False
		# 	for obj in context.scene.objects:
		# 		if not obj == self.id_data and (obj.esquisse.isAnchor) and obj.esquisse.anchor_properties.constrained_object == self.constrained_object:
		# 			# Here, there is another existing anchor attached to the hand 
		# 			found_another_anchor = True
		# 			break


		# 	if not found_another_anchor:

		# 		# test if one bone is overlaping the screen (compute raycast with the screen normal)
		# 		# If so, we consider the hand is close enough not to be moved 

		# 		bone_overlaping_screen = False
				
		# 		for bone in self.constrained_object.pose.bones:

		# 			# get the world loc for the bone tail
		# 			w_loc = self.constrained_object.matrix_world*bone.tail

		# 			bone_overlaping_screen,_,_,_  = self.screen.ray_cast(self.screen.matrix_world.inverted() * w_loc,-self.screen.data.vertices[0].normal )

		# 			if bone_overlaping_screen:
		# 				break

		# 		if not bone_overlaping_screen:
				
		# 			print("Automatically moving the contrained object.")

		# 			# # Reset the hand pose:
		# 			for bone in self.constrained_object.pose.bones:
		# 				bone.matrix_basis = Matrix()

		# 			self.constrained_object.esquisse.hand_properties.thumb_opening = 1 if 'Finger_01' in self.constrained_finger else 0
		# 			self.constrained_object.esquisse.hand_properties.index_opening = 1 if 'Finger_11' in self.constrained_finger else 0
		# 			self.constrained_object.esquisse.hand_properties.middle_opening = 1 if 'Finger_21' in self.constrained_finger else 0
		# 			self.constrained_object.esquisse.hand_properties.ring_opening = 1 if 'Finger_31' in self.constrained_finger else 0
		# 			self.constrained_object.esquisse.hand_properties.pinky_opening = 1 if 'Finger_41' in self.constrained_finger else 0

		# 			# Compute the distance between the arm tail and the finger (when the finger is full opened)
		# 			# here the bone is expressend in the local space of the armature where the 
		# 			# origin should be at (0,0,0), the origin of the object `

		# 			bpy.context.scene.update()
					
		# 			d = constrained_finger_bone.tail.length

		# 			anchor_world_position = self.constrained_object.matrix_world.to_translation()

		# 			anchor_world_normal = localDirectionToWorldDirection(self.screen, self.screen.data.vertices[0].normal)

		# 			theta = radians(-45)
		# 			phi = radians(45)
		# 			if self.constrained_object.esquisse.hand_properties.is_left_hand:
		# 				phi *= -1
		# 				theta *= -1
					
		# 			v_local = Vector((d*cos(theta)*sin(phi),d*sin(theta)*sin(phi),d*cos(phi)))

		# 			# v should be in the local coordinates of the anchor
		# 			v_world = self.id_data.matrix_world*v_local

		# 			self.constrained_object.location = v_world

		

		# Step 4 : Create the Inverse Kinematics constraint between the anchor and the finger PoseBone


		if self.constrained_object.esquisse.isHand:
			if 'Finger_01' in self.constrained_finger:
				self.constrained_object.esquisse.hand_properties.thumb_opening = 1 
			elif 'Finger_11' in self.constrained_finger:
				self.constrained_object.esquisse.hand_properties.index_opening = 1
			elif 'Finger_21' in self.constrained_finger:			
				self.constrained_object.esquisse.hand_properties.middle_opening = 1 
			elif 'Finger_31' in self.constrained_finger:
				self.constrained_object.esquisse.hand_properties.ring_opening = 1
			elif 'Finger_41' in self.constrained_finger:
				self.constrained_object.esquisse.hand_properties.pinky_opening = 1

		elif self.constrained_object.esquisse.isCharacter:
			if 'thumb_r' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.R_thumb_opening = 1 
			elif 'index_r' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.R_index_opening = 1
			elif 'middle_r' in self.constrained_finger:			
				self.constrained_object.esquisse.character_properties.R_middle_opening = 1 
			elif 'ring_r' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.R_ring_opening = 1
			elif 'pinky_r' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.R_pinky_opening = 1
			elif 'thumb_l' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.L_thumb_opening = 1 
			elif 'index_l' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.L_index_opening = 1
			elif 'middle_l' in self.constrained_finger:			
				self.constrained_object.esquisse.character_properties.L_middle_opening = 1 
			elif 'ring_l' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.L_ring_opening = 1
			elif 'pinky_l' in self.constrained_finger:
				self.constrained_object.esquisse.character_properties.L_pinky_opening = 1



		constraint = constrained_finger_bone.constraints.new(type='IK')
		constraint.target = self.id_data

		if self.constrained_object.esquisse.isHand:
			self.constraint_type = 'onhand'
		elif self.constrained_object.esquisse.isCharacter:
			self.constraint_type = 'onarm'



	radius = bpy.props.FloatProperty(
		default = 0.2,
		update = radius_update,
		min=0.0,
		description = "Set the radius of the anchor"
	)
	
	screen = bpy.props.PointerProperty(type = bpy.types.Object)

	constrained_object = bpy.props.PointerProperty(
		type = bpy.types.Object, 
		poll = constrained_object_poll, 
		update = constrained_object_updated,
		description = "Select the object to be anchored")


	constrained_finger = bpy.props.EnumProperty(
		items = get_fingers_items, # Get automatically finger in fucntion of the object anchored
		name="Finger to anchor",
		description="Select a finger to be anchored",
		update = constrained_finger_update,
	)


	constraint_type = bpy.props.EnumProperty(
		items= get_constraint_types_items,
		name = "Contraint type",
		description = "Choose the impact of the constraint on the finger only or on the full hand",
		update = constraint_type_update,
	)

	old_constrained_finger = bpy.props.StringProperty(default = 'none')
	old_constrained_object = bpy.props.PointerProperty(type = bpy.types.Object)

class EsquisseHand(bpy.types.PropertyGroup):

	def finger_posture(self, context, finger, value):
		angles = [radians(90),radians(90),radians(90)]
		if 'Finger_01' in finger:
			angles = [radians(30),radians(30),radians(90)]

		i = 0
		bone = self.id_data.pose.bones.get(finger)
		while bone:
			bone.matrix_basis = Matrix.Rotation(angles[i]*(1-value),4,'X')
			bone = bone.child
			i += 1

	def update_thumb_opening(self, context):
		self.finger_posture(context, 'Finger_01', self.thumb_opening)
	def update_index_opening(self, context):
		self.finger_posture(context, 'Finger_11', self.index_opening)
	def update_middle_opening(self, context):
		self.finger_posture(context, 'Finger_21', self.middle_opening)
	def update_ring_opening(self, context):
		self.finger_posture(context, 'Finger_31', self.ring_opening)
	def update_pinky_opening(self, context):
		self.finger_posture(context, 'Finger_41', self.pinky_opening)


	is_left_hand = BoolProperty(default = False)
	is_right_hand = BoolProperty(default = False)

	thumb_opening = FloatProperty(
		name = "Control the thumb opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = update_thumb_opening,
		description = "Control the thumb opening"
	)

	index_opening = FloatProperty(
		name = "Control the index opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = update_index_opening,
		description = "Control the index opening"
	)

	middle_opening = FloatProperty(
		name = "Control the middle opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = update_middle_opening,
		description = "Control the middle opening"
	)

	ring_opening = FloatProperty(
		name = "Control the ring opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = update_ring_opening,
		description = "Control the ring opening"
	)

	pinky_opening = FloatProperty(
		name = "Control the pinky opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = update_pinky_opening,
		description = "Control the pinky opening"
	)

class EsquisseCharacter(bpy.types.PropertyGroup):

	def head_posture_top_bottom(self, context):
		angle = radians(45)

		m = Matrix.Rotation(angle*self.head_top_bottom,4,'X')
		self.id_data.pose.bones.get('Neck').matrix_basis = m
		self.id_data.pose.bones.get('Head').matrix_basis = m

	def head_posture_left_right(self, context):
		angle = radians(45)

		m = Matrix.Rotation(angle*self.head_top_bottom,4,'X') * Matrix.Rotation(-angle*self.head_left_right,4,'Y')
		self.id_data.pose.bones.get('Neck').matrix_basis = m
		self.id_data.pose.bones.get('Head').matrix_basis = m

	def back_posture_upward_backward(self, context):
		angle = radians(45)

		m = Matrix.Rotation(angle*self.back_upward_backward,4,'X')
		self.id_data.pose.bones.get('Torso').matrix_basis = m
		self.id_data.pose.bones.get('Rib_cage').matrix_basis = m



	def finger_posture(self, context, finger, value):
		angles = [radians(90),radians(90),radians(90)]
		if 'thumb' in finger:
			angles = [radians(30),radians(30),radians(90)]

		i = 0
		bone = self.id_data.pose.bones.get(finger)
		while bone:
			bone.matrix_basis = Matrix.Rotation(-angles[i]*(1-value),4,'X')
			bone = bone.child
			i += 1


	def L_update_thumb_opening(self, context):
		self.finger_posture(context, 'thumb_L', self.L_thumb_opening)
	def L_update_index_opening(self, context):
		self.finger_posture(context, 'index_L', self.L_index_opening)
	def L_update_middle_opening(self, context):
		self.finger_posture(context, 'middle_L', self.L_middle_opening)
	def L_update_ring_opening(self, context):
		self.finger_posture(context, 'ring_L', self.L_ring_opening)
	def L_update_pinky_opening(self, context):
		self.finger_posture(context, 'pinky_L', self.L_pinky_opening)

	def R_update_thumb_opening(self, context):
		self.finger_posture(context, 'thumb_R', self.R_thumb_opening)
	def R_update_index_opening(self, context):
		self.finger_posture(context, 'index_R', self.R_index_opening)
	def R_update_middle_opening(self, context):
		self.finger_posture(context, 'middle_R', self.R_middle_opening)
	def R_update_ring_opening(self, context):
		self.finger_posture(context, 'ring_R', self.R_ring_opening)
	def R_update_pinky_opening(self, context):
		self.finger_posture(context, 'pinky_R', self.R_pinky_opening)

	head_top_bottom = FloatProperty(
		name = "Control the head/neck top/bottom",
		min=-1.0, 
		max=1.0,
		default = 0,
		update = head_posture_top_bottom,
		description = "Control the head/neck top/bottom"
	)

	head_left_right = FloatProperty(
		name = "Control the head/neck left/right",
		min=-1.0, 
		max=1.0,
		default = 0,
		update = head_posture_left_right,
		description = "Control the head/neck left/right"
	)

	back_upward_backward = FloatProperty(
		name = "Control the back upward/backward",
		min = 0.0,
		max = 1.0,
		default = 0,
		update = back_posture_upward_backward,
		description = "Control the back upward/backward",
	)


	R_thumb_opening = FloatProperty(
		name = "Control the thumb opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = R_update_thumb_opening,
		description = "Control the thumb opening"
	)

	R_index_opening = FloatProperty(
		name = "Control the index opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = R_update_index_opening,
		description = "Control the index opening"
	)

	R_middle_opening = FloatProperty(
		name = "Control the middle opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = R_update_middle_opening,
		description = "Control the middle opening"
	)

	R_ring_opening = FloatProperty(
		name = "Control the ring opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = R_update_ring_opening,
		description = "Control the ring opening"
	)

	R_pinky_opening = FloatProperty(
		name = "Control the pinky opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = R_update_pinky_opening,
		description = "Control the pinky opening"
	)

	L_thumb_opening = FloatProperty(
		name = "Control the thumb opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = L_update_thumb_opening,
		description = "Control the thumb opening"
	)

	L_index_opening = FloatProperty(
		name = "Control the index opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = L_update_index_opening,
		description = "Control the index opening"
	)

	L_middle_opening = FloatProperty(
		name = "Control the middle opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = L_update_middle_opening,
		description = "Control the middle opening"
	)

	L_ring_opening = FloatProperty(
		name = "Control the ring opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = L_update_ring_opening,
		description = "Control the ring opening"
	)

	L_pinky_opening = FloatProperty(
		name = "Control the pinky opening",
		min=0.0, 
		max=1.0,
		default = 1,
		update = L_update_pinky_opening,
		description = "Control the pinky opening"
	)



class EsquisseScreen(bpy.types.PropertyGroup):

	def updateScene(self, context):
		context.scene.update()
		
	use_interface = BoolProperty(
		name = "Use interface",
		description = "Use interface SVG to be displayed on the screen",
		default = False,
		update = updateScene
	)
	
	interface_path = StringProperty(
	    name = "Interface path",
	    description = "Filepath of the SVG file to be applied on the screen",
	    default = "/Users/esquissexp/Desktop/Interfaces/default_interface.svg",
	    subtype = 'FILE_PATH',
	    update = updateScene
	)

	default_texture_id = StringProperty(default = "")

	texture_loaded = BoolProperty(
		default = False
	)

	texture_id = StringProperty(
		default = ""
	)



class EsquisseObjectTypePanel(bpy.types.Panel):
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_label = "Esquisse Object Type"
	bl_options = {'DEFAULT_CLOSED'}
	bl_context = "object"


	def draw(self, context):
		obj = context.object

		row = self.layout.row(True)
		row.prop(obj.esquisse, 'isHand', text="Esquisse hand")
		if obj.esquisse.isHand:
			row.prop(obj.esquisse.hand_properties, 'is_left_hand', text="Left")
			row.prop(obj.esquisse.hand_properties, 'is_right_hand', text="Right")			

		row = self.layout.row(True)
		row.prop(obj.esquisse, 'isScreen', text="Esquisse screen")

		row = self.layout.row(True)
		row.prop(obj.esquisse, 'isCharacter', text="Esquisse character")


class EsquisseObjectProperties(PropertyGroup):

	isAnchor = BoolProperty(default = False)
	anchor_properties = PointerProperty(name = "EsquisseAnchor", type=EsquisseAnchor)

	isHand = BoolProperty(default = False)
	hand_properties = PointerProperty(name = "EsquisseHand", type=EsquisseHand)
	
	isScreen = BoolProperty(default = False)
	screen_properties = PointerProperty(name = "EsquisseScreen", type=EsquisseScreen)
	
	isCharacter = BoolProperty(default = False)
	character_properties = PointerProperty(name = "EsquisseCharacter", type=EsquisseCharacter)

	expand_properties = BoolProperty(
		default = False,
		description = "Show/Hide all properties related to this object"
	)

	isSave = BoolProperty(default = False)
	isGhost = BoolProperty(default = False)
	source_object = PointerProperty(type = bpy.types.Object)
	ghost_source_object = PointerProperty(type = bpy.types.Object)
	
	transparent = BoolProperty(default = False)
	transparency = FloatProperty(default = 0.5, min = 0, max = 1)
	make_visible_hidden_contours_transparent = BoolProperty(
		default = False,
		description = "Enable contours of other objects hidden by this transparent object to be considered as visible."
		)



def register():
	bpy.types.Object.esquisse = PointerProperty(name = "Esquisse Object Properties", type=EsquisseObjectProperties)


def unregister():
	del bpy.types.Object.esquisse
