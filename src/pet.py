import pygame 
import random 

class Pet(pygame.sprite.Sprite): 
    def __init__(self,screen_width, screen_height, group):
        super().__init__()
        self.group = group 
        self.screen_width = screen_width
        self.ground_y = screen_height

        h = (pygame.image.load("graphics/sheep/walk_1.png").convert_alpha()).get_height()
        w = (pygame.image.load("graphics/sheep/walk_1.png").convert_alpha()).get_width()
        s = 0.8
        
        scale = (w * s, h * s)

        # animations
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
        self.lay_right = [
            pygame.transform.scale(pygame.image.load("graphics/sheep/lay_1.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/lay_2.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/lay_3.png").convert_alpha(), scale)
        ]
        self.lay_left = [
            pygame.transform.flip(img, True, False) for img in self.lay_right
        ]
        self.sleep_right = [
            pygame.transform.scale(pygame.image.load("graphics/sheep/sleep_1.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/sleep_2.png").convert_alpha(), scale)
        ]
        self.sleep_left = [
            pygame.transform.flip(img, True, False) for img in self.sleep_right
        ]
        self.turn_left = [
            self.idle_right[0],
            pygame.transform.scale(pygame.image.load("graphics/sheep/turn_1.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/turn_2.png").convert_alpha(), scale),
            pygame.transform.scale(pygame.image.load("graphics/sheep/turn_3.png").convert_alpha(), scale),
            self.idle_left[0]
        ]
        self.turn_right = [
            pygame.transform.flip(img, True, False) for img in self.turn_left
        ]

        # frame 
        self.frame = 0
        self.frame_timer = 0
        self.frame_delay = 20

        # direction
        self.direction = random.choice([-1,1])
        self.crash_dir = 0

        # walk
        self.walk_speed = 1 * self.direction

        # run
        self.run_chance = 0.15
        self.acc = 0.1 * self.direction
        self.max_speed = 10
        self.knockback_x = 3 * self.direction
        self.knockback_y = -6

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
        self.sleep_until = 0

        # gravity 
        self.vy = 0
        self.gravity = 0.2
        self.drag_offset = pygame.Vector2()

        self.next_state = ""

   
    def update(self, platforms):
        if self.state ==  "drag": # drag has highest priority
            self.drag()
            return
        elif self.state == "crash":
            self.crash(platforms)
            return

        elif not (self.has_support(platforms))[0]:
            self.state = "fall"
        
        if self.state == "fall":
            self.fall(platforms)
        elif self.state == "run":
            self.run()
        elif self.state == "walk":
            self.walk()
        elif self.state == "idle":
            self.idle()
        elif self.state == "lay":
            self.lay()
        elif self.state == "sleep":
            self.sleep()
        elif self.state == "turn":
            self.turn()

    def idle(self):
        self.animate("idle", 20)
        self.reset_move_attributes()
        # stand still for x amount of time
        if pygame.time.get_ticks() >= self.idle_until:
            if random.random() < self.run_chance:  # chance to run
                next_state = "run"
            elif random.random() < 0.1:
                next_state = "lay"
            else: 
                next_state = "walk"

        # choose new direction
            new_dir = random.choice([-1,1])
            self.request_turn(new_dir, next_state)
        
    def fall(self, platforms):
        # physics
        self.vy += self.gravity
        self.rect.y += self.vy

        # animation
        self.animate("drag", 5)

        # check if we landed on a platform or the ground
        support_check = self.has_support(platforms)
        if support_check[0]:
                self.rect.bottom = support_check[1]
                self.set_idle(300,5000)
                return
        
    def drag(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.x = mouse_x + self.drag_offset.x
        self.rect.y = mouse_y + self.drag_offset.y

        # can't be dragged outside of desktop frame
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
        # make sure the speed doesn't exceed the limit
        if abs(self.vx) >= self.max_speed: 
            self.vx  = self.max_speed * self.direction
        self.move()

        # collisions
        if self.border_collision(self.start_crash): return 
 
        hits = pygame.sprite.spritecollide(self, self.group, False)
        for other in hits:
            if other is self:
                continue 
            if self.rect.bottom <= other.rect.top:
                continue 
            else :
                if self.vx > 0: # moving right
                    self.rect.right = other.rect.left
                    self.start_crash(-1)
                else:
                    self.rect.left = other.rect.right 
                    self.start_crash(1)
                return 

        self.animate("walk", 5)

    def walk(self):
        # movement 
        self.vx = self.walk_speed
        self.move()
        
        #collisions
        if self.border_collision(
            lambda dir: self.request_turn(dir, "walk")
        ):
            return 
        
        hits = pygame.sprite.spritecollide(self, self.group, False)
        for other in hits:
            if other is self:
                continue 
            if other.state == "drag" or other.state == "crash":
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

        

        self.animate("walk", 20)

        # RANDOMLY GO IDLE
        if random.random() < 0.003:  # tweak this value
            self.state = "idle"
            self.idle_until = pygame.time.get_ticks() + random.randint(3000, 10000)

    def start_crash(self, hit_dir):
        self.state = "crash"
        self.crash_dir = hit_dir
        self.vx = self.knockback_x * hit_dir
        self.vy = self.knockback_y

    def crash(self, platforms):
        self.vy += self.gravity
        self.move()

        if self.rect.top < 0:
            self.rect.top = -1
            self.reset_move_attributes()
            self.state = "fall"
            return 
        

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
                self.set_idle(300,3000)
                self.on_platform = platform
                return

        # land on ground
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.set_idle(500, 3000)


        # collisions
        # border collision
        if self.rect.left <= 0: 
            self.rect.left = 0
            self.vx = abs(self.vx)
            return 
        elif self.rect.right >= self.screen_width:
            self.rect.right = self.screen_width
            self.vx  = -abs(self.vx)
            return 
   

        hits = pygame.sprite.spritecollide(self, self.group, False)
        for other in hits:
            if other is self:
                continue 
            if self.rect.bottom <= other.rect.top:
                continue 
            else :
                if self.vx > 0: # moving right
                    self.rect.right = other.rect.left
                    self.vx = -abs(self.vx)
                    return
                else:
                    self.rect.left = other.rect.right 
                    self.vx  = abs(self.vx)
                    return

    def lay(self):
        self.animate("lay", 10)

        if self.frame == len(self.lay_right) - 1:
            self.frame = 0
            self.timer = 0
            self.sleep_until = pygame.time.get_ticks() + random.randint(10000, 20000) # sleep for at least 10 seconds
            self.state = "sleep"

    def sleep(self):
        # sleep until timer
        if pygame.time.get_ticks() >= self.sleep_until:
            self.set_idle(300, 10000)
        self.animate("sleep", 20)
        
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

        

        if self.direction == 1:
            list = getattr(self, f"{state}_right")
        else: 
            list = getattr(self, f"{state}_left")
        # animation
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0 
            self.frame = (self.frame + 1) % len(list)

        if self.frame >= len(list):
            self.frame = 0
        

        self.image = list[self.frame]

    def has_support(self, platforms):
        foot_y = self.rect.bottom + 1

        # check ground
        if foot_y >= self.ground_y:
            return (True, self.ground_y)

        # check platforms
        for platform in platforms:
            rect = platform.rect 
            if (
                self.rect.bottom >= rect.top and
                self.rect.bottom - self.vy <= rect.top and
                self.rect.right >= rect.left and
                self.rect.left <= rect.right
            ):
                return (True, rect.top) 

        return (False, None)
    
    def move(self):
        self.rect.x
        self.rect.x += self.vx
        self.rect.y += self.vy

    def reset_move_attributes(self):
        self.vx = 0
        self.vy = 0

    def border_collision(self, on_hit):
        if self.rect.left <= 0: # left border hit
            self.rect.left = 0
            on_hit(1)
            return True
        
        elif self.rect.right >= self.screen_width: # right border hit
            self.rect.right = self.screen_width
            on_hit(-1)
            return True
        return False 

    def request_turn(self, new_dir, next_state):
        if new_dir == self.direction:
            self.state = next_state
            return 
        
        self.direction = new_dir
        self.next_state = next_state
        self.frame = 0
        self.frame_timer = 0
        self.state = "turn"

    def turn(self):
        self.reset_move_attributes()
        self.animate("turn", 15)

        if self.frame == len(self.turn_right) - 1:
            self.direction = self.direction
            self.change_direction()
            self.frame = 0
            self.frame_timer = 0
            self.state = self.next_state  

    def change_direction(self):
            self.walk_speed = abs(self.walk_speed) * self.direction
            self.knockback_x = abs(self.knockback_x) * self.direction
            self.acc = abs(self.acc) * self.direction