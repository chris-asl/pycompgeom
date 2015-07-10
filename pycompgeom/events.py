LEFTBUTTON = 1
MIDDLEBUTTON = 2
RIGHTBUTTON = 3
K_ESCAPE = 4

import pygame
import sys

def should_i_quit(event):
	if event.type == pygame.QUIT or \
		event.type == pygame.KEYDOWN \
		and event.key == pygame.K_ESCAPE:
			pygame.quit()
			sys.exit()
	return False
		
def get_mouse_click(button=LEFTBUTTON):
	while True:
		event = pygame.event.poll()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == button:
				return event.pos
		elif not should_i_quit(event):
			event = None

def waitForKeyPress():
	while True:
		event = pygame.event.poll()
		if not should_i_quit(event):
			if event.type == pygame.KEYDOWN:
				return

def pause():
	pygame.display.set_caption('hit any key to continue ...')
	waitForKeyPress()
	pygame.display.set_caption('pyCompGeom window')
