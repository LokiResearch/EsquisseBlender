// Author: Axel Antoine
// https://axantoine.com
// 01/26/2021

// Loki, Inria project-team with Université de Lille
// within the Joint Research Unit UMR 9189 CNRS-Centrale
// Lille-Université de Lille, CRIStAL.
// https://loki.lille.inria.fr

// LICENCE: Licence.md

%module mycgal

%{
#define SWIG_FILE_WITH_INIT
#include "Point.h"
#include "Hole.h"
#include "Segment.h"
#include "Region.h"
#include "mycgal.h"
%}

%ignore Point::Point(); 
%ignore Hole::Hole(); 
%ignore Segment::Segment(); 
%ignore Region::Region(); 

%include "std_vector.i"
namespace std
{
	%template(VectorPoint) vector<Point>;
	%template(VectorHole) vector<Hole>;
	%template(VectorRegion) vector<Region>;
	%template(VectorSegment) vector<Segment>;
}

%include "Point.h";
%include "Hole.h";
%include "Segment.h";
%include "Region.h";


std::vector<Region> computeRegions(std::vector<Segment> segments);


