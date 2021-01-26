// Author: Axel Antoine
// https://axantoine.com
// 01/26/2021

// Loki, Inria project-team with Université de Lille
// within the Joint Research Unit UMR 9189 CNRS-Centrale
// Lille-Université de Lille, CRIStAL.
// https://loki.lille.inria.fr

// LICENCE: Licence.md

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