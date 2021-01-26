// Author: Axel Antoine
// https://axantoine.com
// 01/26/2021

// Loki, Inria project-team with Université de Lille
// within the Joint Research Unit UMR 9189 CNRS-Centrale
// Lille-Université de Lille, CRIStAL.
// https://loki.lille.inria.fr

// LICENCE: Licence.md

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
