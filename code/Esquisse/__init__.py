# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md



bl_info = {
    "name": "Esquisse",
    "description": "Generating SVG files from 3D scenes",
    "author": "Anonymous",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "category": "Render" }


# load and reload submodules
##################################
import bpy
import os
import sys
import pkgutil
import importlib
import ctypes

def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon.

    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py

  
    """
    def get_submodule_names(path = path[0], root = ""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            else:
                module_names.append(root + module_name)
        return module_names

    def import_submodules(names):
        modules = []
        for name in names:
            modules.append(importlib.import_module("." + name, package_name))
        return modules

    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)

    names = get_submodule_names()
    modules = import_submodules(names)
    if reload:
        reload_modules(modules)
    return modules

modules = setup_addon_modules(__path__, __name__, "bpy" in locals())

# register
##################################

import traceback

def register():

    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    for module in modules:
        try : module.register()
        except: pass

    #print("Registered {} with {} modules".format(bl_info["name"], len(modules)))


def unregister():

    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    for module in modules:
        try: module.unregister()
        except: pass

    #print("Unregistered {}".format(bl_info["name"]))













