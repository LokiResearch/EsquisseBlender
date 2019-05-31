



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
