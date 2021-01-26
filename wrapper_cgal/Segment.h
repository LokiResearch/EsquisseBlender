// Author: Axel Antoine
// https://axantoine.com
// 01/26/2021

// Loki, Inria project-team with Université de Lille
// within the Joint Research Unit UMR 9189 CNRS-Centrale
// Lille-Université de Lille, CRIStAL.
// https://loki.lille.inria.fr

// LICENCE: Licence.md

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