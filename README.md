pycompgeom
==========
*pycompgeom* is a pure Python library that eventually will provide 
Robust Geometric Computations and Visualizations _for ordinary mortals_.
*pycompgeom* shares the same spirit and rationale behind the similar 
[py.CGAL.visual](http://cgi.di.uoa.gr/~compgeom/pycgalvisual/index.shtml) project and  tries to be self-contained by dropping the
dependency of the CGAL-Python bindings.

The primary goal of *pycompgeom* is to motivate students to implement 
the algorithms taught in class and experiment with various inputs in 
order to gain better insight and experience.

This is an example of the Andrew algorithm coded in Python: 

```python
from pycompgeom.predicates import *

def andrew(points):
	upper = []
	lower = []
	for point in sorted(points):
		while len(upper) > 1 and ccwon(upper[-2], upper[-1], point):
			upper.pop()
		while len(lower) > 1 and cwon(lower[-2], lower[-1], point):
			lower.pop()
		upper.append(point)
		lower.append(point)
	hull = lower[:-1]+ [x for x in reversed(upper[1:])]
	return hull
	
points = getVPoints()
hull = VPolygon2(Polygon2(andrew(points)))
pause()
```
