import bpy

from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Panel, Operator, AddonPreferences, PropertyGroup, BlendData, UIList
from .GhostProperties import *

class EsquissePanel(bpy.types.Panel):
	bl_idname = "esquisse_panel"
	bl_label = "Esquisse"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Esquisse"

	def draw(self, context):

		self.esquisse = context.scene.esquisse
		self.panelProperties = context.scene.esquissePanelProperties

		self.draw_library_panel(context)
		self.draw_screens_panel(context)
		self.draw_anchors_panel(context)
		self.draw_hands_panel(context)
		self.draw_character_panel(context)
		self.draw_objects_color_panel(context)
		self.draw_SVG_settings_panel(context)
		self.draw_camera_panel(context)
		self.draw_render_panel(context)
		self.draw_ghost_panel(context)


	def draw_library_panel(self, context):

		library_box = self.layout.box()
		header_row = library_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_library_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_library_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_library_panel", icon="DISK_DRIVE", text="Esquisse Library", emboss=False)

		if self.panelProperties.expand_library_panel:

			row = library_box.row(True)
			row.prop(self.esquisse, 'esquisse_library_path' , text="Esquisse Folder path")

			if (self.esquisse.esquisse_library_path.endswith('Esquisse_library') or 
				self.esquisse.esquisse_library_path.endswith('Esquisse_library/')):
				row = library_box.row(True)
				col = row.column(True)
				col.operator('esquisse.showtemplatesmenu', icon= "SCENE_DATA", text="Load Templates")
				col = row.column(True)
				col.operator('esquisse.show_objects_library_menu', icon = "MESH_CUBE", text="Add Object")


			library_box.prop(self.esquisse, "ease_blender_controls")


	def draw_screens_panel(self, context):

		screens_box = self.layout.box()
		header_row = screens_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_screens_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_screens_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_screens_panel", icon="FACESEL_HLT", text="Screens", emboss=False)
		

		if self.panelProperties.expand_screens_panel:

			for obj in bpy.context.scene.objects:
				if obj.esquisse.isScreen:

					screen_box = screens_box.box()
					row = screen_box.row(True)
					row.prop(obj.esquisse, "expand_properties", icon="DOWNARROW_HLT" if obj.esquisse.expand_properties else "RIGHTARROW", icon_only=True, emboss=False)
					row.prop(obj.esquisse, "expand_properties", text = obj.name if not obj.parent else '%s [%s]'%(obj.name,obj.parent.name), emboss=False)
					row.operator('esquisse.identify_object', icon = 'RESTRICT_SELECT_OFF', text="", emboss=False).obj_name = obj.name

					if obj.esquisse.expand_properties:
						row = screen_box.row(True)
						row.prop(obj.esquisse.screen_properties, "use_interface", text="Add Interface", icon = "FILE_IMAGE")
						if obj.esquisse.screen_properties.use_interface:
							row.prop(obj.esquisse.screen_properties, "interface_path", text="")


						# Transparent screen
						# if obj.parent:
						# 	transparent_row = screen_box.row(True)
						# 	transparent_row.prop(obj.parent.esquisse, 'transparent', text="Transparent")
						# 	if obj.parent.esquisse.transparent:
						# 		transparent_row.prop(obj.parent.esquisse, 'transparency', text="transparency")
						# 		transparent_row.prop(obj.parent.esquisse, 'make_visible_hidden_contours_transparent', text="Make visible the hidden contours")	

						
						# Anchors
						# has_anchors = False
						# for child in obj.children:
						# 	if child.esquisse.isAnchor and not child.esquisse.isGhost:
						# 		has_anchors = True
						# 		break

						# if has_anchors:
						# 	anchors_box = screen_box.box()
						# 	anchors_box.label("Anchors:", icon = "UNPINNED")

						# 	# Draw anchor lines
						# 	for child in obj.children:
						# 		if child.esquisse.isAnchor and not child.esquisse.isGhost:
						# 			row = anchors_box.row(True)
						# 			row.prop(child.esquisse.anchor_properties, "radius")
						# 			row.prop(child.data.materials[0], "diffuse_color", text = "")
						# 			row.prop(child.esquisse.anchor_properties, "constrained_object", text = "")
						# 			if child.esquisse.anchor_properties.constrained_object:
						# 				row.prop(child.esquisse.anchor_properties, "constrained_finger", text = "")
						# 				row.prop(child.esquisse.anchor_properties, 'constraint_type', text = "")

						# 			row.operator('esquisse.identify_object', icon = 'RESTRICT_SELECT_OFF', text="", emboss=False).obj_name = child.name
						# 			op = row.operator('esquisse.remove_anchor', icon = 'X', text="", emboss=False).anchor_name = child.name

		
	def draw_anchors_panel(self, context):
		anchors_box = self.layout.box()
		header_row = anchors_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_anchors_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_anchors_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_anchors_panel", icon="UNPINNED", text="Anchors", emboss=False)



		if self.panelProperties.expand_anchors_panel:

			row = anchors_box.row(True)	
			row.operator('esquisse.add_anchor', text="New Anchor", icon="UNPINNED")


			for obj in context.scene.objects:
				if obj.esquisse.isAnchor:
					row = anchors_box.row(True)
					row.prop(obj.esquisse.anchor_properties, "radius")
					row.prop(obj.data.materials[0], "diffuse_color", text = "")
					row.prop(obj.esquisse.anchor_properties, "constrained_object", text = "")
					if obj.esquisse.anchor_properties.constrained_object:
						row.prop(obj.esquisse.anchor_properties, "constrained_finger", text = "")
						row.prop(obj.esquisse.anchor_properties, 'constraint_type', text = "")

					row.operator('esquisse.identify_object', icon = 'RESTRICT_SELECT_OFF', text="", emboss=False).obj_name = obj.name
					row.prop(obj, 'hide_render', emboss = False, text='')
					op = row.operator('esquisse.remove_anchor', icon = 'X', text="", emboss=False).anchor_name = obj.name




	def draw_hands_panel(self, context):
		hands_box = self.layout.box()
		header_row = hands_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_hands_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_hands_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_hands_panel", icon="HAND", text="Hands", emboss=False)

		
		if self.panelProperties.expand_hands_panel:
			
			for obj in bpy.context.scene.objects:
				if obj.esquisse.isHand:
					hand_box = hands_box.box()
					row = hand_box.row(True)
					row.prop(obj.esquisse, "expand_properties", icon="DOWNARROW_HLT" if obj.esquisse.expand_properties else "RIGHTARROW", icon_only=True, emboss=False)
					row.prop(obj.esquisse, "expand_properties", text = obj.name, emboss=False)
					row.operator('esquisse.identify_object', icon = 'RESTRICT_SELECT_OFF', text="", emboss=False).obj_name = obj.name

					if obj.esquisse.expand_properties:

						# Draw opeing/closing finger properties
						row = hand_box.row(True)
						row.label("Fingers flexion / extension")
						row = hand_box.row(True)
						row.prop(obj.esquisse.hand_properties, "thumb_opening", text="thumb")
						row.prop(obj.esquisse.hand_properties, "index_opening", text="index")
						row.prop(obj.esquisse.hand_properties, "middle_opening", text="middle")
						row.prop(obj.esquisse.hand_properties, "ring_opening", text="ring")
						row.prop(obj.esquisse.hand_properties, "pinky_opening", text="pinky")

						# Draw operators for the hand
						hand_operators_row = hand_box.row(True)
						hand_operators_row.operator('esquisse.reset_pose_operator', text="Reset Pose", icon="MOD_ARMATURE").obj_name = obj.name
						hand_operators_row.operator('esquisse.apply_constraints_to_pose', text="Apply Constraints", icon="CONSTRAINT_DATA").obj_name = obj.name

	
	
	def draw_character_panel(self, context):
		characters_box = self.layout.box()
		header_row = characters_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_character_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_character_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_character_panel", icon="MOD_ARMATURE", text="Characters", emboss=False)
		
		if self.panelProperties.expand_character_panel:
			
			for obj in bpy.context.scene.objects:
				if obj.esquisse.isCharacter:
					character_box = characters_box.box()
					row = character_box.row(True)
					row.prop(obj.esquisse, "expand_properties", icon="DOWNARROW_HLT" if obj.esquisse.expand_properties else "RIGHTARROW", icon_only=True, emboss=False)
					row.prop(obj.esquisse, "expand_properties", text = obj.name, emboss=False)
					row.operator('esquisse.identify_object', icon = 'RESTRICT_SELECT_OFF', text="", emboss=False).obj_name = obj.name

					if obj.esquisse.expand_properties:

						# Left Hand
						row = character_box.row(True)
						row.label("Left Hand Fingers flexion / extension")
						row = character_box.row(True)
						row.prop(obj.esquisse.character_properties, "L_thumb_opening", text="thumb")
						row.prop(obj.esquisse.character_properties, "L_index_opening", text="index")
						row.prop(obj.esquisse.character_properties, "L_middle_opening", text="middle")
						row.prop(obj.esquisse.character_properties, "L_ring_opening", text="ring")
						row.prop(obj.esquisse.character_properties, "L_pinky_opening", text="pinky")

						# Right Hand
						row = character_box.row(True)
						row.label("Right Hand Fingers flexion / extension")
						row = character_box.row(True)
						row.prop(obj.esquisse.character_properties, "R_thumb_opening", text="thumb")
						row.prop(obj.esquisse.character_properties, "R_index_opening", text="index")
						row.prop(obj.esquisse.character_properties, "R_middle_opening", text="middle")
						row.prop(obj.esquisse.character_properties, "R_ring_opening", text="ring")
						row.prop(obj.esquisse.character_properties, "R_pinky_opening", text="pinky")

						# Head
						row = character_box.row(True)
						row.label("Head")
						row = character_box.row(True)
						row.prop(obj.esquisse.character_properties, "head_top_bottom", text="Top/Bottom")
						row.prop(obj.esquisse.character_properties, "head_left_right", text="Left/Right")

						# Back
						row = character_box.row(True)
						row.label("Back")
						row.prop(obj.esquisse.character_properties, "back_upward_backward", text="Upward/Backward")

						# Operators
						row = character_box.row(True)
						row.operator('esquisse.reset_pose_operator', text="Reset Pose", icon="MOD_ARMATURE").obj_name = obj.name
						row.operator('esquisse.apply_constraints_to_pose', text="Apply Constraints", icon="CONSTRAINT_DATA").obj_name = obj.name

	def draw_objects_color_panel(self, context):
		# Objects color:
		color_box = self.layout.box()
		header_row = color_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_objects_color_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_objects_color_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_objects_color_panel", icon="COLOR", text="Colors", emboss=False)

		if self.panelProperties.expand_objects_color_panel:	
			color_box.template_list("ObjectsColorList", "", context.scene, "objects", self.esquisse, "useless", rows = 3)


	def draw_SVG_settings_panel(self, context):
		# SVG Settings :
		svg_box = self.layout.box()
		header_row = svg_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_SVG_settings_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_SVG_settings_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_SVG_settings_panel", icon="SCRIPTWIN", text="SVG Lines Style", emboss=False)

		if self.panelProperties.expand_SVG_settings_panel:
			# Screens settings:
			#screens_box = svg_box.box()
			#screens_box.prop(self.esquisse, "render_screens", text="Render Screens")
			

			# Fills settings
			#fills_box = svg_box.box()
			#fills_box.prop(self.esquisse, "render_fills", text="Render Fills")


			# Visible Strokes settings
			visible_box = svg_box.box()
			visible_box.prop(self.esquisse, "render_visible_strokes", text="Render Visible Strokes")
			if self.esquisse.render_visible_strokes:
				row = visible_box.row(True)
				col = row.column(True)
				col.prop(self.esquisse, "visible_strokes_color", text = "")
				col = row.column(True)
				col.prop(self.esquisse, "visible_strokes_width", text="width")
				row = visible_box.row(True)
				row.prop(self.esquisse, "visible_strokes_style", text="Style")
				if self.esquisse.visible_strokes_style in "DASHED":
					row = visible_box.row(True)
					col = row.column(True)
					col.prop(self.esquisse, "plain_dashed_value_visible_strokes", text = "Plain")
					col = row.column(True)
					col.prop(self.esquisse, "space_dashed_value_visible_strokes", text = "Space")



			# Hidden Strokes settings
			hidden_box = svg_box.box()
			hidden_box.prop(self.esquisse, "render_hidden_strokes", text="Render Hidden Strokes")
			if self.esquisse.render_hidden_strokes:
				row = hidden_box.row(True)
				col = row.column(True)
				col.prop(self.esquisse, "hidden_strokes_color", text = "")
				col = row.column(True)
				col.prop(self.esquisse, "hidden_strokes_width", text="width")
				row = hidden_box.row(True)
				row.prop(self.esquisse, "hidden_strokes_style", text="Style")
				if self.esquisse.hidden_strokes_style in "DASHED":
					row = hidden_box.row(True)
					col = row.column(True)
					col.prop(self.esquisse, "plain_dashed_value_hidden_strokes", text = "Plain")
					col = row.column(True)
					col.prop(self.esquisse, "space_dashed_value_hidden_strokes", text = "Space")


	def draw_camera_panel(self, context):
		# Camera Settings
		camera_box = self.layout.box()
		header_row = camera_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_camera_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_camera_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_camera_panel", icon="CAMERA_DATA", text="Camera Settings", emboss=False)

		if self.panelProperties.expand_camera_panel:
			row = camera_box.row(True)
			row.label('Aspect')
			# row.prop(context.scene.render,'resolution_x')
			#row.prop(context.scene.render,'resolution_y')
			row.prop(context.scene.esquisse, 'camera_aspect')
			
			if context.scene.camera:
				row.label('Lens')
				row.prop(context.scene.camera.data,'lens')
				#row.prop(context.scene.camera.data,'shift_x')
				#row.prop(context.scene.camera.data,'shift_y')


			row = camera_box.row(True)
			row.operator("view3d.camera_to_view", icon = 'OUTLINER_DATA_CAMERA', text= 'Move camera to view')
			view3d = get_3d_view()
			
			if view3d and view3d.region_3d.view_perspective == 'CAMERA':
				row.operator("view3d.viewnumpad", icon='SCENE', text="Scene View").type = 'CAMERA'
			else:
				row.operator("view3d.viewnumpad", icon='SCENE', text="Camera View").type = 'CAMERA'


	
	def draw_render_panel(self, context):
		# Render settings
		render_box = self.layout.box()
		header_row = render_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_render_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_render_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_render_panel", icon="RENDER_ANIMATION", text="Render", emboss=False)

		if self.panelProperties.expand_render_panel:
			row = render_box.row(True)
			row.prop(self.esquisse, "SVG_output_path", text="SVG output path")

			row = render_box.row(True)
			row.operator("esquisse.renderstill", icon='RENDER_ANIMATION', text="Render Still Image")
			row.operator("esquisse.renderghost", icon='RENDER_ANIMATION', text="Render Stroboscopic Image")
	
	def draw_ghost_panel(self, context):
		# Ghost settings
		ghost_box = self.layout.box()
		header_row = ghost_box.row(True)
		header_row.alignment = 'LEFT'
		header_row.prop(self.panelProperties, "expand_ghost_panel", icon="DOWNARROW_HLT" if self.panelProperties.expand_ghost_panel else "RIGHTARROW", icon_only=True, emboss=False)
		header_row.prop(self.panelProperties, "expand_ghost_panel", icon="GHOST_ENABLED", text="Stroboscopic Effect", emboss=False)

		if self.panelProperties.expand_ghost_panel:


			row = ghost_box.row(True)
			row.prop(self.esquisse, "ghost_mode_enable", text="Keyframe Mode")

			if self.esquisse.ghost_mode_enable:
				row.operator("esquisse.add_ghost_screenshot", icon='RENDER_ANIMATION', text="Add keyframe")

			row = ghost_box.row(True)
			row.template_list("GhostScreenshotsList", "", self.esquisse, "ghost_screenshots_list", self.esquisse, "useless", rows = 3)
			

