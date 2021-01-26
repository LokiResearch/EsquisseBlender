# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import bgl
from mathutils import Vector
import math
from .FunctionsUtils import *

TEXTURE_NORMAL_FACTOR = 0.001
# CONTACT_POINTS_NORMAL_FACTOR = 0.002

def draw_in_view3D_callback():

	bgl.glEnable(bgl.GL_DEPTH_TEST)

	draw_interface_textures()
	
	bgl.glDisable(bgl.GL_DEPTH_TEST)


def draw_interface_textures():
	if bpy.context.scene.esquisse.is_rendering:
		return

	for obj in bpy.context.scene.objects:

		# Get screen objects
		if obj.esquisse.isScreen :
		
			# Draw upon the object 
			bot_left = obj.matrix_world * (obj.data.vertices[0].co + TEXTURE_NORMAL_FACTOR*obj.data.vertices[0].normal)
			bot_right = obj.matrix_world * (obj.data.vertices[1].co + TEXTURE_NORMAL_FACTOR*obj.data.vertices[1].normal)
			top_left = obj.matrix_world * (obj.data.vertices[2].co + TEXTURE_NORMAL_FACTOR*obj.data.vertices[2].normal)
			top_right = obj.matrix_world * (obj.data.vertices[3].co + TEXTURE_NORMAL_FACTOR*obj.data.vertices[3].normal)


			r,g,b = (1,1,1)
			if not obj.esquisse.screen_properties.use_interface or not obj.esquisse.screen_properties.texture_loaded:
				if len(obj.data.materials) > 0:
					r,g,b = obj.data.materials[0].diffuse_color

			bgl.glColor3f(r,g,b)

			# Draw a white rectangle before drawing SVG for transparancy 
			bgl.glColor3f(r,g,b)
			bgl.glBegin(bgl.GL_QUADS)
			bgl.glVertex3f(bot_left.x,bot_left.y,bot_left.z)
			bgl.glVertex3f(bot_right.x,bot_right.y,bot_right.z)
			bgl.glVertex3f(top_right.x,top_right.y,top_right.z)
			bgl.glVertex3f(top_left.x,top_left.y,top_left.z)
			bgl.glEnd()

			# Draw texture with transparency

			img = None
			if obj.esquisse.screen_properties.use_interface and obj.esquisse.screen_properties.texture_loaded:
				img = bpy.data.images[obj.esquisse.screen_properties.texture_id]
			else:
				img = bpy.data.images[obj.esquisse.screen_properties.default_texture_id]

			bgl.glColor3f(1,1,1)

			img.gl_load(bgl.GL_NEAREST, bgl.GL_NEAREST)
			bgl.glBindTexture(bgl.GL_TEXTURE_2D, img.bindcode[0])
			bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
			bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
			bgl.glEnable(bgl.GL_TEXTURE_2D)
			bgl.glEnable(bgl.GL_BLEND)


			bgl.glBegin(bgl.GL_QUADS)
			bgl.glTexCoord2f(0,0)
			bgl.glVertex3f(bot_left.x,bot_left.y,bot_left.z)

			bgl.glTexCoord2f(1,0)
			bgl.glVertex3f(bot_right.x,bot_right.y,bot_right.z)

			bgl.glTexCoord2f(1,1)
			bgl.glVertex3f(top_right.x,top_right.y,top_right.z)
	
			bgl.glTexCoord2f(0,1)
			bgl.glVertex3f(top_left.x,top_left.y,top_left.z)

			bgl.glEnd()
 
			bgl.glDisable(bgl.GL_BLEND)
			bgl.glDisable(bgl.GL_TEXTURE_2D)


callback = None

def register():	
	global callback
	callback = bpy.types.SpaceView3D.draw_handler_add(draw_in_view3D_callback, (), 'WINDOW', 'PRE_VIEW')


def unregister():
	bpy.types.SpaceView3D.draw_handler_remove(callback, 'WINDOW')





