#ifndef _REGION_H 
#define _REGION_H 

#include "Point.h"
#include "Hole.h"
#include "gpc.h"
#include <vector>

class Region
{
public:
	Region();
	Region(std::vector<Point> _contour, 	std::vector<Hole> _holes);
	~Region();
	std::vector<Point> contour;
	std::vector<Hole> holes;
	// gpc_polygon* poly;
	// Point getPointInRegion();
};

#endif
