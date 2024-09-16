import pygame
import math
from collections import deque
import colorsys
import random
import cv2
import numpy as np
from datetime import datetime, timedelta

pygame.init()

GAME_WIDTH, GAME_HEIGHT = 900, 800
INFO_WIDTH = 200  # Width for the information panel
WIDTH, HEIGHT = GAME_WIDTH + INFO_WIDTH, GAME_HEIGHT
CIRCLE_RADIUS = 350
COVERING_BORDER_THICKNESS = 10
INITIAL_BALL_RADIUS = 15
INNER_BALL_RADIUS_RATIO = 0.8
GRAVITY = 0.2
FRAME_RATE = 120
GLOW_DURATION = 60
GLOW_THICKNESS = 5
GLASS_BORDER_THICKNESS = 1
GLASS_ALPHA = 128
COLOR_CHANGE_SPEED = 0.009
BALL_GROWTH_RATE = 1
CONSTANT_SPEED = 5

MESSAGE_TOP = "HEY"
MESSAGE_BOTTOM = "MATT :)"
FONT_SIZE = 50
LETTER_SPACING = 20
VERTICAL_SPACING = 70
LETTER_RESOLUTION = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
MAX_WHITE = (245, 245, 220)

FULL_COVERAGE_RADIUS = CIRCLE_RADIUS
PAUSE_DURATION = 10000  # 3 seconds at 60 FPS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball with Growing Ball")

