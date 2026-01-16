import pygame 
import random 

class Pet(pygame.sprite.Sprite): 
    def __init__(self,screen_width, screen_height, group):
        super().__init__()
        self.group = group 
        self.screen_width = screen_width
        self.ground_y = screen_height

        self.on_platform = False 
        scale = (125,88)

        # animation lists
        self.walk_right = [
            pygame.transform.scale(pygame.image.load("graphics/sheep/walk_1.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/walk_2.png").convert_alpha(), scale)
        ]

        self.walk_left = [
            pygame.transform.flip(img, True, False) for img in self.walk_right
        ]

        self.drag_right = [
            pygame.transform.scale(pygame.image.load("graphics/sheep/drag_1.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/drag_2.png").convert_alpha(), scale)
        ]
        self.drag_left = [
            pygame.transform.flip(img, True, False) for img in self.drag_right
        ]

        self.idle_right = [
            pygame.transform.scale(pygame.image.load("graphics/sheep/idle_1.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/idle_2.png").convert_alpha(), scale)
        ]        

        self.idle_left = [
            pygame.transform.flip(img, True, False) for img in self.idle_right
        ]

        # frame 
        self.frame = 0
        self.frame_timer = 0
        self.frame_delay = 20

        # direction
        self.direction = random.choice([-1,1])

        # walk
        self.walk_speed = 1

        # run
        self.acc = 0.1
        self.max_speed = 10
        self.knockback_x = 4

        # current speed
        self.vx = 0
    
        # set correct animation image for direction 
        if self.direction == 1:
            self.image = self.walk_right[self.frame]
        else: 
            self.image = self.walk_left[self.frame]

        # spawn location
        pos = (random.randint(50,screen_width - 50), 0)
        self.rect = self.image.get_rect(midbottom=pos)

        # state
        self.state = "fall"
        self.idle_until = 0

        # gravity 
        self.vy = 0
        self.gravity = 0.2
        self.drag_offset = pygame.Vector2()

   
    def update(self, platforms):
        if self.state ==  "drag": # drag has highest priority
            self.drag()
        elif self.state == "crash":
            self.crash()

        elif not self.has_support(platforms): # otherwise check if we should fall
            self.state = "fall"
            self.on_platform = False
        
        if self.state == "fall":
            self.fall(platforms)
        elif self.state == "run":
            self.run()
        elif self.state == "walk":
            self.walk()
        elif self.state == "idle":
            self.idle()

    def fall(self, platforms):
        # physics
        self.vy += self.gravity
        self.rect.y += self.vy

        self.on_platform= False

        # check platforms
        for platform in platforms:
            rect = platform.rect
            if (
                self.rect.bottom >= rect.top and
                self.rect.bottom - self.vy <= rect.top and
                self.rect.right >= rect.left and
                self.rect.left <= rect.right
            ):
                self.rect.bottom = rect.top
                self.vy = 0
                self.set_idle(300,3000)
                self.on_platform = platform
                return

        # snap to ground floor if it exceeds the limit
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vy = 0
            self.set_idle(50,5000)
        
        self.animate("drag", 5)

    def walk(self):
        # movement 
        self.vx = self.walk_speed
        self.move()
        
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
            self.set_idle(500,5000)
            break 

        if self.rect.left <= 0: # hit the left border
            self.rect.left = 0
            self.direction = 1
            self.change_direction()
        elif self.rect.right >= self.screen_width:
            self.rect.right = self.screen_width
            self.direction = -1
            self.change_direction()

        self.animate("walk", 20)

        # RANDOMLY GO IDLE
        if random.random() < 0.003:  # tweak this value
            self.state = "idle"
            self.idle_until = pygame.time.get_ticks() + random.randint(3000, 10000)
    
    def idle(self):
        self.reset_move_attributes()
        # stand still for x amount of time
        if pygame.time.get_ticks() >= self.idle_until:
            # choose new direction
            self.direction = random.choice([-1,1])
            self.change_direction()

            state = random.choice(["walk", "run"])
            self.state = state
        
        self.animate("idle", 20)

    def drag(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.x = mouse_x + self.drag_offset.x
        self.rect.y = mouse_y + self.drag_offset.y

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > self.ground_y:
            self.rect.bottom = self.ground_y

        self.animate("drag", 5)

    def run(self):
        # speed movement
        self.vx += self.acc
        if abs(self.vx) >= self.max_speed:
            self.vx  = self.max_speed * self.direction
        self.move()

        # collisions
        if (self.rect.left <= 0) or (self.rect.right >= self.screen_width): # hit the border
            self.vy = -10
            self.vx = self.knockback_x * -1
            self.state = "crash"
            return 

        self.animate("walk", 5)

        # randomly stop
        if random.random() < 0.003: 
            self.set_idle(500,5000)

    def crash(self):
        self.vy += self.gravity
        self.move()

        # land on ground
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.set_idle(500, 3000)

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

    def set_idle(self, min, max):
        self.state = "idle"
        self.idle_until = pygame.time.get_ticks() + random.randint(min, max)

    def animate(self, state, delay):
        self.frame_delay = delay 
        # animation
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0 
            self.frame = (self.frame + 1) % 2 

        if self.direction == 1:
            list = getattr(self, f"{state}_right")
        else: 
            list = getattr(self, f"{state}_left")
    
        self.image = list[self.frame]

    def has_support(self, platforms):
        foot_left = self.rect.left
        foot_right  = self.rect.right
        foot_y = self.rect.bottom + 1

        # check ground
        if foot_y >= self.ground_y:
            return True

        # check platforms
        for platform in platforms:
            rect = platform.rect 
            if (
                rect.collidepoint(foot_left, foot_y) or
                rect.collidepoint(foot_right, foot_y)
            ):
                return True

        return False
    
    def move(self):
        self.rect.x
        self.rect.x += self.vx
        self.rect.y += self.vy

    def reset_move_attributes(self):
        self.vx = 0
        self.vy = 0

    def change_direction(self):
        self.walk_speed = abs(self.walk_speed) * self.direction
        self.knockback_x = abs(self.knockback_x) * self.direction
        self.acc = abs(self.acc) * self.direction