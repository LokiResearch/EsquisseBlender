#include "Region.h"
#include <stdlib.h>

Region::Region() {}

Region::Region(std::vector<Point> _contour, std::vector<Hole> _holes) : contour(_contour), holes(_holes) 
{
	// int n_vertices = this->contour.size();

	// gpc_vertex_list* vertex_list = new gpc_vertex_list();
	// gpc_vertex* vertices = new gpc_vertex[n_vertices]();

	// for (int i=0; i<n_vertices; i++)
	// {
	// 	gpc_vertex v;
	// 	v.x = contour[i].x; v.y = contour[i].y;
	// 	vertices[i] = v;
	// }

	// vertex_list->num_vertices = n_vertices;
	// vertex_list->vertex = vertices;

	// gpc_add_contour(this->poly, vertex_list, 0);


	// int n_hole = this->holes.size();

	// for (int i=0; i<n_hole; i++)
	// {
	// 	n_vertices = this->holes[i].contour.size();
	// 	vertex_list = new gpc_vertex_list();
	// 	vertices = new gpc_vertex[n_vertices]();

	// 	for (int j=0; j<n_vertices; j++)
	// 	{
	// 		gpc_vertex v;
	// 		v.x = this->holes[i].contour[j].x; v.y = this->holes[i].contour[j].y;
	// 		vertices[j] = v;
	// 	}

	// 	vertex_list->num_vertices = n_vertices;
	// 	vertex_list->vertex = vertices;

	// 	gpc_add_contour(this->poly, vertex_list, 1);
	// }
}

Region::~Region() 
{
	// free(this->poly);
}

// Point Regionb::getPointInRegion()
// {
// 	Point p;


// 	return p;
// }
