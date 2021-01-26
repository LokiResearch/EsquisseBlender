# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy


from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Panel, Operator, AddonPreferences, PropertyGroup, BlendData, UIList

from . import operator_leapMotion


class LeapMotion(bpy.types.PropertyGroup):

	def onHandCheckUpdate(self, context):

		if self.leap_control:
			if self.id_data.esquisse.hand_properties.is_left_hand:
				if context.scene.leapmotionhands.left_manipulated_hand:
					context.scene.leapmotionhands.left_manipulated_hand.leapmotion.leap_control = False
				context.scene.leapmotionhands.left_manipulated_hand = self.id_data

			elif self.id_data.esquisse.hand_properties.is_right_hand:
				if context.scene.leapmotionhands.right_manipulated_hand:
					context.scene.leapmotionhands.right_manipulated_hand.leapmotion.leap_control = False
				context.scene.leapmotionhands.right_manipulated_hand = self.id_data
		else:
			if self.id_data.esquisse.hand_properties.is_left_hand:
				if context.scene.leapmotionhands.left_manipulated_hand:
					context.scene.leapmotionhands.left_manipulated_hand = None

			elif self.id_data.esquisse.hand_properties.is_right_hand:
				if context.scene.leapmotionhands.right_manipulated_hand:
					context.scene.leapmotionhands.right_manipulated_hand = None

		print("Right hand:",context.scene.leapmotionhands.right_manipulated_hand)
		print("Left hand:",context.scene.leapmotionhands.left_manipulated_hand)


	leap_control = BoolProperty(default = False, update = onHandCheckUpdate)

	translation_scale = FloatProperty(default = 1)



class LeapMotionHands(bpy.types.PropertyGroup):

	left_manipulated_hand = PointerProperty(type = bpy.types.Object)
	right_manipulated_hand = PointerProperty(type = bpy.types.Object)


class LeapMotionPanel(bpy.types.Panel):
	bl_idname = "leapmotion_panel"
	bl_label = "Leap Motion"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Esquisse"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
	# Leap Motion properties :

		leap_box = self.layout.box()
		leap_box.label("Leap Motion")

		left_hands_box = leap_box.box()
		left_hands_box.label('Left Hands:')

		right_hands_box = leap_box.box()
		right_hands_box.label('Right Hands')

		for obj in bpy.context.scene.objects:
			if obj.esquisse.isHand and not obj.esquisse.isGhost: 
				if obj.esquisse.hand_properties.is_left_hand:
					row = left_hands_box.row(True)
					
				elif obj.esquisse.hand_properties.is_right_hand:
					row = right_hands_box.row(True)
				
				row.label(obj.name, icon='MOD_ARMATURE')
				row.prop(obj.leapmotion, 'translation_scale', text='Scale' )
				row.prop(obj.leapmotion, 'leap_control', text='Control')
				row.operator('esquisse.identify_object', icon = 'RESTRICT_SELECT_OFF', text="").obj_name = obj.name


		row = leap_box.row(True)

		text = "(on)" if operator_leapMotion.listening_leapMotion else "(off)"
		row.operator("leapmotion.listen", icon='POSE_DATA', text= "LeapMotion" + text)

		op = row.operator("leapmotion.listen", icon='POSE_DATA', text= "LeapMotion[OnlyWrist]" + text)
		op.lock_arm = True


def register():
	bpy.types.Object.leapmotion = PointerProperty(type=LeapMotion)
	bpy.types.Scene.leapmotionhands = PointerProperty(type=LeapMotionHands)


 
def unregister():
	del bpy.types.Object.leapmotion