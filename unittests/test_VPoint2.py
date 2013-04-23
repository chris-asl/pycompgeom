import sys
sys.path.append('..')

from pycompgeom import *

points = random_points(1000, visual=True)
a = VPoint2(color=BLUE)
pause()
del points, a
