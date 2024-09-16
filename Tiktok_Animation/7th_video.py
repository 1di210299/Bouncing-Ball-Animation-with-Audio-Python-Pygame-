import pygame
import sys
import math
import random
import cv2
import numpy as np
import re
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeAudioClip
import os

# Inicializar Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bolas rebotando")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Círculo grande
big_circle_radius = 200
big_circle_pos = (width // 2, height // 2)

# Física
gravity = 0.1
elasticity = 0.95
impulse_boost = 1.05
max_speed = 10
min_speed = 2

# Barra de vida
life_count = 30
life_bar_width = 300
life_bar_height = 15
life_unit_width = life_bar_width // life_count

# Cargar efectos de sonido
inputNotes = 'CDEF'
note_sequence = re.findall(r'[A-G][^A-G]*', inputNotes)

# Definir additional_sounds primero
additional_sounds = ["Dsynthharpsoft.wav", "Esynthharpsoft.wav", "Fsynthharpsoft.wav"]

# Crear la lista de archivos de sonido
sound_files = [f"{note}synthharpsoft.wav" for note in note_sequence]
sound_files.extend(additional_sounds)

# Cargar los efectos de sonido
sound_effects = [pygame.mixer.Sound(sound_file) for sound_file in sound_files]

current_sound_index = 0
sound_times = []  # Lista para guardar los tiempos de los sonidos

def play_collision_sound(time):
    global current_sound_index
    sound_times.append((time, current_sound_index))
    current_sound_index = (current_sound_index + 1) % len(sound_effects)

# Clase para las bolas pequeñas
class SmallBall:
    def __init__(self, x, y, color):
        self.initial_radius = 20
        self.radius = self.initial_radius
        self.x = x
        self.y = y
        self.dx = random.uniform(-5, 5)
        self.dy = random.uniform(-5, 5)
        self.color = color
        self.life = life_count
        self.active = True
        self.is_winner = False
        self.flash_timer = 0

    def move(self):
        if not self.active:
            return
        self.dy += gravity
        
        # Limitar la velocidad
        speed = math.sqrt(self.dx**2 + self.dy**2)
        if speed > max_speed:
            factor = max_speed / speed
            self.dx *= factor
            self.dy *= factor
        elif speed < min_speed:
            factor = min_speed / speed
            self.dx *= factor
            self.dy *= factor
        
        self.x += self.dx
        self.y += self.dy

        # Comprobar colisión con el círculo grande
        dx = self.x - big_circle_pos[0]
        dy = self.y - big_circle_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        if distance > big_circle_radius - self.radius:
            normal_angle = math.atan2(dy, dx)
            tangent_angle = normal_angle + math.pi/2
            
            normal_vel = self.dx * math.cos(normal_angle) + self.dy * math.sin(normal_angle)
            tangent_vel = -self.dx * math.sin(normal_angle) + self.dy * math.cos(normal_angle)
            
            normal_vel *= -elasticity * impulse_boost
            
            self.dx = tangent_vel * -math.sin(normal_angle) + normal_vel * math.cos(normal_angle)
            self.dy = tangent_vel * math.cos(normal_angle) + normal_vel * math.sin(normal_angle)
            
            self.x = big_circle_pos[0] + (big_circle_radius - self.radius - 1) * math.cos(normal_angle)
            self.y = big_circle_pos[1] + (big_circle_radius - self.radius - 1) * math.sin(normal_angle)

    def draw(self):
        if self.active:
            color = self.color
            if self.flash_timer > 0:
                color = WHITE
                self.flash_timer -= 1
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.radius))
        if self.is_winner:
            pygame.draw.circle(screen, self.color, big_circle_pos, int(self.radius))

    def draw_life_bar(self, index):
        bar_x = width // 2 - life_bar_width // 2
        bar_y = height // 2 + big_circle_radius + 20 + index * (life_bar_height + 5)
        for i in range(self.life):
            pygame.draw.rect(screen, self.color, (bar_x + i * life_unit_width, bar_y, life_unit_width - 1, life_bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, life_bar_width, life_bar_height), 1)

    def shrink(self):
        self.radius = max(5, self.radius - 0.5)

    def grow(self):
        if self.is_winner:
            dx = self.x - big_circle_pos[0]
            dy = self.y - big_circle_pos[1]
            distance_to_center = math.sqrt(dx**2 + dy**2)
            
            growth_rate = (big_circle_radius - self.radius) / 30
            self.radius = min(self.radius + growth_rate, big_circle_radius)
            
            if distance_to_center > 1:
                move_rate = 0.1
                self.x += (big_circle_pos[0] - self.x) * move_rate
                self.y += (big_circle_pos[1] - self.y) * move_rate

