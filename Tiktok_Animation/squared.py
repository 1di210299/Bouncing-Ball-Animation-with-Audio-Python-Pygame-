import pygame
import math
import random
import cv2
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

def generate_beep(frequency=440, duration=0.1, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * frequency * t) * volume
    wave = np.repeat(wave.reshape(len(wave), 1), 2, axis=1)
    sound = pygame.sndarray.make_sound((wave * 32767).astype(np.int16))
    return sound

collision_sound = generate_beep(frequency=350, duration=0.1, volume=0.1)

width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cuadrados y líneas en movimiento")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 60.0, (width, height))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.Font(None, 36)

time = 0
bounces = 0

square_size = 280  
rhombus_x = 200
rhombus_y = 200
initial_velocity = 15  
velocity = initial_velocity
max_velocity = 30  
direction = 0  

def draw_alpha_line(surface, color, start, end):
    temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.line(temp_surface, (*color, 50), start, end, 3)
    surface.blit(temp_surface, (0, 0))

def get_changing_color(time):
    r = int((math.sin(time * 0.02) + 1) * 127)
    g = int((math.sin(time * 0.02 + 2) + 1) * 127)
    b = int((math.sin(time * 0.02 + 4) + 1) * 127)
    return (r, g, b)

def find_nearest_vertex(point, vertices):
    return min(vertices, key=lambda v: ((v[0]-point[0])**2 + (v[1]-point[1])**2)**0.5)

def generate_reference_points():
    points = []
    for i in range(0, 301, 50):
        points.extend([
            (50, 50 + i),   
            (350, 50 + i),  
            (50 + i, 50),   
            (50 + i, 350)   
        ])
    return points

reference_points = generate_reference_points()

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    changing_color = get_changing_color(time)

    pygame.draw.rect(screen, changing_color, (50, 50, 300, 300), 4)

    text = font.render(f"Bounces: {bounces:02d}", True, WHITE)
    text_rect = text.get_rect(center=(width // 2, 30))
    screen.blit(text, text_rect)

    half_size = square_size // 2
    collision_occurred = False 

    if direction == 0:  
        rhombus_x += velocity
        if rhombus_x + half_size >= 350:
            rhombus_x = 350 - half_size
            direction = 1
            collision_occurred = True
    elif direction == 1:  
        rhombus_y += velocity
        if rhombus_y + half_size >= 350:
            rhombus_y = 350 - half_size
            direction = 2
            collision_occurred = True
    elif direction == 2:  
        rhombus_x -= velocity
        if rhombus_x - half_size <= 50:
            rhombus_x = 50 + half_size
            direction = 3
            collision_occurred = True
    elif direction == 3: 
        rhombus_y -= velocity
        if rhombus_y - half_size <= 50:
            rhombus_y = 50 + half_size
            direction = 0
            collision_occurred = True

    if collision_occurred:
        bounces += 1
        collision_sound.play()  

    seconds = time / 60  

    if seconds < 15:
        velocity = initial_velocity
        square_size = 280
    elif 15 <= seconds < 30:
        velocity = min(max_velocity, initial_velocity + (seconds - 15) * 0.1)
        square_size = max(200, 280 - (seconds - 15) * 2)
    elif 30 <= seconds < 45:
        velocity = max_velocity
        square_size = max(100, 200 - (seconds - 30) * 4)
    else:
        velocity = max_velocity
        square_size = 100

    vertices = [
        (rhombus_x, rhombus_y - half_size),   
        (rhombus_x + half_size, rhombus_y),  
        (rhombus_x, rhombus_y + half_size),  
        (rhombus_x - half_size, rhombus_y)  
    ]
    
    pygame.draw.polygon(screen, changing_color, vertices)

    for point in reference_points:
        nearest_vertex = find_nearest_vertex(point, vertices)
        draw_alpha_line(screen, changing_color, point, nearest_vertex)

    pygame.display.flip()

    frame = pygame.surfarray.array3d(screen)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = np.rot90(frame)
    frame = np.flipud(frame)
    out.write(frame)
    
    time += 1
    clock.tick(60)

out.release()

pygame.quit()