circle_center = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
ball_initial_pos = [GAME_WIDTH // 2 + 20, GAME_HEIGHT // 2 + 200 - CIRCLE_RADIUS + INITIAL_BALL_RADIUS]

trail = []
PAINT_SPEED = 0.04

MESSAGE_FONT = pygame.font.SysFont('Arial', FONT_SIZE, bold=True)
font = pygame.font.SysFont('Arial', 15)

def reflect(ball_pos, circle_center, ball_direction):
    dx, dy = ball_pos[0] - circle_center[0], ball_pos[1] - circle_center[1]
    normal = [dx, dy]
    normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
    
    if normal_length == 0:
        # Si la bola está en el centro, damos una dirección aleatoria
        angle = random.uniform(0, 2 * math.pi)
        return [math.cos(angle), math.sin(angle)]
    
    normal = [normal[0] / normal_length, normal[1] / normal_length]
    dot_product = ball_direction[0] * normal[0] + ball_direction[1] * normal[1]
    ball_direction[0] -= 2 * dot_product * normal[0]
    ball_direction[1] -= 2 * dot_product * normal[1]
    
    ball_direction[0] += random.uniform(-0.1, 0.1)
    ball_direction[1] += random.uniform(-0.1, 0.1)
    
    return ball_direction

def create_glass_circle(radius, border_thickness, color):
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(surface, (*color, GLASS_ALPHA), (radius, radius), radius)
    return surface

def draw_glowing_circle_border(surface, color, center, radius, border_thickness, glow_thickness, glow_alpha):
    outer_radius = radius + border_thickness
    pygame.draw.circle(surface, color, center, outer_radius)
    pygame.draw.circle(surface, BLACK, center, radius)
    
    if glow_thickness > 0:
        glow_surface = pygame.Surface((outer_radius * 2 + glow_thickness * 2, outer_radius * 2 + glow_thickness * 2), pygame.SRCALPHA)
        for i in range(glow_thickness):
            current_alpha = glow_alpha * (glow_thickness - i) / glow_thickness
            pygame.draw.circle(glow_surface, (*color, int(current_alpha)), 
                               (outer_radius + glow_thickness, outer_radius + glow_thickness), 
                               outer_radius + glow_thickness - i, 1)
        surface.blit(glow_surface, (center[0] - outer_radius - glow_thickness, center[1] - outer_radius - glow_thickness), special_flags=pygame.BLEND_ALPHA_SDL2)

def setup_message_sections(message_top, message_bottom):
    sections = []
    
    def setup_message(message, y_pos):
        total_width = sum(MESSAGE_FONT.size(char)[0] for char in message) + LETTER_SPACING * (len(message) - 1)
        start_x = circle_center[0] - total_width / 2
        
        for i, char in enumerate(message):
            char_surface = MESSAGE_FONT.render(char, True, MAX_WHITE)
            char_rect = char_surface.get_rect()
            char_rect.x = start_x + sum(MESSAGE_FONT.size(message[j])[0] + LETTER_SPACING for j in range(i))
            char_rect.y = y_pos - char_rect.height / 2
            
            segment_height = char_rect.height / LETTER_RESOLUTION
            char_segments = [0] * LETTER_RESOLUTION
            sections.append((char, char_rect, char_segments))
    
    setup_message(message_top, circle_center[1] - VERTICAL_SPACING / 2)
    setup_message(message_bottom, circle_center[1] + VERTICAL_SPACING / 2)
    
    return sections

def draw_trail(surface, trail, ball_radius, message_sections):
    for pos, color, radius in trail:
        inner_radius = int(radius * INNER_BALL_RADIUS_RATIO)
        pygame.draw.circle(surface, color, (int(pos[0]), int(pos[1])), inner_radius)
        glass_surface = create_glass_circle(radius, GLASS_BORDER_THICKNESS, BLACK)
        surface.blit(glass_surface, (int(pos[0]) - radius, int(pos[1]) - radius), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        for i, (char, rect, segments) in enumerate(message_sections):
            if rect.collidepoint(pos):
                segment_index = int((pos[1] - rect.top) / (rect.height / LETTER_RESOLUTION))
                if 0 <= segment_index < LETTER_RESOLUTION:
                    segments[segment_index] = min(segments[segment_index] + PAINT_SPEED, 1)
                message_sections[i] = (char, rect, segments)
    
    for char, rect, segments in message_sections:
        char_surface = MESSAGE_FONT.render(char, True, MAX_WHITE)
        masked_surface = pygame.Surface(char_surface.get_size(), pygame.SRCALPHA)
        
        for i, level in enumerate(segments):
            segment_height = rect.height / LETTER_RESOLUTION
            segment_rect = pygame.Rect(0, i * segment_height, rect.width, segment_height)
            segment_color = [int(c * level) for c in MAX_WHITE] + [int(255 * level)]
            pygame.draw.rect(masked_surface, segment_color, segment_rect)
        
        masked_surface.blit(char_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(masked_surface, rect)

def draw_ball(surface, pos, color, ball_radius):
    inner_radius = int(ball_radius * INNER_BALL_RADIUS_RATIO)
    pygame.draw.circle(surface, color, (int(pos[0]), int(pos[1])), inner_radius)
    glass_surface = create_glass_circle(ball_radius, GLASS_BORDER_THICKNESS-1, color)
    surface.blit(glass_surface, (int(pos[0]) - ball_radius, int(pos[1]) - ball_radius), special_flags=pygame.BLEND_ALPHA_SDL2)

def get_color(hue):
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return (int(r * 255), int(g * 255), int(b * 255))

def draw_info(surface, ball_radius, border_thickness, constant_speed):
    info_texts = [
        f"Ball Radius:",
        f"{ball_radius:.0f} px",
        f"Border Thickness:",
        f"{border_thickness} px",
        f"Ball Velocity:",
        f"{constant_speed:.0f} px/frame"
    ]
    
    total_height = sum(font.size(text)[1] for text in info_texts)
    start_y = (HEIGHT - total_height) // 2
    
    for i, text in enumerate(info_texts):
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.left = GAME_WIDTH + 10
        text_rect.top = start_y + i * (text_rect.height + 5)
        surface.blit(text_surface, text_rect)

def main():
    ball_pos = ball_initial_pos.copy()
    ball_velocity = [3, 3]
    glow_timer = 0
    hue = 0
    ball_radius = INITIAL_BALL_RADIUS
    
    message_sections = setup_message_sections(MESSAGE_TOP, MESSAGE_BOTTOM)
    
    clock = pygame.time.Clock()
    running = True
    
    pause_timer = 0
    covered = False
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 60.0, (WIDTH, HEIGHT))

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=70)
    frame_count = 0
    total_frames = 70 * FRAME_RATE
    
    while running and datetime.now() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if pause_timer > 0:
            pause_timer -= 1
            if pause_timer == 0:
                # Reset the ball after the pause
                ball_pos = ball_initial_pos.copy()
                ball_velocity = [2, 2]
                ball_radius = INITIAL_BALL_RADIUS
                covered = False
        else:
            # Apply gravity
            ball_velocity[1] += GRAVITY

            # Calculate speed factor based on ball size
            speed_factor = ball_radius / INITIAL_BALL_RADIUS

            # Move the ball with increased speed
            ball_pos[0] += ball_velocity[0] * speed_factor
            ball_pos[1] += ball_velocity[1] * speed_factor
            
        screen.fill(BLACK)
        
        distance = math.sqrt((ball_pos[0] - circle_center[0])**2 + (ball_pos[1] - circle_center[1])**2)
        if distance >= CIRCLE_RADIUS - ball_radius:
            ball_velocity = reflect(ball_pos, circle_center, ball_velocity)
            overlap = distance + ball_radius - CIRCLE_RADIUS
            if distance != 0:
                ball_pos[0] -= overlap * (ball_pos[0] - circle_center[0]) / distance
                ball_pos[1] -= overlap * (ball_pos[1] - circle_center[1]) / distance
            else:
                # Si la distancia es cero, mueve la bola en una dirección aleatoria
                angle = random.uniform(0, 2 * math.pi)
                ball_pos[0] = circle_center[0] + math.cos(angle) * (CIRCLE_RADIUS - ball_radius)
                ball_pos[1] = circle_center[1] + math.sin(angle) * (CIRCLE_RADIUS - ball_radius)
            
            glow_timer = GLOW_DURATION
            if ball_radius < FULL_COVERAGE_RADIUS:
                ball_radius += BALL_GROWTH_RATE
                ball_radius = min(ball_radius, FULL_COVERAGE_RADIUS)
                if ball_radius == FULL_COVERAGE_RADIUS and not covered:
                    covered = True
                    pause_timer = PAUSE_DURATION
        
        # Update color
        hue = (hue + COLOR_CHANGE_SPEED) % 1
        current_color = get_color(hue)
        
        # Add current position to trail
        trail.append((ball_pos.copy(), current_color, ball_radius))
        
        screen.fill(BLACK)  # Fill the entire screen with black
        
        if glow_timer > 0:
            glow_alpha = int(255 * (glow_timer / GLOW_DURATION))
            draw_glowing_circle_border(screen, WHITE, circle_center, CIRCLE_RADIUS, COVERING_BORDER_THICKNESS, GLOW_THICKNESS, glow_alpha)
            glow_timer -= 1
        else:
            draw_glowing_circle_border(screen, WHITE, circle_center, CIRCLE_RADIUS, COVERING_BORDER_THICKNESS, 0, 0)
        
        draw_trail(screen, trail, ball_radius, message_sections)
        draw_ball(screen, ball_pos, current_color, ball_radius)
        
        # Calculate current speed
        current_speed = math.sqrt(ball_velocity[0]**2 + ball_velocity[1]**2) * speed_factor
        draw_info(screen, ball_radius, COVERING_BORDER_THICKNESS, current_speed)
        
        pygame.display.flip()
        
        # Capturar la pantalla y guardarla en el video
        screen_array = pygame.surfarray.array3d(screen)
        screen_array = cv2.rotate(screen_array, cv2.ROTATE_90_CLOCKWISE)
        screen_array = cv2.flip(screen_array, 1)
        out.write(screen_array)
        
        clock.tick(FRAME_RATE)
    
    pygame.quit()
    out.release()

    print("Video guardado como 'output.mp4'")

if __name__ == "__main__":
    main()