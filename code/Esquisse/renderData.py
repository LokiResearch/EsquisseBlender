# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md





scene = None
render_width = None
render_height = None
modelViewMatrix = None
projectionMatrix = None
modelViewProjectionMatrix = None
meshObjects = []
camera = None
screenObjects = []
freestyle_visible_lines = []
freestyle_hidden_lines = []
freestyle_all_lines = []


def reset():

	global scene 
	global width 
	global height 
	global modelViewMatrix 
	global projectionMatrix 
	global modelViewProjectionMatrix 
	global meshObjects
	global camera 
	global screenObjects
	global freestyle_visible_lines
	global freestyle_hidden_lines
	global freestyle_all_lines

	scene = None
	render_width = None
	render_height = None
	modelViewMatrix = None
	projectionMatrix = None
	modelViewProjectionMatrix = None
	meshObjects = []
	camera = None
	screenObjects = []
	freestyle_visible_lines = []
	freestyle_hidden_lines = []
	freestyle_all_lines = []
