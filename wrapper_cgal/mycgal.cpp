#include "mycgal.h"
#include <iostream>
#include <math.h>

double distanceBetween(double x1, double y1, double x2, double y2)
{
	return sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2));
} 

std::vector<Region> computeRegions(std::vector<Segment> segments)
{
	// std::cout << "Computing CGAL regions" << std::endl;
	// std::cout << "Input segments:" << segments.size() << std::endl;

	Arrangement_2 arr;

	// std::cout << "Segments array allocation." << std::endl;
	Segment_2 seg[segments.size()];
	// std::cout << "Ok" << std::endl;


	// Insert all segments in the arrangement
	int idx=0;
	for(std::vector<Segment>::iterator it = segments.begin(); it != segments.end(); it++)    
	{
		if (distanceBetween(it->a.x, it->a.y,it->b.x,it->b.y) > 0.000000001)
		{

			seg[idx] = Segment_2(Point_2(it->a.x, it->a.y),Point_2(it->b.x,it->b.y));
			// std::cout << "Inserting segment into the arrangement." << std::endl;
			// std::cout << "Segment:" << seg[idx] << std::endl;
			// arr.insert_in_face_interior(seg[idx], arr.unbounded_face());
			// CGAL::insert(arr, &seg[0], &seg[1]);

			idx++;

			// std::cout << "OK" << std::endl;
		}


	}

	// for (int i = 0; i < idx; i++)
	// {
	// 	std::cout << "Segment :" << seg[i] << std::endl;
	// }
	
	// std::cout << "idx:" << idx << std::endl;
	// std::cout << "Inserting segments into the arrangement." << std::endl;
	CGAL::insert(arr, &seg[0], &seg[idx]);
	// std::cout << "Ok" << std::endl;


	// Iterate over the faces of the arrangement and compute the regions
	std::vector<Region> regions;

	// std::cout << arr.number_of_faces() << " faces:" << std::endl;
	for (Arrangement_2::Face_const_iterator fit = arr.faces_begin(); fit != arr.faces_end(); ++fit)
	{
		if (!fit->is_unbounded())
		{
			regions.push_back(createRegion(fit));
		}
	}
	return regions;
}

Region createRegion(Arrangement_2::Face_const_handle f)
{
	std::vector<Hole> region_holes;
	std::vector<Point> region_contour;
	Arrangement_2::Ccb_halfedge_const_circulator curr;

	curr = f->outer_ccb();
	
	// Get the outer boudary
	do 
	{
		Arrangement_2::Halfedge_const_handle he = curr;
		Point p;
    	p.x = CGAL::to_double(he->target()->point().x());
    	p.y = CGAL::to_double(he->target()->point().y());
    	region_contour.push_back(p);
	}
	while (++curr != f->outer_ccb());

	// Get the holes
	for (Arrangement_2::Hole_const_iterator hi = f->holes_begin(); hi != f->holes_end(); ++hi)
	{
		std::vector<Point> hole_contour;
		curr = *hi;
		do 
		{
			Arrangement_2::Halfedge_const_handle he = curr;
			Point p;
	    	p.x = CGAL::to_double(he->target()->point().x());
	    	p.y = CGAL::to_double(he->target()->point().y());
	    	hole_contour.push_back(p);
		}
		while (++curr != *hi);
		region_holes.push_back(Hole(hole_contour));
	}
	return Region(region_contour, region_holes);
}