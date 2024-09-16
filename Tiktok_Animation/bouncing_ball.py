import pygame
import math
import random
import time
import cv2
import numpy as np

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball with Trails")

# Video recording setup
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('bouncing_ball.mp4', fourcc, 60.0, (WIDTH, HEIGHT))

trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 200
covering_border_thickness = 10

initial_ball_radius = 10
ball_radius = initial_ball_radius
max_ball_radius = circle_radius - 5
ball_pos = [WIDTH // 2 + 20, HEIGHT // 2 + 200 - circle_radius + ball_radius]
ball_velocity = [2, 2]

gravity = 0.1
ball_border_color = [255, 255, 255]
ball_border_thickness = 1

collision_lines = []
lines_per_collision = 10

VIBRANT_COLORS = [
    (204, 51, 51),    # Rojo oscuro
    (51, 51, 204),    # Azul oscuro
    (204, 204, 51),   # Amarillo oscuro
    (51, 204, 51),    # Verde oscuro
    (204, 51, 204),   # Morado oscuro
    (51, 204, 204),   # Celeste oscuro
    (204, 55, 0),     # Rojo-naranja oscuro
    (24, 115, 204),   # Azul dodger oscuro
    (204, 172, 0),    # Oro oscuro
    (40, 164, 40),    # Verde lima oscuro
    (174, 90, 171),   # Orquídea oscuro
    (0, 153, 204),    # Azul cielo profundo oscuro
]

def reflect(ball_pos, circle_center, ball_velocity):
    dx, dy = ball_pos[0] - circle_center[0], ball_pos[1] - circle_center[1]
    normal = [dx, dy]
    normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
    normal = [normal[0] / normal_length, normal[1] / normal_length]
    dot_product = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1]
    ball_velocity[0] -= 2 * dot_product * normal[0]
    ball_velocity[1] -= 2 * dot_product * normal[1]
    return ball_velocity

def random_vibrant_color():
    return random.choice(VIBRANT_COLORS)

running = True
clock = pygame.time.Clock()

current_color = random_vibrant_color()

start_time = time.time()
duration = 60  # duración en segundos

while running and time.time() - start_time < duration:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]

    ball_velocity[1] += gravity

    elapsed_time = time.time() - start_time
    growth_progress = min(elapsed_time / duration, 1)
    ball_radius = initial_ball_radius + (max_ball_radius - initial_ball_radius) * growth_progress

    distance = math.sqrt((ball_pos[0] - circle_center[0])**2 + (ball_pos[1] - circle_center[1])**2)
    if distance >= circle_radius - ball_radius:
        collision_point = [
            circle_center[0] + (ball_pos[0] - circle_center[0]) * circle_radius / distance,
            circle_center[1] + (ball_pos[1] - circle_center[1]) * circle_radius / distance
        ]
        
        current_color = random_vibrant_color()
        
        for _ in range(lines_per_collision):
            collision_lines.append((collision_point, current_color))

        ball_velocity = reflect(ball_pos, circle_center, ball_velocity)
        overlap = distance + ball_radius - circle_radius
        ball_pos[0] -= overlap * (ball_pos[0] - circle_center[0]) / distance
        ball_pos[1] -= overlap * (ball_pos[1] - circle_center[1]) / distance

    trail_surface.fill((0, 0, 0, 5))
    screen.blit(trail_surface, (0, 0))

    pygame.draw.circle(screen, current_color, circle_center, circle_radius + covering_border_thickness, covering_border_thickness)

    for line in collision_lines:
        circle_point, line_color = line
        pygame.draw.line(screen, line_color, circle_point, (int(ball_pos[0]), int(ball_pos[1])), 2)

    pygame.draw.circle(screen, current_color, (int(ball_pos[0]), int(ball_pos[1])), int(ball_radius))
    pygame.draw.circle(screen, ball_border_color, (int(ball_pos[0]), int(ball_pos[1])), int(ball_radius), ball_border_thickness)

    pygame.display.flip()

    # Convert Pygame surface to OpenCV image and write to video
    frame = pygame.surfarray.array3d(screen)
    frame = cv2.transpose(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    out.write(frame)

    clock.tick(60)

# Release video writer
out.release()

pygame.quit()