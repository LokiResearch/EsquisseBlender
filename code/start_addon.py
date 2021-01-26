# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import os
import sys
import bpy
import shutil
import re

addon_name = "Esquisse"

current_dir = os.path.dirname(os.path.abspath(__file__))
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


# bpy.app.debug = True