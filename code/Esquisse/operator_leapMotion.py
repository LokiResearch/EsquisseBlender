import bpy
import time
from .LeapMotion import Leap
from mathutils import *
import math


listening_leapMotion = False

class LeapMotionOperator(bpy.types.Operator):

	bl_idname = "leapmotion.listen"
	bl_label = "Leap Motion Listener"
	bl_description = "Start/Stop listening for Leap Motion events [ESC to stop listening]"


	lock_arm = bpy.props.BoolProperty(default = False)

	def __init__(self):
		#print("Start")
		pass

	def __del__(self):
		#print("End")
		pass

	
	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	def modal(self, context, event):

		# QUIT
		if event.type == 'ESC':
			self.stopOperator(context)
			context.area.tag_redraw()
			return {'CANCELLED'}

		self.leap_listener.getLastFrame()

		return {'PASS_THROUGH'}


	def execute(self, context):

		global listening_leapMotion

		if listening_leapMotion:
			print("already listenning")
			return {'CANCELLED'}

		listening_leapMotion = True
		context.window_manager.modal_handler_add(self)

		self._timer = context.window_manager.event_timer_add(0.00000001, context.window)

		self.leap_listener = LeapMotionListener()
		self.leap_listener.lock_arm = self.lock_arm


		return {'RUNNING_MODAL'}



	def stopOperator(self,context):
		print("LeapMotion listening stopped.")
		global listening_leapMotion
		listening_leapMotion = False

		if context.scene.leapmotionhands.left_manipulated_hand:
			context.scene.leapmotionhands.left_manipulated_hand.leapmotion.leap_control = False
			context.scene.leapmotionhands.left_manipulated_hand = None

		if context.scene.leapmotionhands.right_manipulated_hand:
			context.scene.leapmotionhands.right_manipulated_hand.leapmotion.leap_control = False
			context.scene.leapmotionhands.right_manipulated_hand = None

		context.window_manager.event_timer_remove(self._timer)
		self._timer = None


	


class BlenderHand():

	def __init__(self, obj):

		self.obj = obj

		self.rest_pose()

		self.delta_distance = self.obj.pose.bones.get("Wrist").tail - self.obj.pose.bones.get("Arm").head

	def rest_pose(self):
		for bone in self.obj.pose.bones:
			bone.matrix_basis = Matrix()

class LeapMotionListener(Leap.Listener):

	def __init__(self):
		self.lock_arm = False
		self.controller = Leap.Controller()

		self.right_hand = None
		if bpy.context.scene.leapmotionhands.right_manipulated_hand:
			self.right_hand = BlenderHand(bpy.context.scene.leapmotionhands.right_manipulated_hand)
		self.left_hand = None

		if bpy.context.scene.leapmotionhands.left_manipulated_hand:
			self.left_hand = BlenderHand(bpy.context.scene.leapmotionhands.left_manipulated_hand)

	def getLastFrame(self):

		
		def handle_hand(leap_hand, blender_hand, transform_matrix_f):


			old_loc = blender_hand.obj.pose.bones.get('Arm').location
			blender_hand.obj.pose.bones.get('Arm').matrix = transform_matrix_f(leap_hand.arm.basis)
			blender_hand.obj.pose.bones.get('Arm').location = old_loc
			blender_hand.obj.pose.bones.get('Wrist').matrix = transform_matrix_f(leap_hand.basis)

			if not self.lock_arm:
				scale = blender_hand.obj.pose.bones.get('Finger_10').bone.length/leap_hand.fingers[1].bone(0).length
				blender_hand.obj.pose.bones.get('Arm').location = leapVectorToBlenderVector(leap_hand.palm_position)*scale*blender_hand.obj.leapmotion.translation_scale
			


			for i in range(0,5):
				for j in range(1,4):
					finger_name = 'Finger_'+str(i)+str(j)
					blender_bone = blender_hand.obj.pose.bones.get(finger_name)
					leap_bone = leap_hand.fingers[i].bone(j)
					blender_bone.matrix = transform_matrix_f(leap_bone.basis)


		frame = self.controller.frame()

		leap_left_hand = None
		leap_right_hand = None
		for hand in frame.hands:
			if hand.is_left and hand.is_valid:
				leap_left_hand = hand
			elif hand.is_right and hand.is_valid:
				leap_right_hand = hand

		if self.right_hand:
			if leap_right_hand:
				handle_hand(leap_right_hand, self.right_hand, leapBasisToBlenderMatrix_right)
			else:
				self.right_hand.rest_pose()

		if self.left_hand:
			if leap_left_hand:
				handle_hand(leap_left_hand, self.left_hand, leapBasisToBlenderMatrix_left)
			else:
				self.left_hand.rest_pose()


def rad(deg):
	return deg * Leap.DEG_TO_RAD

def deg(rad):
	return rad * Leap.RAD_TO_DEG


def leapVectorToBlenderVector(v):
	return Vector((-v.x, -v.z, -v.y))



def leapBasisToBlenderMatrix_left(basis):
	leap_matrix = Leap.Matrix(basis.x_basis, -basis.z_basis, -basis.y_basis).to_array_4x4()
	blender_matrix = Matrix((leap_matrix[0:4], leap_matrix[4:8], leap_matrix[8:12], leap_matrix[12:16])).inverted()
	output_matrix = blender_matrix
	return output_matrix

def leapBasisToBlenderMatrix_right(basis):
	leap_matrix = Leap.Matrix(-basis.x_basis, -basis.z_basis, -basis.y_basis).to_array_4x4()
	blender_matrix = Matrix((leap_matrix[0:4], leap_matrix[4:8], leap_matrix[8:12], leap_matrix[12:16])).inverted()
	output_matrix = blender_matrix
	return output_matrix




def rotationMatrixToEulerAngles(R) :
      
    sy = math.sqrt(R[0] * R[0] +  R[3] * R[3])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[7] , R[8])
        y = math.atan2(-R[6], sy)
        z = math.atan2(R[3], R[0])
    else :
        x = math.atan2(-R[5], R[4])
        y = math.atan2(-R[6], sy)
        z = 0
    return (x,y,z)
    # return (deg(x), deg(y), deg(z))






