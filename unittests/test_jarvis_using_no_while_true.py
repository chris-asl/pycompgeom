import sys
sys.path.append('..')

from pycompgeom import *

def jarvis(points):
    r = r0 = min(points)
    hull = [r0]
    u = None
    while u <> r0:
        u = random.choice(points)
        for t in points:
            if cw(r, u, t) or collinear(r, u, t) and between(r, t, u):
                u = t

        r = u
        points.remove(r)
        hull.append(r)
    return hull


points = random_points(500, visual=True)
p=VPolygon2(Polygon2(jarvis(points[:])), color=GREEN)
pause()