class EsquissePanelProperties(PropertyGroup):

	expand_library_panel = BoolProperty(default = True)
	expand_screens_panel = BoolProperty(default = False)
	expand_hands_panel = BoolProperty(default = False)
	expand_character_panel = BoolProperty(default = False)
	expand_SVG_settings_panel = BoolProperty(default = False)
	expand_objects_color_panel = BoolProperty(default = False)
	expand_camera_panel = BoolProperty(default = True)
	expand_ghost_panel = BoolProperty(default = True)
	expand_render_panel = BoolProperty(default = True)
	expand_anchors_panel = BoolProperty(default = True)

class ObjectsColorList(bpy.types.UIList):

	VGROUP_EMPTY = 1 << 0

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		obj = item
		layout.label(obj.name)

		if len(obj.data.materials) > 0:
			for material in obj.data.materials:
				layout.prop(material,'diffuse_color', icon_only=True)


	# Here we filter only mesh objects
	def filter_items(self, context, data, propname):

		# Default return values.
		flt_flags = []
		flt_neworder = []

		objects = getattr(data, propname)

		if not flt_flags:
			flt_flags = [self.bitflag_filter_item] * len(objects)

		cpt = 0
		for obj in objects:
			if not obj.type == 'MESH' or obj.esquisse.isAnchor or obj.esquisse.isGhost:
				flt_flags[cpt] &= ~self.bitflag_filter_item 
			cpt +=1

		return flt_flags, flt_neworder


class GhostScreenshotsList(bpy.types.UIList):

	VGROUP_EMPTY = 1 << 0

	def draw_item(self, context, layout, data, screenshot, icon, active_data, active_propname):
		layout.label("State "+str(screenshot.number))



		layout.prop(screenshot, "use_interpolation")

		if screenshot.use_interpolation:
			layout.prop(screenshot, "number_of_interpolation")

		op = layout.prop(screenshot, "show_ghosts_in_scene", icon = "RESTRICT_VIEW_OFF" if screenshot.show_ghosts_in_scene else "RESTRICT_VIEW_ON", icon_only=True, emboss = False)
		op = layout.operator("esquisse.remove_ghost_screenshot", icon='X', text="", emboss = False)
		op.screenshot_number = screenshot.number




def area_of_type(type_name):
	for area in bpy.context.screen.areas:
		if area.type == type_name:
			return area
	return None

def get_3d_view():
	return area_of_type('VIEW_3D').spaces[0]



def register():
	bpy.types.Scene.esquissePanelProperties = PointerProperty(type=EsquissePanelProperties)

def unregister():
	del bpy.types.Scene.esquissePanelProperties





