# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import os
from bpy.app.handlers import persistent
import bgl

SCREEN_TAG = "EScreen"

@persistent
def detect_interface_callback(dummy):
	if bpy.context.scene.esquisse.is_rendering:
		return
		
	for obj in bpy.context.scene.objects:
		if obj.esquisse.isScreen :
			if obj.esquisse.screen_properties.use_interface:
				
				texture_path = bpy.path.abspath(obj.esquisse.screen_properties.interface_path)[:-3] + "png"

				if not obj.esquisse.screen_properties.texture_loaded:
					# Try to load the texture (PNG) with the same interface name

					# Check if file exists
					if os.path.isfile(texture_path):

						# Load the texture in the blender data
						texture =  bpy.data.images.load(texture_path)

						# Iterate over the current images stored in blender to get the key of the new image (should be filename, but not sure)
						texture_id = None
						for item in bpy.data.images.items():
							key, value = item
							if value == texture:
								texture_id = key
								break

						# Set the texture as loaded
						obj.esquisse.screen_properties.texture_loaded = True
						# Set the texture identifier of blender data images
						obj.esquisse.screen_properties.texture_id = texture_id

						print("Loaded %s texture in blender images for screen : %s."%(texture_id,obj.name))

				else:
					# Check if the loaded texture for the screen still has changed or is still loaded
					if obj.esquisse.screen_properties.texture_id not in bpy.data.images.keys():
						# Delete current texture identifier in blender data
						obj.esquisse.screen_properties.texture_id = ""
						# Set the texture for the current screen obj as not loaded to be loaded in the next function callback call
						obj.esquisse.screen_properties.texture_loaded = False
						break

					# get the filepath of the current texture stored in blender data for the current screen obj

					loaded_texture = bpy.data.images[obj.esquisse.screen_properties.texture_id]

					# check if the current screen obj interface path is the same stored in blender data
					if not loaded_texture.filepath == texture_path:

						# If filepath different, then it's a different texture
						# Remove texture from blender data
						bpy.data.images.remove(loaded_texture)
						# Delete current texture identifier in blender data
						obj.esquisse.screen_properties.texture_id = ""
						# Set the texture for the current screen obj as not loaded to be loaded in the next function callback call
						obj.esquisse.screen_properties.texture_loaded = False

@persistent
def load_default_interface(dummy):
	dir_path = os.path.dirname(os.path.realpath(__file__))
	filename = 'Esquisse_Default_interface.png'
	texture_path = dir_path +"/" + filename
	if not os.path.exists(texture_path):
		print("Can't find default interface %s", texture_path)		
		return

	texture = None
	if filename not in bpy.data.images.keys():
		texture = bpy.data.images.load(texture_path)

	for obj in bpy.context.scene.objects:
		if obj.esquisse.isScreen:
			obj.esquisse.screen_properties.default_texture_id = filename




def register():	
	bpy.app.handlers.scene_update_post.append(detect_interface_callback)
	bpy.app.handlers.scene_update_post.append(load_default_interface)
	

def unregister():
	bpy.app.handlers.scene_update_post.remove(detect_interface_callback)
	bpy.app.handlers.scene_update_post.remove(load_default_interface)

