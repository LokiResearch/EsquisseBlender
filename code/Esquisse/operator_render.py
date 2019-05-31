import bpy
import time
import gpu
import bgl
import blf

from .renderCore import RenderCore 

running = False
class EsquisseRenderOperator(bpy.types.Operator):

	bl_idname = "esquisse.renderstill"
	bl_label = "Esquisse Render Operator"
	bl_description = "Render the SVG [ESC to cancel rendering]"
	
	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'



	def modal(self, context, event):
		global running

		if not running:
			context.window_manager.event_timer_remove(self._timer)
			bpy.types.SpaceView3D.draw_handler_remove(self.message_callback, 'WINDOW')
			return {'FINISHED'}
	
		if event.type == 'ESC':
			bpy.types.SpaceView3D.draw_handler_remove(self.draw_scene_handler, 'WINDOW')
			return {'CANCELLED'}
		
		if event.type == 'TIMER':
			running = not self.renderCore.renderStillImage()
			if not running:
				self.message = 'Finished !'

		return {'PASS_THROUGH'}

	def execute(self, context):
		global running
		if running:
			print("Esquisse renderer is already running. Please wait or cancel before starting it again.")
			return{'CANCELLED'}


		bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath, check_existing = False)

		running = True
		context.window_manager.modal_handler_add(self)
		self._timer = context.window_manager.event_timer_add(0.00000001, context.window)

		# context.window_manager.modal_handler_add(self)
		
		self.message = "Rendering.."
		self.message_callback = bpy.types.SpaceView3D.draw_handler_add(self.draw_message, (context,), 'WINDOW', 'POST_PIXEL')
		self.renderCore = RenderCore(context)


		#self.draw_scene_handler = bpy.types.SpaceView3D.draw_handler_add(self.render_core.draw_scene, (context,), 'WINDOW', 'POST_VIEW')

		return {'RUNNING_MODAL'}



	def draw_message(self, context):

		bgl.glEnable(bgl.GL_BLEND)

		# size = max(len(self.infos_message_line1),len(self.infos_message_line2))
		
		# glColor4f(0,0,0,0.5)

		# glBegin(GL_QUADS)
		# glVertex2f(10, context.area.height - 100)
		# glVertex2f(10, context.area.height - 180)
		# glVertex2f(11*(size+1), context.area.height - 180)
		# glVertex2f(11*(size+1), context.area.height - 100)
		# glEnd()



		font_id = 0  # XXX, need to find out how best to get this.
		bgl.glColor4f(1,1,1,1)

		blf.position(font_id, 20, context.area.height - 130, 0)
		blf.size(font_id, 25, 72)
		blf.draw(font_id, self.message)
		# blf.position(font_id, 20, context.area.height - 160, 0)
		# blf.size(font_id, 25, 72)
		# blf.draw(font_id, self.infos_message_line2)



class EsquisseRenderGhostOperator(bpy.types.Operator):
	bl_idname = "esquisse.renderghost"
	bl_label = "Esquisse Render Ghost Operator"
	bl_description = "Render Ghost effect in SVG"
	
	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'


	def modal(self, context, event):
		global running

		if not running:
			context.window_manager.event_timer_remove(self._timer)
			bpy.types.SpaceView3D.draw_handler_remove(self.message_callback, 'WINDOW')
			return {'FINISHED'}
	
		if event.type == 'ESC':
			bpy.types.SpaceView3D.draw_handler_remove(self.draw_scene_handler, 'WINDOW')
			return {'CANCELLED'}
		
		if event.type == 'TIMER':
			running = not self.renderCore.renderGhostEffectImage()
			if not running:
				self.message = 'Finished !'

		return {'PASS_THROUGH'}

	def execute(self, context):
		global running
		if running:
			print("Esquisse renderer is already running. Please wait or cancel before starting it again.")
			return{'CANCELLED'}

		bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath, check_existing = False)

		running = True
		context.window_manager.modal_handler_add(self)
		self._timer = context.window_manager.event_timer_add(0.00000001, context.window)

		# context.window_manager.modal_handler_add(self)
		
		self.message = "Rendering.."
		self.message_callback = bpy.types.SpaceView3D.draw_handler_add(self.draw_message, (context,), 'WINDOW', 'POST_PIXEL')
		self.renderCore = RenderCore(context)


		#self.draw_scene_handler = bpy.types.SpaceView3D.draw_handler_add(self.render_core.draw_scene, (context,), 'WINDOW', 'POST_VIEW')

		return {'RUNNING_MODAL'}



	def draw_message(self, context):

		bgl.glEnable(bgl.GL_BLEND)

		# size = max(len(self.infos_message_line1),len(self.infos_message_line2))
		
		# glColor4f(0,0,0,0.5)

		# glBegin(GL_QUADS)
		# glVertex2f(10, context.area.height - 100)
		# glVertex2f(10, context.area.height - 180)
		# glVertex2f(11*(size+1), context.area.height - 180)
		# glVertex2f(11*(size+1), context.area.height - 100)
		# glEnd()



		font_id = 0  # XXX, need to find out how best to get this.
		bgl.glColor4f(1,1,1,1)

		blf.position(font_id, 20, context.area.height - 130, 0)
		blf.size(font_id, 25, 72)
		blf.draw(font_id, self.message)
		# blf.position(font_id, 20, context.area.height - 160, 0)
		# blf.size(font_id, 25, 72)
		# blf.draw(font_id, self.infos_message_line2)










