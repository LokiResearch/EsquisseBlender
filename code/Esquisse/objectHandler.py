
class ObjectHandler():

	def __init__(self, mesh_object):
		self.mesh_object = mesh_object

		self.regions = []
		

		# Map of ghost handlers in fucntion of screenshots
		self.ghost_handlers = {}

		self.ghost_interpolations = {}



	def group_regions_per_color(self):

		sorted_regions = []
		for region in self.regions:
			found = False
			for group_regions in sorted_regions:
				if group_regions[0].color == region.color:
					group_regions.append(region)
					found = True
					break
			if not found:
				sorted_regions.append([region])

		return sorted_regions