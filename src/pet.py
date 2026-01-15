import pygame 
import random 
import win32gui

class Pet(pygame.sprite.Sprite): 
    def __init__(self,screen_width, screen_height, group):
        super().__init__()
        self.group = group 
        self.screen_width = screen_width
        self.ground_y = screen_height

        self.platform_hwnd = None
        self.on_window = False 
        scale = (125,88)

        # animation lists
        self.walk_right = [
        pygame.transform.scale(pygame.image.load("graphics/sheep_walk_1.png").convert_alpha(), scale),
        pygame.transform.scale(pygame.image.load("graphics/sheep_walk_2.png").convert_alpha(), scale)
        ]

        self.walk_left = [
            pygame.transform.flip(img, True, False) for img in self.walk_right
        ]
        
        # frame 
        self.frame = 0
        self.frame_timer = 0
        self.frame_delay = 8

        # direction
        self.direction = random.choice([-1,1])
        self.vx = 4 * self.direction
        if self.direction == 1:
            self.image = self.walk_right[self.frame]
        else: 
            self.image = self.walk_left[self.frame]

        pos = (random.randint(50,screen_width - 50), 0)
        self.rect = self.image.get_rect(midbottom=pos)

        # state
        self.state = "fall"
        self.idle_until = 0

        # gravity 
        self.vy = 0
        self.gravity = 0.3
        self.drag_offset = pygame.Vector2()
   
    def update(self, window_platforms):
        if self.state ==  "drag": # drag has highest priority
            self.drag()
        elif not self.has_support(window_platforms): #otherwise check if we should fall
            self.state = "fall"
            self.on_window = False
            self.platform_hwnd = None
        
        if self.state == "fall":
            self.fall(window_platforms)
        elif self.state == "walk":
            self.walk()
        elif self.state == "idle":
            self.idle()
     

    def fall(self, window_platforms):
        # physics
        self.vy += self.gravity
        self.rect.y += self.vy

        self.on_window = False
        self.platform_hwnd = None

        # check window platforms
        for hwnd, platform in window_platforms:
            if (
                self.rect.bottom >= platform.top and
                self.rect.bottom - self.vy <= platform.top and
                self.rect.right >= platform.left and
                self.rect.left <= platform.right
            ):
                self.rect.bottom = platform.top
                self.vy = 0
                self.state = "walk"
                self.on_window = True
                self.platform_hwnd = hwnd
                return

        # snap to ground floor if it exceeds the limit
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vy = 0
            self.state = "walk"

    def walk(self):
        # movement 
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, self.group, False)
        for other in hits:
            if other is self:
                continue 
            if other.state == "drag":
                continue 
            if self.rect.bottom <= other.rect.top:
                continue 
            else :
                if self.vx > 0: # moving right
                    self.rect.right = other.rect.left
                else:
                    self.rect.left = other.rect.right 
            self.state = "idle"
            self.idle_until = pygame.time.get_ticks() + random.randint(500, 5000)
            break 

        if self.rect.left <= 0:
            self.rect.left = 0
            self.vx = abs(self.vx)
            self.direction = 1
        elif self.rect.right >= self.screen_width:
            self.rect.right = self.screen_width
            self.vx = -abs(self.vx)
            self.direction = -1

        # animation
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0 
            self.frame = (self.frame + 1) % 2 

        if self.direction == 1:
            self.image = self.walk_right[self.frame]
        else: 
            self.image = self.walk_left[self.frame]
        
        if self.on_window:
            l, t, r, b = win32gui.GetWindowRect(self.platform_hwnd)

            if self.rect.right < l or self.rect.left > r:
                self.on_window = False
                self.platform_hwnd = None
                self.state = "fall"
        
        # RANDOMLY GO IDLE
        if random.random() < 0.003:  # tweak this value
            self.state = "idle"
            self.idle_until = pygame.time.get_ticks() + random.randint(3000, 10000)
    
    def idle(self):
        # stand still for x amount of time
        if pygame.time.get_ticks() >= self.idle_until:
            # choose new direction
            self.direction = random.choice([-1,1])
            self.vx = 3 * self.direction
            self.state = "walk"

    def drag(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.x = mouse_x + self.drag_offset.x
        self.rect.y = mouse_y + self.drag_offset.y

    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = "drag"
                self.vy = 0
                self.drag_offset.x = self.rect.x - event.pos[0]
                self.drag_offset.y = self.rect.y - event.pos[1]
                pygame.event.set_grab(True)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == "drag":
                self.state = "fall"
                pygame.event.set_grab(False)


    def has_support(self,window_platforms):
        foot_left = self.rect.left
        foot_right  = self.rect.right
        foot_y = self.rect.bottom + 1

        # check ground
        if foot_y >= self.ground_y:
            return True

        # check sheep
        for other in self.group:
            if other is self:
                continue
            if (
                other.rect.collidepoint(foot_left, foot_y) or
                other.rect.collidepoint(foot_right, foot_y)
                ):
                return True

        # check window platforms
        for _, platform in window_platforms:
            if (
                platform.collidepoint(foot_left, foot_y) or
                platform.collidepoint(foot_right, foot_y)
            ):
                return True

        return False