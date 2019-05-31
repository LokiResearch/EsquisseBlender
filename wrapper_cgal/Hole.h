#ifndef _HOLE_H 
#define _HOLE_H 

#include "Point.h"
#include <vector>

class Hole
{
public:
	Hole();
	Hole(std::vector<Point> _contour);
	~Hole();
	std::vector<Point> contour;
};

#endif