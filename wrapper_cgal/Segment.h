#ifndef _SEGMENT_H
#define _SEGMENT_H

#include "Point.h"

class Segment
{
public:
	Segment();
	Segment(Point _a, Point _b);
	~Segment();
	Point a;
	Point b;
};

#endif