import bpy
import time
import bgl
import os
from math import sqrt, floor


showing_menu = False
eraseScene = False

class EsquisseObject():

	def __init__(self, blend_file_path, imageID):
		self.blend_file_path = blend_file_path
		self.imageID = imageID

class ShowEsquisseObjectsLibraryMenuOperator(bpy.types.Operator):

	bl_idname = "esquisse.show_objects_library_menu"
	bl_label = "Show Esquisse Objects Menu"
	bl_description = "Show the Esquisse objects menu [ESC to quit menu]"

	def init(self, context):

		if context.scene.esquisse.esquisse_library_path.endswith('/'):
			self.objects_directory_path = bpy.path.abspath(context.scene.esquisse.esquisse_library_path + 'objects/')
		else:
			self.objects_directory_path = bpy.path.abspath(context.scene.esquisse.esquisse_library_path + '/objects/')

		self.display_menu_handler = None

		self.selectedObject = None

		# list blend files
		files = os.listdir(self.objects_directory_path)

		blend_files = [file for file in files if file.endswith('.blend')]
		images = [file for file in files if file.endswith('.png')]

		self.objects = []

		for blend_file in blend_files:

			# Check if there is a previe picture associated with the object (same name)
			
			blend_file_name = blend_file[:-6] # Removes .blend

			i = 0
			image = None
			while image is None and i < len(images):
				if images[i][:-4] == blend_file_name:
					image = images[i]
				i += 1

			if image is not None:

				image_path = self.objects_directory_path + image

				# Load the image in the blender data
				blender_image =  bpy.data.images.load(image_path)

				# Iterate over the current images stored in blender to get the key of the new image (should be filename, but not sure)
				image_id = None
				for item in bpy.data.images.items():
					key, value = item
					if value == blender_image:
						image_id = key
						break

				self.objects.append(EsquisseObject(blend_file, image_id))
			else:
				self.objects.append(EsquisseObject(blend_file, None))

	def computeUISize(self):

		# Compute UI Elements size :

		root = sqrt(len(self.objects))
		self.menu_size = floor(root)
		if root > floor(root):
			self.menu_size += 1



		viewport = bgl.Buffer(bgl.GL_INT, 4)
		bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport)
		self.viewport_x = viewport[0]
		self.viewport_y = viewport[1]
		self.viewport_w = viewport[2]
		self.viewport_h = viewport[3]	

		self.space_ratio = 0.1

		self.h_space = self.viewport_h*self.space_ratio/(self.menu_size+1)
		self.w_space = self.viewport_w*self.space_ratio/(self.menu_size+1)

		self.item_w = self.viewport_w*(1-self.space_ratio)/self.menu_size
		self.item_h = self.viewport_h*(1-self.space_ratio)/self.menu_size

	def end(self):

		# Remove Image from blender
		for obj in self.objects:
			if obj.imageID is not None:
				bpy.data.images.remove(bpy.data.images[obj.imageID])

		
	def dipslay_menu(self,context):

		self.computeUISize()

		# draw background

		bgl.glColor4f(0,0,0,0.5)

		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBegin(bgl.GL_QUADS)
		bgl.glVertex2f(0,0)
		bgl.glVertex2f(0,self.viewport_h)
		bgl.glVertex2f(self.viewport_w,self.viewport_h)
		bgl.glVertex2f(self.viewport_w,0)
		bgl.glEnd()

		
		idx = 0
		col_idx = 0
		row_idx = 0


		while idx < len(self.objects):
		
			item_x = self.w_space + col_idx*(self.item_w + self.w_space)
			item_y = self.viewport_h - self.h_space - row_idx*(self.item_h + self.h_space)
			bgl.glColor4f(1,1,1,1)
			# if idx == self.selectedObject:
			# 	bgl.glColor4f(1,0,0,1)

			if self.objects[idx].imageID:
				img = bpy.data.images[self.objects[idx].imageID]
				img.gl_load(bgl.GL_NEAREST, bgl.GL_NEAREST)
				bgl.glBindTexture(bgl.GL_TEXTURE_2D, img.bindcode[0])
				bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
				bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
				bgl.glEnable(bgl.GL_TEXTURE_2D)


			bgl.glBegin(bgl.GL_QUADS)
			bgl.glTexCoord2f(0,1)
			bgl.glVertex2f(item_x,item_y)
			bgl.glTexCoord2f(0,0)
			bgl.glVertex2f(item_x,item_y-self.item_h)
			bgl.glTexCoord2f(1,0)
			bgl.glVertex2f(item_x+self.item_w,item_y-self.item_h)
			bgl.glTexCoord2f(1,1)
			bgl.glVertex2f(item_x+self.item_w,item_y)
			bgl.glEnd()

			idx += 1
			col_idx += 1
			if col_idx > self.menu_size-1:
				col_idx = 0
				row_idx += 1

			bgl.glDisable(bgl.GL_TEXTURE_2D)

		bgl.glDisable(bgl.GL_BLEND)


	def loadObject(self, context, obj):
		print("Load object :", obj.blend_file_path)

		filepath = self.objects_directory_path+obj.blend_file_path
		with bpy.data.libraries.load(filepath) as (data_from, data_to):
			data_to.objects = data_from.objects

		# Add new object in the scene
		for obj in data_to.objects:
			context.scene.objects.link(obj)

		# Deselect all
		for obj in context.scene.objects:
			obj.select = False
		context.scene.objects.active = None





	
	@classmethod
	def poll(self, context):
		return context.area.type == 'VIEW_3D'

	def modal(self, context, event):
		if event.type == 'ESC':
			self.stopOperator(context)
			print("Hiding menu.")
			return {'CANCELLED'}


		if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
			x_mouse_menu = event.mouse_x - self.viewport_x
			y_mouse_menu = self.viewport_h - (event.mouse_y - self.viewport_y)


			col = int(x_mouse_menu/(self.w_space+self.item_w))
			row = int(y_mouse_menu/(self.h_space+self.item_h))

			if 	(x_mouse_menu >= (self.w_space+self.item_w)*(min(0,col-1)) + self.w_space and
				y_mouse_menu >= (self.h_space+self.item_h)*(min(0,row-1)) + self.item_h):
				self.selectedObject = int(col) + int(row*self.menu_size)
			else:
				self.selectedObject = -1

			context.area.tag_redraw()

			if self.selectedObject >= 0 and self.selectedObject < len(self.objects):
				self.loadObject(context, self.objects[self.selectedObject])
				self.stopOperator(context)
				return {'FINISHED'}


			print("Selected item [%d,%d]: %d"%(col, row,self.selectedObject))


		return {'PASS_THROUGH'}



	def execute(self, context):
		global showing_menu
		if showing_menu:
			print("Menu already displayed")
			return{'CANCELLED'}

		print("Diplaying menu")

		self.init(context)

		showing_menu = True
		
		context.window_manager.modal_handler_add(self)

		self.display_menu_handler = bpy.types.SpaceView3D.draw_handler_add(self.dipslay_menu, (context,), 'WINDOW', 'POST_PIXEL')

		context.area.tag_redraw()

		return {'RUNNING_MODAL'}

	def stopOperator(self,context):

		global showing_menu
		showing_menu = False



		if self.display_menu_handler is not None:
			bpy.types.SpaceView3D.draw_handler_remove(self.display_menu_handler, 'WINDOW')

		self.display_menu_handler = None

		context.area.tag_redraw()

		self.end()









