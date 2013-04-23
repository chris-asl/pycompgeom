import sys
sys.path.append('..')

from pycompgeom import *

segments = random_segments(9, visual=True)
status = BST()
for s in segments:
	status.insert(s.start, s)

def pleaf(key,data):
	print segments.index(data)

status.processAll(pleaf)

pause()
del status, segments
