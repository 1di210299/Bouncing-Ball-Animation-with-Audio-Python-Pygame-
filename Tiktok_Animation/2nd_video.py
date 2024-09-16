import pygame
import math
import random
import time
from moviepy.editor import ImageSequenceClip, AudioFileClip

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball with Trails")

trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 200
covering_border_thickness = 10

initial_ball_radius = 10
ball_radius = initial_ball_radius
max_ball_radius = circle_radius - 5
ball_pos = [WIDTH // 2 + 20, HEIGHT // 2 + 200 - circle_radius + ball_radius]
ball_velocity = [4, 4]

gravity = 0.25
ball_border_thickness = 1

collision_lines = []
lines_per_collision = 10

# Load the JPEG image for the ball
ball_image = pygame.image.load(r"D:\Plantillas personalizadas de Office\UpWork\Tiktok_Animation\mr_beast.jpeg")
use_image_for_ball = True

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

# Audio setup
bounce_sound_path = r"D:\Plantillas personalizadas de Office\UpWork\Tiktok_Animation\MrBeast_Song.mp3"
pygame.mixer.music.load(bounce_sound_path)
pygame.mixer.music.play(-1)  # Reproducir en bucle
pygame.mixer.music.pause()  # Inicialmente pausada

# Configuración de la duración de reproducción después de cada colisión
PLAY_DURATION = 300  # 0.3 segundos en milisegundos

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

def create_circular_image(image, size):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255), (size[0]//2, size[1]//2), size[0]//2)
    
    masked_image = pygame.Surface(size, pygame.SRCALPHA)
    masked_image.blit(image, (0, 0))
    masked_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    return masked_image

running = True
clock = pygame.time.Clock()

current_color = random_vibrant_color()
border_color = random_vibrant_color()

start_time = time.time()
duration = 60  # duración en segundos

music_playing = False
music_start_time = 0

frames = []
collision_times = []

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

    # Verificar si es tiempo de pausar la música
    if music_playing and pygame.time.get_ticks() - music_start_time > PLAY_DURATION:
        pygame.mixer.music.pause()
        music_playing = False

    distance = math.sqrt((ball_pos[0] - circle_center[0])**2 + (ball_pos[1] - circle_center[1])**2)
    if distance >= circle_radius - ball_radius:
        collision_point = [
            circle_center[0] + (ball_pos[0] - circle_center[0]) * circle_radius / distance,
            circle_center[1] + (ball_pos[1] - circle_center[1]) * circle_radius / distance
        ]
        
        current_color = random_vibrant_color()
        border_color = random_vibrant_color()
        
        for _ in range(lines_per_collision):
            collision_lines.append((collision_point, current_color, border_color))

        ball_velocity = reflect(ball_pos, circle_center, ball_velocity)
        overlap = distance + ball_radius - circle_radius
        ball_pos[0] -= overlap * (ball_pos[0] - circle_center[0]) / distance
        ball_pos[1] -= overlap * (ball_pos[1] - circle_center[1]) / distance
        
        # Reproducir la música
        pygame.mixer.music.unpause()
        music_playing = True
        music_start_time = pygame.time.get_ticks()
        collision_times.append(elapsed_time)
        
        # Movemos la pelota un poco para evitar que se quede pegada
        ball_pos[0] += ball_velocity[0] * 0.1
        ball_pos[1] += ball_velocity[1] * 0.1

    trail_surface.fill((0, 0, 0, 5))
    screen.blit(trail_surface, (0, 0))

    pygame.draw.circle(screen, border_color, circle_center, circle_radius + covering_border_thickness, covering_border_thickness)

    for line in collision_lines:
        circle_point, line_color, line_border_color = line
        pygame.draw.line(screen, line_color, circle_point, (int(ball_pos[0]), int(ball_pos[1])), 4)
        pygame.draw.line(screen, line_border_color, circle_point, (int(ball_pos[0]), int(ball_pos[1])), 6)

    if use_image_for_ball:
        ball_size = int(ball_radius * 2)
        resized_ball = pygame.transform.scale(ball_image, (ball_size, ball_size))
        
        circular_ball = create_circular_image(resized_ball, (ball_size, ball_size))
        
        ball_rect = circular_ball.get_rect(center=(int(ball_pos[0]), int(ball_pos[1])))
        screen.blit(circular_ball, ball_rect)
    else:
        pygame.draw.circle(screen, current_color, (int(ball_pos[0]), int(ball_pos[1])), int(ball_radius))
    
    pygame.draw.circle(screen, border_color, (int(ball_pos[0]), int(ball_pos[1])), int(ball_radius), ball_border_thickness)

    pygame.display.flip()
    
    # Capturar el frame actual
    frame = pygame.surfarray.array3d(screen)
    frames.append(frame)
    
    clock.tick(60)

pygame.quit()

# Crear el video con audio
clip = ImageSequenceClip(frames, fps=60)
audio = AudioFileClip(bounce_sound_path)

# Crear clips de audio para cada colisión
audio_clips = []
for collision_time in collision_times:
    start = collision_time
    end = min(start + PLAY_DURATION / 1000.0, clip.duration)
    audio_clip = audio.subclip(start, end).set_start(start)
    audio_clips.append(audio_clip)

# Combinar todos los clips de audio
from moviepy.audio.AudioClip import CompositeAudioClip  # Cambiado esta línea
final_audio = CompositeAudioClip(audio_clips)

# Añadir el audio al video
final_clip = clip.set_audio(final_audio)

# Guardar el video final
final_clip.write_videofile("bouncing_ball_animation_with_audio.mp4", audio_codec='aac')

print("Video con audio creado: bouncing_ball_animation_with_audio.mp4")