import pygame
import math
import time
import sys
import colorsys
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeAudioClip

def log_message(message):
    print(f"[{time.time()}] {message}")

log_message("Iniciando el programa")

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Revealing Circle Image")

circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 200
ball_radius = 10

speed = 10  # Increased from 8
angle = math.pi / 4
gravity = 0.1  # Reduced from 0.15

gray_color = (128, 128, 128)
circle_border_color = gray_color

revealed_angles = set()
angle_range = math.pi / 12  # Changed from math.pi / 24

target_time = 60

trail_length = 10
trail_update_frequency = 3

flashes = []
hue = 0
frames = []

BOUNCE_DURATION = 400  
collision_times = []

is_music_playing = False

try:
    bounce_sound_path = r"D:\Plantillas personalizadas de Office\UpWork\Tiktok_Animation\nomo_audio.mp3"
    full_audio = AudioFileClip(bounce_sound_path)
    log_message("Audio cargado exitosamente")
except Exception as e:
    log_message(f"Error al cargar el audio: {e}")
    full_audio = None

try:
    reveal_image = pygame.image.load('D:/Plantillas personalizadas de Office/UpWork/Tiktok_Animation/Foto.jpeg')
    reveal_image = pygame.transform.scale(reveal_image, (circle_radius * 2, circle_radius * 2))
    log_message("Imagen cargada exitosamente")
except pygame.error as e:
    log_message(f"Error al cargar la imagen: {e}")
    reveal_image = pygame.Surface((circle_radius * 2, circle_radius * 2))
    reveal_image.fill((255, 0, 0))

circular_mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(circular_mask, (255, 255, 255), (circle_radius, circle_radius), circle_radius)
reveal_image.blit(circular_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

reveal_mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
reveal_mask.fill((0, 0, 0, 255))

def add_revealed_angle(angle):
    global revealed_angles
    revealed_angles.add(angle)
    revealed_angles.add((angle + angle_range/2) % (2 * math.pi))
    revealed_angles.add((angle - angle_range/2) % (2 * math.pi))
    update_reveal_mask()

def update_reveal_mask():
    reveal_mask.fill((0, 0, 0, 255))
    for angle in revealed_angles:
        points = [
            (circle_radius, circle_radius),
            (circle_radius + math.cos(angle - angle_range/2) * circle_radius * 2, 
             circle_radius - math.sin(angle - angle_range/2) * circle_radius * 2),
            (circle_radius + math.cos(angle + angle_range/2) * circle_radius * 2, 
             circle_radius - math.sin(angle + angle_range/2) * circle_radius * 2)
        ]
        pygame.draw.polygon(reveal_mask, (255, 255, 255, 0), points)

def reflect(ball_pos, circle_center, ball_velocity, circle_radius):
    global hue, collision_times, is_music_playing
    dx, dy = ball_pos[0] - circle_center[0], ball_pos[1] - circle_center[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance > circle_radius - ball_radius:
        normal = [dx / distance, dy / distance]
        dot_product = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1]
        ball_velocity[0] -= 2 * dot_product * normal[0]
        ball_velocity[1] -= 2 * dot_product * normal[1]
        
        ball_pos[0] = circle_center[0] + normal[0] * (circle_radius - ball_radius)
        ball_pos[1] = circle_center[1] + normal[1] * (circle_radius - ball_radius)
    
        angle = math.atan2(-dy, dx)
        add_revealed_angle(angle)
        
        current_time = pygame.time.get_ticks()
        collision_times.append(current_time)
        
        hue = (hue + 0.1) % 1.0
        is_music_playing = True
        new_color = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1, 1))
        return ball_velocity, ball_pos, new_color
    
    return ball_velocity, ball_pos, None

