# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import time
import threading
from Esquisse.SimpleWebSocketServer import WebSocket, SimpleWebSocketServer

server_listening = False

# https://medium.com/tensorflow/real-time-human-pose-estimation-in-the-browser-with-tensorflow-js-7dd0bc881cd5


def thread_func(server, context):
	global server_listening

	while server_listening:
		server.serveonce()



class PoseNetServer(WebSocket):

	def handleMessage(self):
		print("Message:",self.data)

	def handleConnected(self):
		print(self.address, 'connected')

	def handleClose(self):
		print(self.address, 'closed')



class PoseNetOperator(bpy.types.Operator):

	bl_idname = "esquisse.posenet"
	bl_label = "Esquisse PoseNet"
	bl_description = "Start/Stop listening for events [ESC to stop listening]"

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

			return {'CANCELLED'}


		return {'PASS_THROUGH'}

	

	def execute(self, context):

		global server_listening

		if server_listening:
			print("already listenning")
			return {'CANCELLED'}

		server_listening = True
		context.window_manager.modal_handler_add(self)

		#self._timer = context.window_manager.event_timer_add(0.00000001, context.window)
		self.server = SimpleWebSocketServer('', 8000, PoseNetServer)
		self.thread = threading.Thread(target = thread_func, args = (self.server, context,))
		self.thread.start()

		return {'RUNNING_MODAL'}



	def stopOperator(self,context):
		print("PoseNet Server stopped.")
		global server_listening
		server_listening = False
		self.thread.join()
		self.server.close()

		#context.window_manager.event_timer_remove(self._timer)
		#self._timer = None


		







