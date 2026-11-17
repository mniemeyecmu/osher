import __main__
import os
import sys

__main__.CMU_GRAPHICS_NO_UPDATE = True

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

try:
    import pygame
    from PIL import Image
    _base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(
        os.path.abspath(__file__))
    _icon = Image.open(os.path.join(_base, 'Osher.ico')).convert('RGBA')
    pygame.display.init()
    pygame.display.set_icon(
        pygame.image.fromstring(_icon.tobytes(), _icon.size, 'RGBA'))
except Exception:
    pass