def update_ball(ball):
    ball_pos, ball_velocity = ball['pos'], ball['velocity']
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]
    ball_velocity[1] += gravity
    
    dx = ball_pos[0] - circle_center[0]
    dy = ball_pos[1] - circle_center[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance > circle_radius - ball_radius:
        ball_velocity, ball_pos, new_color = reflect(ball_pos, circle_center, ball_velocity, circle_radius)
        if new_color:
            ball['color'] = new_color
            flashes.append({'pos': ball_pos[:], 'color': new_color, 'time': 30})
    
    current_speed = math.sqrt(ball_velocity[0]**2 + ball_velocity[1]**2)
    if current_speed < speed and current_speed != 0:
        ball_velocity[0] *= speed / current_speed
        ball_velocity[1] *= speed / current_speed
    
    ball['pos'] = ball_pos
    ball['velocity'] = ball_velocity

def get_trail_color(color, fraction):
    return tuple(int(c * (0.3 + 0.7 * fraction)) for c in color)

def draw_flash(flash):
    pos = flash['pos']
    color = flash['color']
    time = flash['time']
    size = 20 * (time / 30)
    opacity = int(255 * (time / 30))
    flash_color = color + (opacity,)
    
    points = []
    for i in range(8):
        angle = i * (2 * math.pi / 8)
        distance = size if i % 2 == 0 else size / 2
        point = (pos[0] + distance * math.cos(angle), pos[1] + distance * math.sin(angle))
        points.append(point)
    
    pygame.draw.polygon(screen, flash_color, points)

# Initialize multiple balls
num_balls = 3
balls = []
for _ in range(num_balls):
    balls.append({
        'pos': [WIDTH // 2 + 100, HEIGHT // 2],
        'velocity': [speed * math.cos(angle), speed * math.sin(angle)],
        'color': gray_color,
        'trail': []
    })

running = True
clock = pygame.time.Clock()
frame_count = 0
start_ticks = pygame.time.get_ticks()

cleanup_phase = False
cleanup_start_time = 0

log_message("Iniciando bucle principal")

try:
    while running and (pygame.time.get_ticks() - start_ticks < target_time * 1000 or cleanup_phase):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        if not cleanup_phase:
            for ball in balls:
                update_ball(ball)

                frame_count += 1
                if frame_count % trail_update_frequency == 0:
                    ball['trail'].append((int(ball['pos'][0]), int(ball['pos'][1])))
                    if len(ball['trail']) > trail_length:
                        ball['trail'].pop(0)

            # Check if it's time to start the cleanup phase
            if pygame.time.get_ticks() - start_ticks >= target_time * 1000:
                cleanup_phase = True
                cleanup_start_time = pygame.time.get_ticks()
        else:
            # Clean-up phase: Reveal any remaining sections
            for angle in np.linspace(0, 2*math.pi, 100):
                if angle not in revealed_angles:
                    add_revealed_angle(angle)
            
            # End the cleanup phase after 5 seconds
            if pygame.time.get_ticks() - cleanup_start_time > 5000:
                running = False

        # Draw the revealed image
        revealed_image = reveal_image.copy()
        revealed_image.blit(reveal_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(revealed_image, (circle_center[0] - circle_radius, circle_center[1] - circle_radius))

        pygame.draw.circle(screen, circle_border_color, circle_center, circle_radius, 3)

        for ball in balls:
            for i, pos in enumerate(ball['trail']):
                fraction = i / (len(ball['trail']) - 1) if len(ball['trail']) > 1 else 1
                color = get_trail_color(ball['color'], fraction)
                pygame.draw.circle(screen, color, pos, ball_radius)

        for flash in flashes[:]:
            draw_flash(flash)
            flash['time'] -= 1
            if flash['time'] <= 0:
                flashes.remove(flash)

        for ball in balls:
            pygame.draw.circle(screen, ball['color'], (int(ball['pos'][0]), int(ball['pos'][1])), ball_radius)

        pygame.display.flip()

        frame = pygame.surfarray.array3d(screen)
        frame = np.transpose(frame, (1, 0, 2))
        frames.append(frame)

        clock.tick(60)

        if frame_count % 60 == 0:
            log_message(f"Frames procesados: {frame_count}")

except Exception as e:
    log_message(f"Se produjo un error: {e}")
    import traceback
    traceback.print_exc()

finally:
    log_message("Finalizando el programa")
    pygame.quit()

try:
    log_message("Creando el video")
    clip = ImageSequenceClip(frames, fps=60)
    
    audio_path = r"D:\Plantillas personalizadas de Office\UpWork\Tiktok_Animation\nomo_audio.mp3"
    
    full_audio = AudioFileClip(audio_path)
    video_duration = len(frames) / 60  # duración en segundos
    log_message(f"Duración del video: {video_duration:.2f}s")

    # Crear clips de audio para cada colisión
    audio_clips = []
    for collision_time in collision_times:
        start = (collision_time - start_ticks) / 1000.0  # convertir a segundos
        end = min(start + BOUNCE_DURATION / 1000.0, video_duration, full_audio.duration)
        if start < full_audio.duration:
            audio_clip = full_audio.subclip(start, end).set_start(start)
            audio_clips.append(audio_clip)
    
    final_audio = CompositeAudioClip(audio_clips)
    
    final_clip = clip.set_audio(final_audio)

    log_message("Audio añadido al video correctamente")
    log_message(f"Número de colisiones: {len(collision_times)}")

    output_path = r"D:/Plantillas personalizadas de Office/UpWork/Tiktok_Animation/bouncing_ball_animation_with_audio.mp4"
    final_clip.write_videofile(output_path, fps=60, audio_codec='aac')
    log_message("Video guardado con éxito")

except Exception as e:
    log_message(f"Error al crear o guardar el video: {e}")
    import traceback
    traceback.print_exc()

log_message("Programa finalizado")
sys.exit()