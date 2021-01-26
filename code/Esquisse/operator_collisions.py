# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md
import bpy
import bmesh
import math

from mathutils.bvhtree import BVHTree

from Esquisse.cgal import mycgal as mycgal

#================================================
#   Collision detection Operator
#================================================

class EsquisseCollisionDetectionOperator(bpy.types.Operator):

	bl_idname = "esquisse.collision_detection"
	bl_label = "Esquisse Collision Detection Operator"
	bl_description = "Detect the collision for each objects in the scene"

	#============================================

	def execute(self, context):
		objs = self._get_object_in_scene(context)

		already_tested = []
		found_collision = False
		for o1 in objs:
			already_tested += [o1]
			m1 = self._make_mesh_from_blender(o1)

			for o2 in objs:
				if o1 != o2 and o2 not in already_tested:
					m2 = self._make_mesh_from_blender(o2)
					if mycgal.collision_test_with_tree(m1, m2):
						self.report({'INFO'}, ("There is a collision between the meshes : '" + o1.name + "' and '" + o2.name + "' !"))
						found_collision = True

		if not found_collision:
			self.report({'INFO'}, "No collisions found.")

		return {'FINISHED'}

	#============================================

	def _get_object_in_scene(self, context):

		objects = []
		for obj in context.scene.objects:
			if obj.type == 'MESH':
				objects += [obj]

		return objects

	#============================================

	def _make_mesh_from_blender(self, obj):

		# apply modifiers :
		mesh = obj.to_mesh(bpy.context.scene, True, 'RENDER')

		# without modifiers :
		# mesh = obj.data

		mesh_triangles = []
		world_matrix = obj.matrix_world

		for polygon in mesh.polygons:

			if len(polygon.vertices) == 3:

				triangle = []
				for point_id in range(0, 3):
					poly_id = polygon.vertices[point_id]
					vertex = world_matrix * mesh.vertices[poly_id].co
					triangle += [mycgal.Point3(vertex[0], vertex[1], vertex[2])]

				mesh_triangles += [mycgal.Triangle(triangle[0], triangle[1], triangle[2])]

			elif len(polygon.vertices) == 4:

				triangle_a = []
				for point_id in range(0, 3):
					poly_id = polygon.vertices[point_id]
					vertex = world_matrix * mesh.vertices[poly_id].co
					triangle_a += [mycgal.Point3(vertex[0], vertex[1], vertex[2])]

				triangle_b = []
				for point_id in range(1, 4):
					poly_id = polygon.vertices[point_id]
					vertex = world_matrix * mesh.vertices[poly_id].co
					triangle_b += [mycgal.Point3(vertex[0], vertex[1], vertex[2])]

				mesh_triangles += [mycgal.Triangle(triangle_a[0], triangle_a[1], triangle_a[2])]
				mesh_triangles += [mycgal.Triangle(triangle_b[0], triangle_b[1], triangle_b[2])]

		return mesh_triangles

#================================================
#   Intersection detection Operator
#================================================

