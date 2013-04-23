import sys
sys.path.append('..')

from pycompgeom import *

segments = random_segments(1000, visual=True)
a = VPoint2(color=BLUE)
pause()