# Crear bolas pequeñas
small_balls = [
    SmallBall(width//2, height//2, RED),
    SmallBall(width//2, height//2, GREEN),
    SmallBall(width//2, height//2, BLUE),
    SmallBall(width//2, height//2, YELLOW)
]

# Configuración de grabación
RECORD_TIME = 80  # segundos (1:20)
FPS = 70
frame_count = 0
max_frames = RECORD_TIME * FPS
frames = []

# Bucle principal
clock = pygame.time.Clock()
game_over = False
winner = None
while frame_count < max_frames and not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    pygame.draw.circle(screen, WHITE, big_circle_pos, big_circle_radius, 2)

    active_balls = [ball for ball in small_balls if ball.active]
    for ball in active_balls:
        ball.move()
        ball.draw()

    for i in range(len(active_balls)):
        for j in range(i + 1, len(active_balls)):
            ball1, ball2 = active_balls[i], active_balls[j]
            dx = ball2.x - ball1.x
            dy = ball2.y - ball1.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance < ball1.radius + ball2.radius:
                normal_angle = math.atan2(dy, dx)
                ball1_normal_vel = ball1.dx * math.cos(normal_angle) + ball1.dy * math.sin(normal_angle)
                ball2_normal_vel = ball2.dx * math.cos(normal_angle) + ball2.dy * math.sin(normal_angle)
                
                new_ball1_normal_vel = ((ball1_normal_vel * (ball1.radius - ball2.radius) + 
                                         2 * ball2.radius * ball2_normal_vel) / 
                                        (ball1.radius + ball2.radius))
                new_ball2_normal_vel = ((ball2_normal_vel * (ball2.radius - ball1.radius) + 
                                         2 * ball1.radius * ball1_normal_vel) / 
                                        (ball1.radius + ball2.radius))
                
                new_ball1_normal_vel *= elasticity * impulse_boost
                new_ball2_normal_vel *= elasticity * impulse_boost
                
                ball1.dx = new_ball1_normal_vel * math.cos(normal_angle) + ball1.dx * math.sin(normal_angle)
                ball1.dy = new_ball1_normal_vel * math.sin(normal_angle) - ball1.dy * math.cos(normal_angle)
                ball2.dx = new_ball2_normal_vel * math.cos(normal_angle) + ball2.dx * math.sin(normal_angle)
                ball2.dy = new_ball2_normal_vel * math.sin(normal_angle) - ball2.dy * math.cos(normal_angle)
                
                overlap = (ball1.radius + ball2.radius - distance) / 2
                ball1.x -= overlap * math.cos(normal_angle)
                ball1.y -= overlap * math.sin(normal_angle)
                ball2.x += overlap * math.cos(normal_angle)
                ball2.y += overlap * math.sin(normal_angle)

                for ball in [ball1, ball2]:
                    if ball.life > 0:
                        ball.life -= 1
                        ball.shrink()
                        ball.flash_timer = 5
                
                # Play sound only when balls collide with each other
                play_collision_sound(frame_count / FPS)

                if ball1.life <= 0:
                    ball1.active = False
                if ball2.life <= 0:
                    ball2.active = False

    for i, ball in enumerate(small_balls):
        if ball.active:
            ball.draw_life_bar(i)

    active_balls = [ball for ball in small_balls if ball.active]
    if len(active_balls) == 1:
        game_over = True
        winner = active_balls[0]
        winner.is_winner = True

    pygame.display.flip()
    
    frame = pygame.surfarray.array3d(screen)
    frame = frame.transpose([1, 0, 2])  # Ajustar el orden de los ejes
    frames.append(frame)
    
    frame_count += 1
    clock.tick(FPS)

while winner.radius < big_circle_radius and frame_count < max_frames:
    screen.fill(BLACK)
    pygame.draw.circle(screen, WHITE, big_circle_pos, big_circle_radius, 2)
    winner.grow()
    winner.draw()
    pygame.display.flip()
    
    frame = pygame.surfarray.array3d(screen)
    frame = frame.transpose([1, 0, 2])  # Ajustar el orden de los ejes
    frames.append(frame)
    
    frame_count += 1
    clock.tick(FPS)

pygame.quit()

video_clip = ImageSequenceClip(frames, fps=FPS)

audio_clips = []
for time, sound_index in sound_times:
    audio_clip = AudioFileClip(sound_files[sound_index]).set_start(time)
    audio_clips.append(audio_clip)

if audio_clips:
    final_audio = CompositeAudioClip(audio_clips)
    video_clip = video_clip.set_audio(final_audio)

video_clip.write_videofile("game_video_with_audio.mp4", codec="libx264", audio_codec="aac")

print("MP4 video with audio created successfully!")