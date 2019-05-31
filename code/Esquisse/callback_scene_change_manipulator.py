import bpy


class Change3DManipulator(bpy.types.Operator):

	bl_idname = 'esquisse.manipulator'
	bl_label = 'Change 3D Manipulator for hands'

	@classmethod
	def poll(cls, context):
		return context.space_data.type == 'VIEW_3D'

	def invoke(self, context, event):

		if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
			
			if bpy.context.scene.objects.active:
				obj = bpy.context.scene.objects.active

				if obj.esquisse.isHand:

					# Get One anchor
					anchor = None
					for obj2 in bpy.context.scene.objects:
						if (obj2.esquisse.isAnchor) and obj2.esquisse.anchor_properties.constrained_object == obj and not 'none' in obj2.esquisse.anchor_properties.constrained_finger:
							anchor = obj2
							break

					if not anchor:
						views = [area.spaces.active for area in  bpy.context.screen.areas if area.type == 'VIEW_3D']
						for view in views:
							view.transform_orientation = 'GLOBAL'
					else:

							# Set the anchor as the active object
							bpy.context.scene.objects.active = anchor

							# Get the transform orientation of the active object (the anchor)
							if bpy.ops.transform.create_orientation.poll():
								bpy.ops.transform.create_orientation(name="SCREEN", use=True, overwrite=True)

								# Set hand as the active object again
								bpy.context.scene.objects.active = obj

								# Change the 3D manipulator to the new one just created
								views = [area.spaces.active for area in  bpy.context.screen.areas if area.type == 'VIEW_3D']
								for view in views:
									view.transform_orientation = 'SCREEN'

				elif obj.esquisse.isAnchor:

					views = [area.spaces.active for area in  bpy.context.screen.areas if area.type == 'VIEW_3D']
					for view in views:
						view.transform_orientation = 'LOCAL'


		return {'FINISHED'}




def register():

	wm = bpy.context.window_manager
	kc = wm.keyconfigs['Blender User']
	km = kc.keymaps['3D View']


	kmi = km.keymap_items.new(Change3DManipulator.bl_idname, 'RIGHTMOUSE', 'PRESS')


	
