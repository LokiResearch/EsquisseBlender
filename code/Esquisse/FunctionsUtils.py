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
from . import renderData
import math
from math import sqrt, pow
from mathutils import Vector


def isFrontFace(face):
	vv_dotProduct = viewVectorDotProduct(face.world_center, face.world_normal)
	return vv_dotProduct >= 0

def euclidianDistance(v1, v2):
	return sqrt( pow((v1.x-v2.x),2) + pow((v1.y-v2.y),2) + pow((v1.z-v2.z),2))

def viewVectorDotProduct(mesh_point_world_location, mesh_point_world_normal):
	objects_direction = (renderData.camera.location - mesh_point_world_location).normalized().to_3d()
	return objects_direction.dot(mesh_point_world_normal)


def localDirectionToWorldDirection(obj, local_direction):
	world_direction = local_direction.normalized().to_4d()
	world_direction.w = 0
	return (obj.matrix_world * world_direction).normalized().to_3d()

def localLocationToWorldLocation(obj, local_location):
	world_location = local_location.to_4d()
	world_location.w = 1
	return (obj.matrix_world * world_location).to_3d()

def convertWorld3DPointTo2DScreenPoint(point3D):
	p = renderData.modelViewProjectionMatrix * Vector((point3D.x, point3D.y, point3D.z, 1.0))
	ndc = (p/p.w).to_3d()
	screen_x = renderData.render_width/2 * (1 + ndc.x)
	screen_y = renderData.render_height/2 * (1 + ndc.y)
	return Vector((screen_x, screen_y, ndc.z))

def camera_z(point3D):
	p = renderData.modelViewProjectionMatrix * Vector((point3D.x, point3D.y, point3D.z, 1.0))
	return p.z / p.w

def connectedEdgesFromVertex_CCW(vertex):

	size = len(vertex.link_edges) 
	if size == 0 or size == 1:
		print("%d edge connected to the vertex. %d"%(size, vertex.index))
		return None

	vertex.link_edges.index_update()
	first_edge = vertex.link_edges[0]

	edges_CCW_order = []

	edge = first_edge
	while edge not in edges_CCW_order:
		edges_CCW_order.append(edge)
		edge = rightEdgeForEdgeRegardToVertex(edge, vertex)

	return edges_CCW_order


def rightEdgeForEdgeRegardToVertex(edge, vertex):
	right_loop = None

	if len(edge.link_loops) > 2:
		print("More than 2 faces connected to the edge %d."%edge.index)
		return None

	for loop in edge.link_loops:
		if loop.vert == vertex:
			right_loop = loop
			break
	return loop.link_loop_prev.edge


def is_contour_CCW(contour):
	size = len(contour)
	sum_ = 0
	for i in range(0,size):
		next_i = (i+1)%size
		xi, yi = contour[i]
		next_xi, next_yi = contour[next_i]
		sum_ += (next_xi - xi)*(next_yi + yi)
	return sum_ < 0


def get_avg_Z_plane(plane):
	avg_z = 0
	for v in plane.data.vertices:
		avg_z += camera_z(plane.matrix_world*v.co)
	avg_z /= len(plane.data.vertices)
	return avg_z

def getCircleArountCenterAndDirection(center, normal_world, radius, n_cuts):

	if normal_world.z == 0:
		return []

	a = a = Vector((1,1,-(normal_world.x+normal_world.y)/normal_world.z)).normalized()
	b = a.cross(normal_world)

	d_theta = 2 * math.pi / n_cuts
	points = []
	for i in range(0,n_cuts):
		theta = (i+1)*d_theta
		points.append(Vector((
						center.x + radius*math.cos(theta)*a.x + radius*math.sin(theta)*b.x,
						center.y + radius*math.cos(theta)*a.y + radius*math.sin(theta)*b.y,
						center.z + radius*math.cos(theta)*a.z + radius*math.sin(theta)*b.z)))
	return points















