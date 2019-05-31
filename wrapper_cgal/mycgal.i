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


