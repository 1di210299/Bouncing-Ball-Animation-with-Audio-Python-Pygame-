import pygame
import moviepy.editor as mpy
import math
import random

pygame.init()

width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Complex Ball Animation')

black = (0, 0, 0)
white = (255, 255, 255)
vivid_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
base_color = random.choice(vivid_colors)
static_circle_color = random.choice(vivid_colors)

ball_radius = 15
max_radius = 250
growth_rate = (max_radius - ball_radius) / (60 * 120)  # Crecimiento más lento

# Parámetros de movimiento ajustados
gravity = 0.5
initial_speed = 15
max_speed = 25
min_speed = 5

ball = {
    "pos": [width // 2, height // 2],
    "vel": [random.uniform(-initial_speed, initial_speed), random.uniform(-initial_speed, initial_speed)],
    "color": base_color,
    "radius": ball_radius,
    "trail": [],
}

def get_gradient_color(base_color, offset, max_offset):
    ratio = offset / max_offset
    return tuple(int(base_color[i] * (1 - ratio) + 255 * ratio) for i in range(3))

def draw_smooth_circle(surface, color, pos, radius, width=0):
    target_rect = pygame.Rect(pos[0] - radius, pos[1] - radius, radius * 2, radius * 2)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius, width)
    surface.blit(shape_surf, target_rect)

def draw_scene(ball, static_circle_color, t):
    screen.fill(black)
    border_color = [int((math.sin(t * 5 + i * 2) + 1) / 2 * 255) for i in range(3)]
    draw_smooth_circle(screen, border_color, (width // 2, height // 2), max_radius, 5)
    for trail in ball["trail"]:
        draw_smooth_circle(screen, white, trail["pos"], int(trail["radius"]) + 1)
        draw_smooth_circle(screen, trail["color"], trail["pos"], int(trail["radius"]))
    for i in range(int(ball["radius"]), 0, -1):
        color = get_gradient_color(ball["color"], i, int(ball["radius"]))
        draw_smooth_circle(screen, color, [int(ball["pos"][0]), int(ball["pos"][1])], i)

def move_ball(ball):
    center = [width // 2, height // 2]
    
    # Aplicar gravedad
    ball["vel"][1] += gravity
    
    # Calcular nueva posición
    new_pos = [ball["pos"][0] + ball["vel"][0], ball["pos"][1] + ball["vel"][1]]
    
    # Comprobar si la nueva posición está dentro del círculo grande
    distance_from_center = math.sqrt((new_pos[0] - center[0])**2 + (new_pos[1] - center[1])**2)
    
    if distance_from_center + ball["radius"] > max_radius:
        # Si la nueva posición está fuera, calcular el punto de intersección con el borde
        angle = math.atan2(new_pos[1] - center[1], new_pos[0] - center[0])
        intersection = [
            center[0] + (max_radius - ball["radius"]) * math.cos(angle),
            center[1] + (max_radius - ball["radius"]) * math.sin(angle)
        ]
        
        # Calcular vector normal
        normal = [intersection[0] - center[0], intersection[1] - center[1]]
        normal_mag = math.sqrt(normal[0]**2 + normal[1]**2)
        normal = [normal[0] / normal_mag, normal[1] / normal_mag]
        
        # Reflejar velocidad
        dot_product = ball["vel"][0] * normal[0] + ball["vel"][1] * normal[1]
        ball["vel"][0] = ball["vel"][0] - 2 * dot_product * normal[0]
        ball["vel"][1] = ball["vel"][1] - 2 * dot_product * normal[1]
        
        # Añadir un impulso aleatorio en la colisión
        ball["vel"][0] += random.uniform(-2, 2)
        ball["vel"][1] += random.uniform(-2, 2)
        
        # Aplicar una pequeña pérdida de energía en la colisión
        ball["vel"][0] *= 0.98
        ball["vel"][1] *= 0.98
        
        ball["pos"] = intersection
    else:
        # Si la nueva posición está dentro, simplemente actualizar la posición
        ball["pos"] = new_pos

    # Asegurar una velocidad mínima
    speed = math.sqrt(ball["vel"][0]**2 + ball["vel"][1]**2)
    if speed < min_speed:
        ball["vel"][0] = (ball["vel"][0] / speed) * min_speed
        ball["vel"][1] = (ball["vel"][1] / speed) * min_speed

    # Limitar la velocidad máxima
    if speed > max_speed:
        ball["vel"][0] = (ball["vel"][0] / speed) * max_speed
        ball["vel"][1] = (ball["vel"][1] / speed) * max_speed

    # Actualizar el rastro
    if len(ball["trail"]) == 0 or (ball["trail"] and ball["trail"][-1]["pos"] != (int(ball["pos"][0]), int(ball["pos"][1]))):
        ball["trail"].append({
            "pos": (int(ball["pos"][0]), int(ball["pos"][1])),
            "color": ball["color"],
            "radius": ball["radius"]
        })
    
    if len(ball["trail"]) > 50:
        ball["trail"].pop(0)

    # Aumentar el radio de la pelota (crecimiento más lento)
    if ball["radius"] < max_radius:
        ball["radius"] += growth_rate

    return ball

def update_ball_color(ball, t):
    hue = (t * 30) % 360
    color = pygame.Color(0)
    color.hsva = (hue, 100, 100, 100)
    ball["color"] = (color.r, color.g, color.b)
    return ball

def make_frame(t):
    global ball
    ball = move_ball(ball)
    ball = update_ball_color(ball, t)
    draw_scene(ball, static_circle_color, t)
    return pygame.surfarray.array3d(screen).swapaxes(0, 1)

duration = 60  
fps = 30  

animation = mpy.VideoClip(make_frame, duration=duration)
animation = animation.set_fps(fps)

animation.write_videofile(r"C:\Users\LENOVO\Documents\complex_ball_animation.mp4", codec='libx264', bitrate="8000k")

pygame.quit()