import pygame
import math
import colorsys
import cv2
import numpy as np

pygame.init()

width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Círculos en movimiento ondulatorio con rebotes naturales")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('circles_animation.mp4', fourcc, 60.0, (width, height))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

big_circle_radius = 300
center = (width // 2, height // 2)

small_circles = []
cardinal_points = [0, 90, 180, 270]  
for angle in cardinal_points:
    x = center[0] + big_circle_radius * math.cos(math.radians(angle))
    y = center[1] + big_circle_radius * math.sin(math.radians(angle))
    small_circles.append({
        'pos': [x, y],
        'angle': angle,
        'color': WHITE,
        'radius': 10,
        'velocity': [0, 0],
        'phase': 0
    })

angle = 0
speed = 2
wave_speed = 0.1
amplitude = 65

hue = 0
color_speed = 0.005

trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

clock = pygame.time.Clock()

def move_circles():
    global angle, hue
    
    growth_rate = 1.001
    
    for i, circle in enumerate(small_circles):
        base_angle = math.radians(i * 90 + angle)
        
        phase_adjustment = math.pi / 2
        wave_angle = angle * wave_speed + i * math.pi / 2 + phase_adjustment
        adjusted_wave = amplitude * math.sin(wave_angle)
        
        circle['radius'] *= growth_rate
        
        
        r = big_circle_radius - circle['radius'] - abs(adjusted_wave)
        theta = base_angle
        
        new_x = center[0] + r * math.cos(theta)
        new_y = center[1] + r * math.sin(theta)
        
        distance_to_center = math.sqrt((new_x - center[0])**2 + (new_y - center[1])**2)
        if distance_to_center + circle['radius'] > big_circle_radius:
            angle_to_center = math.atan2(new_y - center[1], new_x - center[0])
            new_x = center[0] + (big_circle_radius - circle['radius']) * math.cos(angle_to_center)
            new_y = center[1] + (big_circle_radius - circle['radius']) * math.sin(angle_to_center)
        
        circle['pos'] = [new_x, new_y]
        
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        circle_color = (int(r*255), int(g*255), int(b*255))
        circle['color'] = circle_color
        
        pygame.draw.circle(trail_surface, circle_color, (int(new_x), int(new_y)), int(circle['radius']))
        pygame.draw.circle(trail_surface, WHITE, (int(new_x), int(new_y)), int(circle['radius']), 1)
    
    angle += speed
    hue = (hue + color_speed) % 1
    
running = True
frame_count = 0
max_frames = 70 * 70  

running = True
frame_count = 0
max_frames = 70 * 70  

while running and frame_count < max_frames:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    move_circles()
    
    if any(circle['radius'] >= big_circle_radius for circle in small_circles):
        running = False
    
    screen.fill(BLACK)
    
    screen.blit(trail_surface, (0, 0))
    
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    big_circle_color = (int(r*255), int(g*255), int(b*255))
    pygame.draw.circle(screen, big_circle_color, center, big_circle_radius, 6)

    for circle in small_circles:
        pygame.draw.circle(screen, WHITE, (int(circle['pos'][0]), int(circle['pos'][1])), int(circle['radius']))
        pygame.draw.circle(screen, circle['color'], (int(circle['pos'][0]), int(circle['pos'][1])), int(circle['radius']) - 1)

    pygame.display.flip()
    
    pygame_surface_3d = pygame.surfarray.array3d(screen)
    opencv_surface_3d = cv2.transpose(pygame_surface_3d)
    opencv_surface_3d = cv2.cvtColor(opencv_surface_3d, cv2.COLOR_RGB2BGR)
    video.write(opencv_surface_3d)
    
    clock.tick(60)
    frame_count += 1

video.release()
pygame.quit()

print("Video grabado como 'circles_animation.mp4'")