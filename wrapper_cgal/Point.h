// Author: Axel Antoine
// https://axantoine.com
// 01/26/2021

// Loki, Inria project-team with Université de Lille
// within the Joint Research Unit UMR 9189 CNRS-Centrale
// Lille-Université de Lille, CRIStAL.
// https://loki.lille.inria.fr

// LICENCE: Licence.md

#ifndef _POINT_H 
#define _POINT_H 

class Point 
{
public:
	Point();
	Point(double _x, double _y);
	~Point();
	double x;
	double y;
};

#endif