import pygame  
import ctypes
import win32api
import win32gui
import win32con
from sheep import Sheep 

# init
pygame.init()

# create fullscreen window
pygame.display.set_caption("Desktop Sheep")
WINDOW = pygame.display.set_mode((0,0), pygame.NOFRAME)

# make window layered
hwnd = pygame.display.get_wm_info()["window"]
ctypes.windll.user32.SetWindowLongW(hwnd, -20, ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000)

# make the entire window transparent 
transparency_color = (0,0,0)
color_key = (transparency_color[2] << 16) | (transparency_color[1] << 8) | transparency_color[0]
ctypes.windll.user32.SetLayeredWindowAttributes(hwnd,color_key, 0, 0x00000001)

# get workarea
monitor = win32api.MonitorFromPoint((0,0))
info = win32api.GetMonitorInfo(monitor)
work_rect = info["Work"]
TASKBAR_TOP_Y = work_rect[3]

# set framerate
clock = pygame.time.Clock()
FPS = 60
sheep_group = pygame.sprite.Group()

# button setup
BUTTON_RECT  = pygame.Rect(600,10,140,40)
BUTTON_COLOR = (180,180,180)
BUTTON_HOVER = (150,150,150)

font = pygame.font.SysFont(None,24)
button_text = font.render("Spawn Sheep", True, (255,255,255))

def get_window_platforms():
    platforms = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return 

        # Ignore your own window
        if hwnd == pygame.display.get_wm_info()["window"]:
            return
        
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        # Ignore tiny / weird windows
        if r - l < 100 or b - t < 50:
            return
        
        # Create a thin platform on top border
        platform_rect = pygame.Rect(
            l,
            t - 1,      # a few pixels above window
            r - l,
            2           # platform thickness
        )
        platforms.append((hwnd, platform_rect))

    win32gui.EnumWindows(enum_handler, None)
    return platforms

running = True
transparent_surface = pygame.Surface(WINDOW.get_size())
transparent_surface.fill((0, 0, 0))
while running:
    clock.tick(FPS)
    WINDOW.fill((0, 0, 0))  # MUST match transparency color

    # keep window on top
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for sheep in sheep_group:
            sheep.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if BUTTON_RECT.collidepoint(event.pos):
                sheep_group.add(Sheep(WINDOW.get_width(), TASKBAR_TOP_Y, sheep_group))
          

    window_platforms = get_window_platforms()
    sheep_group.update(window_platforms)

    sheep_group.draw(WINDOW)
    
    # draw button 
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER if BUTTON_RECT.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(WINDOW, color, BUTTON_RECT)
    WINDOW.blit(button_text, button_text.get_rect(center=BUTTON_RECT.center))

    pygame.display.flip()
    pygame.display.update()
    clock.tick(60)