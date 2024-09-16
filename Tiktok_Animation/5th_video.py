import pygame
import sys
import math
import colorsys
import cv2
import numpy as np

pygame.init()

width, height = 500, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Círculos concéntricos con bordes oscuros")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BONE_WHITE = (255, 255, 240)

center = (width // 2, height // 2)
initial_big_radius = 180
big_radius = initial_big_radius
small_radius = 20
ball_radius = small_radius // 2
line_thickness = 4

time = 0
base_speed = 0.009
speed = base_speed

collision_count = 0

lines_visible = True

total_time = 0
max_duration = 60

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('animation.mp4', fourcc, 30, (width, height))

def calculate_ball_position(start, end, t):
    x = start[0] + (end[0] - start[0]) * t
    y = start[1] + (end[1] - start[1]) * t
    return (x, y)

def check_collision(ball_pos, center, small_radius):
    distance = math.sqrt((ball_pos[0] - center[0])**2 + (ball_pos[1] - center[1])**2)
    return distance <= small_radius + ball_radius

def generate_vibrant_rainbow_colors(num_colors):
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
        colors.append((int(r * 255), int(g * 255), int(b * 255)))
    return colors

def interpolate_color(color1, color2, t):
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

def darken_color(color, factor=0.5):
    return tuple(int(c * factor) for c in color)

def draw_circle_with_dark_border(surface, color, center, radius, border_width=2):
    dark_color = darken_color(color)
    pygame.draw.circle(surface, dark_color, center, radius + border_width)
    pygame.draw.circle(surface, color, center, radius)

def draw_circle_with_glow(surface, color, center, radius, glow_width=3):
    for i in range(glow_width, 0, -1):
        alpha = int(255 * (1 - i / glow_width) * 0.3)
        glow_color = (*color[:3], alpha)
        pygame.draw.circle(surface, glow_color, center, radius + i, 1)
    pygame.draw.circle(surface, BLACK, center, radius)
    pygame.draw.circle(surface, color, center, radius, 2)

def ease_out_cubic(t):
    return 1 - math.pow(1 - t, 3)

def lerp(a, b, t):
    return a + (b - a) * t

num_balls = 8
ball_colors = generate_vibrant_rainbow_colors(num_balls)
collision_timers = [0] * num_balls

ball_speeds = [2.0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3]
ball_times = [0] * num_balls

clock = pygame.time.Clock()
running = True
shrinking = True
start_time = pygame.time.get_ticks()
while running and (pygame.time.get_ticks() - start_time) < 60000:  # 60000 ms = 60 segundos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    time += speed
    if time > 1:
        time = 0

    screen.fill(BLACK)

    draw_circle_with_glow(screen, WHITE, center, big_radius)

    all_directions = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
    ball_positions = []
    collision_this_frame = False
    for i, (dx, dy) in enumerate(all_directions):
        ball_times[i] += speed / ball_speeds[i]
        if ball_times[i] > 1:
            ball_times[i] -= 1

        if dx * dy == 0:  
            start = (center[0] + dx * small_radius, center[1] + dy * small_radius)
            end = (center[0] + dx * (big_radius - ball_radius), center[1] + dy * (big_radius - ball_radius))
        else:
            diagonal_start = small_radius / math.sqrt(2)
            diagonal_end = (big_radius - ball_radius) / math.sqrt(2)
            start = (center[0] + dx * diagonal_start, center[1] + dy * diagonal_start)
            end = (center[0] + dx * diagonal_end, center[1] + dy * diagonal_end)

        ball_pos = calculate_ball_position(start, end, abs(math.sin(ball_times[i] * math.pi)))
        ball_positions.append(ball_pos)

        if check_collision(ball_pos, center, small_radius):
            collision_timers[i] = 1.0
            collision_this_frame = True

        if lines_visible:
            current_color = interpolate_color(ball_colors[i], WHITE, collision_timers[i])
        else:
            current_color = ball_colors[i]

        if lines_visible:
            pygame.draw.line(screen, current_color, start, end, line_thickness)

        collision_timers[i] = max(0, collision_timers[i] - 0.02)  

    if lines_visible:
        pygame.draw.lines(screen, WHITE, True, ball_positions, 2)

    for i, ball_pos in enumerate(ball_positions):
        if lines_visible:
            current_color = interpolate_color(ball_colors[i], WHITE, collision_timers[i])
        else:
            current_color = ball_colors[i]
        draw_circle_with_dark_border(screen, current_color, ball_pos, ball_radius)

    if collision_this_frame and shrinking:
        if big_radius > small_radius + 2 * ball_radius:
            big_radius -= max(0.1, (big_radius / initial_big_radius) * 0.1)
            speed = base_speed * (initial_big_radius / big_radius)
            collision_count += 1
        else:
            shrinking = False

    if big_radius <= small_radius + 2 * ball_radius:
        lines_visible = False

    draw_circle_with_dark_border(screen, BONE_WHITE, center, small_radius, 3)

    font = pygame.font.Font(None, 24)
    text = font.render(f"Colisiones: {collision_count}", True, WHITE)
    text_rect = text.get_rect()
    text_rect.bottomright = (width - 10, height - 10) 
    screen.blit(text, text_rect)

    pygame.display.flip()

    string_image = pygame.image.tostring(screen, 'RGB')
    temp_surf = pygame.image.fromstring(string_image, (width, height), 'RGB')
    frame = pygame.surfarray.array3d(temp_surf)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = cv2.flip(frame, 0) 
    video.write(frame)

    clock.tick(50) 

video.release()

pygame.quit()
sys.exit()