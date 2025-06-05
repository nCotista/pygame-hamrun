import random
from setting import *
import pygame
from pygame.locals import *
import pygwidgets
from pygame import mixer


class CustomButton:
    def __init__(self, screen, x, y, image_path):
        self.screen = screen
        self.button = pygwidgets.CustomButton(screen, (x, y),
                                               image_path,
                                               down=image_path,
                                               over=image_path,
                                               disabled=image_path)
        self.x = x
        self.y = y

    def update_position(self):
        screen_width = pygame.display.Info().current_w 
        screen_height = pygame.display.Info().current_h 
        button_x = screen_width // 2 - self.x
        button_y = screen_height // 2 - self.y #it too complicate to find the best equation na i will try another way then come back na 
        # button_x = screen_width * self.x 
        # button_y = screen_height * self.y 
        self.button.setLoc((button_x, button_y))

    def draw(self):
        self.button.draw()
    
    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                if self.button.getRect().collidepoint(mouse_pos):
                    return True  # Button was clicked
        return False  # Button was not clicked

#load music
mixer.music.load('pygame/sound/bgm.mp3')
turn_sound = pygame.mixer.Sound('pygame/sound/change.ogg')

class Slider:
    def __init__(self, screen: pygame.Surface, initial_val: float, min: int, max: int):
        self.screen = screen
        self.min = min
        self.max = max
        self.initial_val = initial_val

        self.hovered = False
        self.grabbed = False

        # Dynamic sizing based on screen width
        self.update_size_and_position()

    def update_size_and_position(self):
        # Dynamic slider width (80% of screen width)
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Scale slider width and height based on screen size
        self.size = (int(screen_width * 0.8), int(screen_height * 0.04))
        
        # Center the slider
        self.pos = (screen_width // 2, screen_height // 2)
        
        # Calculate slider boundaries
        self.slider_left_pos = self.pos[0] - (self.size[0] // 2) #(x,y)
        self.slider_right_pos = self.pos[0] + (self.size[0] // 2)
        self.slider_top_pos = self.pos[1] - (self.size[1] // 2) #pygameg top left

        # Create container and button rects with dynamic sizing
        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        
        # Calculate button width proportional to slider width
        button_width = max(10, int(screen_height * 0.03))
        
        # Position the button based on initial value  bartotal        0.5        - for pos left suit of box
        button_x = (self.slider_left_pos + (self.size[0] * self.initial_val) - (button_width // 2))
        
        self.button_rect = pygame.Rect(button_x, self.slider_top_pos, button_width,self.size[1])

        # Update display text position
        self.display_text = pygwidgets.DisplayText(
            self.screen, 
            (self.pos[0], self.slider_top_pos - int(screen_height * 0.05)), 
            textColor=(255, 255, 255),
            fontSize=int(screen_height * 0.03)  # Dynamic font size
        )
        
        # Update the display value
        self.update_display_value()

    def move_slider(self, mouse_pos):
        pos = mouse_pos[0]
        if pos < self.slider_left_pos:
            pos = self.slider_left_pos
        if pos > self.slider_right_pos:
            pos = self.slider_right_pos
        self.button_rect.centerx = pos
        self.update_display_value()
    
    #add from comment
    def handle_mouse_wheel(self, event):
    # Check if the mouse is over the slider area
        if self.container_rect.collidepoint(pygame.mouse.get_pos()):
            # Adjust value based on scroll direction
            increment = 1 if event.y > 0 else -1  # Scroll up is positive, down is negative
            current_val = self.get_value()
            
            # Calculate the new value with boundaries
            new_val = max(self.min, min(self.max, current_val + increment))
            
            # Update button position based on the new value
            val_range = self.slider_right_pos - self.slider_left_pos
            normalized_pos = (new_val - self.min) / (self.max - self.min)
            self.button_rect.centerx = int(self.slider_left_pos + normalized_pos * val_range)
            
            # Update the displayed value
            self.update_display_value()


    def hover(self, mouse_pos):
        if self.container_rect.collidepoint(mouse_pos):
            self.hovered = True
        else:
            self.hovered = False

    def render(self):
        # Dynamic colors and rendering based on screen size
        container_color = (100, 100, 100)  # Dark gray
        button_color = (255, 255, 255) if self.hovered else (200, 0, 0)
        
        pygame.draw.rect(self.screen, container_color, self.container_rect)
        pygame.draw.rect(self.screen, button_color, self.button_rect)
        self.display_text.draw()

    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos
        button_val = self.button_rect.centerx - self.slider_left_pos
        return (button_val / val_range) * (self.max - self.min) + self.min #(100 - 0 ) + 0  ++  in case of min not 0

    def update_display_value(self):
        # Update the display text with the current value
        value = int(self.get_value())
        self.display_text.setText(f"Volume: {value}")
        
        # Set the mixer volume based on the slider value (normalize to 0.0 - 1.0)
        pygame.mixer.music.set_volume(value / 100.0)
        global turn_sound
        turn_sound.set_volume(value/100.0)


class Obstacle:
    def __init__(self, lane):
        self.lane = lane

        # Basic + Co-ordinate Setting
        self.size = 50 #random.randint(30,50)
        self.y = -self.size
        self.x = get_lane_x_position(self.lane, self.y)
        # Load obstacle image
        
        self.image = pygame.image.load('pygame\img\ham.PNG').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        # Speed Addition/Subtraction + text Setting
        self.speedChanger = random.randint(obstacle_low_value, obstacle_high_value)
        self.font = pygame.font.Font(None, 72)
        self.text = self.font.render(str(self.speedChanger), True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.x + 25, self.y -50))

    def obstacle_move(self):
            self.y += obstacle_speed
            scale = 1 + (self.y / SCREEN_HEIGHT)
            scaled_width = int(obstacle_width * scale)  # obstacle_width in setting.py
            scaled_height = int(obstacle_height * scale)
            self.x = get_lane_x_position(self.lane, self.y)
            # Update image size and position
            scaled_image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            screen.blit(scaled_image, (self.x, self.y))

            # Draw Text on Rect
            self.text_rect = self.text.get_rect(center=(self.x +25, self.y -50 ))
            screen.blit(self.text, self.text_rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class MuDi_Obstacle(Obstacle):
    def __init__(self, lane):
        super().__init__(lane)

        self.operator = random.choice(['X', '%'])
        self.muDiNum = random.randint(obstacle_low_multiplier, obstacle_high_multiplier)
        self.speedChanger = self.muDiNum if self.operator == 'X' else 1/self.muDiNum
        self.text = self.font.render(str(f'{self.operator} {self.muDiNum}'), True, (255, 255, 255))

    def get_total(self, player_speed):
        return int(player_speed * self.speedChanger)

class Barrier(Obstacle):
    def __init__(self, lane, low, high):
        super().__init__(lane)

        # Load barrier image
        self.image = pygame.image.load('pygame/img/wall.jpg').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        
        # Barrier-specific speed limit
        self.color = (0, 0, 255)
        self.speedLimit = random.randint(low, high)
        self.text = self.font.render(str(self.speedLimit), True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.x + 25, self.y - 50))


# Function Section

def create_obstacle():
    for i in range(0, 2):
        if random.randint(0, 100) < MuDi_spawn_rate: # 20% to spawn a Multiplication Obstacle(MuDi_Obstacle)
            obstacles.append(MuDi_Obstacle(i))
        else:
            obstacles.append(Obstacle(i))

def create_barrier(low, high):
    obstacles.append(Barrier(0, low, high))
    obstacles.append(Barrier(1, low, high))
# Function to calculate lane X position based on Y (depth effect)
def get_lane_x_position(lane, y):
    SCREEN_WIDTH = pygame.display.Info().current_w 
    SCREEN_HEIGHT =  pygame.display.Info().current_h 
    road_bottom_width = SCREEN_WIDTH 
    road_top_width = SCREEN_WIDTH * 0.1

    # Linear interpolation between top and bottom lane positions based on Y
    road_width_at_y = road_top_width + (road_bottom_width - road_top_width) * (y / SCREEN_HEIGHT) #come from chat gpt

    if lane == 0:  # Left lane
        return SCREEN_WIDTH // 2 - road_width_at_y / 4
    elif lane == 1:  # Right lane
        return SCREEN_WIDTH // 2 + road_width_at_y / 5


class RoadRenderer:
    def __init__(self, screen, road_image):
        self.screen = screen
        self.road_image = road_image
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
    def render(self, car_x=0):
        # Update screen dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        # Render road slices with perspective effect
        for i in range(self.screen_height):
            # Calculate scale based on distance from viewer
            scale = (self.screen_height - i) / self.screen_height
            x = car_x + i/scale
            # Calculate position of the road slice
            
            road_slice = self.road_image.subsurface((0, x%self.road_image.get_height(), self.road_image.get_width(), 1))
            
            # Scale the slice to create perspective effect
            scaled_slice = pygame.transform.scale(
                road_slice, 
                (int(self.screen_width * scale), 1)
            )
            
            # Position the slice to create vanishing point
            self.screen.blit(
                scaled_slice, 
                (int((self.screen_width / 2) * (1 - scale)), self.screen_height - i)
            )


#this object need to load 
#picture
background = pygame.image.load('pygame/img/Pixellance.png')
uibg = pygame.image.load('pygame/img/uibg.jpg')
died1 =  pygame.image.load('pygame/img/died.webp')

#button from creater
start_button = CustomButton(screen, 200, -150, 'pygame/img/startb.png') #note the same value !!!!!!!!11
meun_button = CustomButton(screen, 0, -150, 'pygame/img/menu.png') 
# Gameoverte = CustomButton(screen, 0, -150, 'pygame/img/menu.png') 
exit_button = CustomButton(screen, 0, -150, 'pygame/img/exit.png')

#pygwidgets object
# musicSound = pygwidgets.BackgroundSound('pygame/sound/bgm.mp3')
# myDisplayText = pygwidgets.DisplayText(screen, (100, 200),textColor=(255, 255, 255))
# GameoverText = pygwidgets.DisplayText(screen, (100, 200),textColor=(255, 255, 255))

slider = Slider(screen, initial_val=0.5, min=0, max=100)

roadx = pygame.image.load('pygame/img/road.png').convert()
road = pygame.transform.scale(roadx, (roadx.get_width(), roadx.get_height()))
clock = pygame.time.Clock()
road_renderer = RoadRenderer(screen, road)