class EsquisseIntersectionDetectionOperator(bpy.types.Operator):

	bl_idname = "esquisse.intersection_detection"
	bl_label = "Esquisse Intersection Detection Operator"
	bl_description = "Detect the intersection fro each objects in the scene"

	#============================================

	def execute(self, context):
		#objs = bpy.data.meshes
		#objs = bpy.data.objects
		#objs = bpy.data.node_groups
		objs = self._get_object_in_scene(context)

		if len(objs) < 2:

			self.report({'ERROR'}, "Only one mesh in the scene")
			return {'CANCELLED'}
		meshes = []

		self.report({'INFO'}, "ROUTINE")

		for obj in objs:
			meshes += [self._make_mesh_from_blender(obj)]

		self._check_intersections(meshes)
		#self._check_sollisions(meshes)

		return {'FINISHED'}

	#============================================

	def _get_object_in_scene(self, context):

		objects = []
		for obj in context.scene.objects:
			if obj.type == 'MESH':
				objects += [obj]

		return objects

	#============================================

	def _make_mesh_from_blender(self, obj):

		# apply modifiers :
		mesh = obj.to_mesh(bpy.context.scene, True, 'RENDER')

		# without modifiers :
		#mesh = obj.data

		mesh_triangles = []
		world_matrix = obj.matrix_world

		for polygon in mesh.polygons:

			if len(polygon.vertices) == 3:

				triangle = []
				for point_id in range(0, 3):
					poly_id = polygon.vertices[point_id]
					vertex = world_matrix * mesh.vertices[poly_id].co
					triangle += [mycgal.Point3(vertex[0], vertex[1], vertex[2])]

				mesh_triangles += [mycgal.Triangle(triangle[0], triangle[1], triangle[2])]

			elif len(polygon.vertices) == 4:

				triangle_a = []
				for point_id in range(0, 3):
					poly_id = polygon.vertices[point_id]
					vertex = world_matrix * mesh.vertices[poly_id].co
					triangle_a += [mycgal.Point3(vertex[0], vertex[1], vertex[2])]

				triangle_b = []
				for point_id in range(1, 4):
					poly_id = polygon.vertices[point_id]
					vertex = world_matrix * mesh.vertices[poly_id].co
					triangle_b += [mycgal.Point3(vertex[0], vertex[1], vertex[2])]

				mesh_triangles += [mycgal.Triangle(triangle_a[0], triangle_a[1], triangle_a[2])]
				mesh_triangles += [mycgal.Triangle(triangle_b[0], triangle_b[1], triangle_b[2])]

		return mesh_triangles

	#============================================

	def _check_intersections(self, meshes):
		recorded_intersections = []

		already_tested = []
		for o1 in meshes:
			if o1 not in already_tested:
				already_tested += [o1]
				for o2 in meshes:
					if o2 not in already_tested and o1 != o2:
						if mycgal.collision_test_with_tree(o1, o2):
							intersections = mycgal.collision_test_with_exact_intersections(o1, o2)
							if len(intersections.points) != 0 or len(intersections.segments) != 0 or len(intersections.triangles) != 0:
								recorded_intersections += [intersections]

		if len(recorded_intersections) == 0:
			self.report({'INFO'}, "There is no intersections")
		else:
			self.report({'INFO'}, "There is intersections")

		for intersections in recorded_intersections:
			self._process_intersections(intersections)

	#============================================

	def _process_intersections(self, intersections):

		# Get all points :
		points = []

		for point in intersections.points:
			points += [point]

		for segment in intersections.segments:
			x = (segment.a.x + segment.b.x) / 2
			y = (segment.a.y + segment.b.y) / 2
			z = (segment.a.z + segment.b.z) / 2
			
			points += [mycgal.Point3(x,y,z)]

		for triangle in intersections.triangles:
			x = (triangle.a.x + triangle.b.x + triangle.c.x) / 3
			y = (triangle.a.y + triangle.b.y + triangle.c.y) / 3
			z = (triangle.a.z + triangle.b.z + triangle.c.z) / 3
			
			points += [mycgal.Point3(x,y,z)]
			
		# Determine joined points :
		epsilon_distance = 5

		current_label = 0
		labels = dict()
		group = dict()

		length = 0

		for p in points:
			if p not in labels:
				labels[p] = current_label
				group[current_label] = []
				group[current_label] += [p]
				for pi in points:
					if p != pi:
						length = max(self._distance_points(p, pi), length)
						if self._distance_points(p, pi) < epsilon_distance:
							labels[pi] = current_label
							group[current_label] += [pi]

			current_label += 1

		# Add spheres :
		for i in group:
			pts = group[i]

			x, y, z = 0, 0, 0
			for p in pts:
				x += p.x
				y += p.y
				z += p.z

			x /= len(pts)
			y /= len(pts)
			z /= len(pts)

			self._create_sphere((x, y, z), length + 0.5)

	#============================================

	def _distance_points(self, a, b):
		return math.sqrt(abs(a.x - b.x) ** 2 + abs(a.y - b.y) ** 2 + abs(a.z - b.z) ** 2)


	#============================================

	def _create_sphere(self, position, d):
		bpyscene = bpy.context.scene

		# Create an empty mesh and the object.
		mesh = bpy.data.meshes.new('Collision_Sphere')
		basic_sphere = bpy.data.objects.new("Collision_Sphere", mesh)

		# Add the object into the scene.
		bpyscene.objects.link(basic_sphere)
		bpyscene.objects.active = basic_sphere
		basic_sphere.select = True
		basic_sphere.location = position

		# Construct the bmesh sphere and assign it to the blender mesh.
		bm = bmesh.new()
		bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=d)
		bm.to_mesh(mesh)
		bm.free()

		bpy.ops.object.modifier_add(type='SUBSURF')
		bpy.ops.object.shade_smooth()

		basic_sphere.active_material.diffuse_color = (1,0,0)


#================================================
# Remove Sphere Operator
#================================================

class EsquisseRemoveSphereOperator(bpy.types.Operator):
	bl_idname = "esquisse.remove_sphere"
	bl_label = "Remove collision sphere"

	#============================================

	def execute(self, context):

		for msh in bpy.data.meshes:
			if "Collision_Sphere" in msh.name:
				bpy.data.meshes.remove(msh)

		self.report({'INFO'}, "Collision sphere has been removed")
		return {'FINISHED'}

#================================================
