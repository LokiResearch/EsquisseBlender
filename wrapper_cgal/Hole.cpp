// Author: Axel Antoine
// https://axantoine.com
// 01/26/2021

// Loki, Inria project-team with Université de Lille
// within the Joint Research Unit UMR 9189 CNRS-Centrale
// Lille-Université de Lille, CRIStAL.
// https://loki.lille.inria.fr

// LICENCE: Licence.md

#include "Hole.h"

Hole::Hole() {}

Hole::Hole(std::vector<Point> _contour) : contour(_contour) {}

Hole::~Hole() {}