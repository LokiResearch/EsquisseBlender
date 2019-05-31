import os
import sys
import bpy
import shutil
import re

addon_name = "Esquisse"

current_dir = os.path.dirname(os.path.abspath(__file__))
result_dir = current_dir + "/../Results/"
addon_archive =  addon_name + ".zip"

############## ADDON INSTALLATION ############

# Move to current dir
os.chdir(current_dir)

# Zip the addon code
shutil.make_archive(base_name = addon_name, format = 'zip', base_dir = addon_name, root_dir = '.')

# Install the addon in Blender (it auto copies the archive to the right local folder )
bpy.ops.wm.addon_install(overwrite = True, filepath = current_dir +"/"+ addon_archive)

# Remove the archive from the folder 
os.remove(current_dir +'/'+ addon_archive)

# Enable addon in Blender
bpy.ops.wm.addon_enable(module=addon_name)


# Set the default output results to the results folder in the parent directory (Can be changed here or manually in Blender)
bpy.context.scene.esquisse.SVG_output_path = result_dir + re.sub(r'\.blend$|$', '.svg' , bpy.path.basename(bpy.context.blend_data.filepath))

bpy.context.scene.esquisse.esquisse_library_path = '/Users/ax/Documents/Workspace/Esquisse/Esquisse_library'

# bpy.app.debug = True