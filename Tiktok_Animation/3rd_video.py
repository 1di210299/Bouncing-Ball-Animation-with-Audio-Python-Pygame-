import pygame
import math
import random
import cv2
import numpy as np
import pygame.gfxdraw
import librosa
import numpy as np
import pygame
import librosa
import subprocess
import os
from moviepy.editor import VideoFileClip, AudioFileClip


pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
# Cargar la canción y extraer características
ruta_cancion = r"D:\Plantillas personalizadas de Office\UpWork\Tiktok_Animation\Post_Malone_Swae_Lee_-_Sunflower_Spider-Man_Into_the_Spider-Verse_[_YouConvert.net_].mp3"
y, sr = librosa.load(ruta_cancion, offset=40.0)  # Comienza a cargar desde el segundo 40

# Ajusta el tiempo de inicio para los cálculos posteriores
tiempo_inicio_cancion = 40.0
segmento_actual = 0

onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
mfcc = librosa.feature.mfcc(y=y, sr=sr)

# Extraer el ritmo y la melodía
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr) + tiempo_inicio_cancion

# Extraer las características armónicas
chroma = librosa.feature.chroma_stft(y=y, sr=sr)

def crear_sonido_colision_xilofono(frecuencia, duracion=0.5, volumen=2):
    sr = 44100
    t = np.linspace(0, duracion, int(sr * duracion), False)
    
    # Ajustamos la frecuencia base para tener más variedad
    frecuencia_base = frecuencia * np.random.uniform(0.98, 1.02)
    
    # Armónicos para simular el sonido de un xilófono con más claridad
    armonicos = [1, 2, 3, 4]
    amplitudes = [1.0, 0.3, 0.1, 0.05]  # Enfatizamos más el tono fundamental
    
    senal = np.zeros_like(t)
    for armonico, amplitud in zip(armonicos, amplitudes):
        senal += amplitud * np.sin(2 * np.pi * frecuencia_base * armonico * t)
    
    # Envelope para un decay más rápido, mejorando la claridad
    envelope = np.exp(-t * 30)
    
    senal *= envelope
    senal = np.clip(senal, -1, 1)
    senal *= volumen
    
    # Aplicamos un filtro simple de paso alto
    senal = senal - np.mean(senal)
    
    senal = (senal * 32767).astype(np.int16)
    estereo = np.column_stack((senal, senal))
    
    return pygame.sndarray.make_sound(estereo)

def crear_paleta_sonidos_armonicos():
    sonidos = []
    # Usamos una escala de notas más espaciada para mayor distinción
    notas_base = [60, 62, 64, 65, 67, 69, 71]  # Escala de Do mayor (C4 a B4)
    for nota_midi in notas_base:
        frecuencia = librosa.midi_to_hz(nota_midi)
        sonido = crear_sonido_colision_xilofono(frecuencia, duracion=0.25, volumen=0.8)
        sonidos.append(sonido)
    return sonidos

sonidos_armonicos = crear_paleta_sonidos_armonicos()

# Dentro de la clase QuarterCircle
def play_sonido_apofenia(self):
    indice_sonido = int((self.position[0] + self.position[1] + abs(self.velocity[0]) + abs(self.velocity[1])) % len(sonidos_armonicos))
    volumen = min(0.8, self.actual_size / self.max_radius)  # Limitamos el volumen máximo
    
    sonido = sonidos_armonicos[indice_sonido]
    sonido.set_volume(volumen)
    
    pygame.mixer.Sound.play(sonido)
    
    nombres_notas = ['Do', 'Mi', 'Sol', 'Si', 'Re', 'Fa', 'La']
    nombre_nota = nombres_notas[indice_sonido % len(nombres_notas)]
    print(f"Reproduciendo sonido de xilófono: {nombre_nota}")
########################################################################################
########################################################################################
########################################################################################
########################################################################################



width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cuartos de círculo en movimiento espejado")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('output.mp4', fourcc, 60.0, (width, height))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

big_ball_radius = 250
small_ball_radius = 15
center_x, center_y = width // 2, height // 2
STATIC_CIRCLE_RADIUS = 100
BIG_CIRCLE_BORDER_WIDTH = 8
VISUAL_MARGIN = 0.01  
ACTUAL_MARGIN = 10

def generate_color_variants(base_color, num_variants=10):
    variants = [base_color]
    r, g, b = base_color
    step = 15
    
    for i in range(1, num_variants // 2):
        new_r = max(0, r - step * i)
        new_g = max(0, g - step * i)
        new_b = max(0, b - step * i)
        variants.append((new_r, new_g, new_b))

    for i in range(1, num_variants // 2):
        new_r = min(255, r + step * i)
        new_g = min(255, g + step * i)
        new_b = min(255, b + step * i)
        variants.append((new_r, new_g, new_b))

    return variants

base_colors = {
    0: (255, 105, 180),  
    1: (50, 205, 50),    
    2: (30, 144, 255),   
    3: (255, 165, 0)     
}

color_palettes = {k: generate_color_variants(v) for k, v in base_colors.items()}

def is_inside_big_circle(x, y, radius, margin=0):
    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
    return distance + radius <= big_ball_radius - margin / 2  

class QuarterCircle:
    def __init__(self, quadrant, is_main=False):
        self.quadrant = quadrant
        self.colors = color_palettes[quadrant]
        self.color_index = 0
        self.is_main = is_main
        self.trail = []
        self.trail_length = 20
        self.radius = small_ball_radius
        self.position = self.initial_position()
        self.speed = 5
        angle = random.uniform(0, math.pi/2)
        self.velocity = [self.speed * math.cos(angle), self.speed * math.sin(angle)]
        self.collision_count = 0
        self.max_radius = big_ball_radius
        self.current_color = self.colors[0]
        self.target_color = self.colors[1]
        self.color_transition = 0
        self.color_transition_speed = 0.01
        self.interpolated_color = self.current_color
        self.max_size_timer = 0
        self.shrink_rate = 0.5
        self.direction_change_timer = 0
        self.direction_change_interval = random.randint(60, 180)  
        self.size_at_last_collision = small_ball_radius
        self.growth_per_collision = 2
        self.actual_size = small_ball_radius
        self.position = self.initial_position()
        angle = random.uniform(0, math.pi/2)
        self.velocity = [self.speed * math.cos(angle), self.speed * math.sin(angle)]
        self.bounce_margin = 0.000001
        self.original_position = self.initial_position()
        self.shrink_rate = 2  
        self.min_size = small_ball_radius  
        self.state = "growing"
        self.shrink_rate = 2  
        self.max_size_duration = 4 * 60  
        self.segmento_actual = 0
        self.ultimo_tiempo = 0

########################################################################################
########################################################################################
########################################################################################
########################################################################################
   
    
    def play_sonido_apofenia(self):
        indice_sonido = int((self.position[0] + self.position[1] + abs(self.velocity[0]) + abs(self.velocity[1])) % len(sonidos_armonicos))
        volumen = min(0.9, self.actual_size / self.max_radius)  # Limitamos el volumen máximo
        
        sonido = sonidos_armonicos[indice_sonido]
        sonido.set_volume(volumen)
        
        # Limitamos la cantidad de sonidos simultáneos
        if pygame.mixer.get_busy():
            pygame.mixer.stop()
        
        pygame.mixer.Sound.play(sonido)
        
        nombres_notas = ['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Si']
        nombre_nota = nombres_notas[indice_sonido % len(nombres_notas)]
        print(f"Reproduciendo sonido de xilófono: {nombre_nota}")
    ########################################################################################
########################################################################################
########################################################################################
########################################################################################
        
    def initial_position(self):
        angle = (self.quadrant * math.pi/2) + (math.pi/4)
        x = center_x + (big_ball_radius - self.radius) * math.cos(angle)
        y = center_y + (big_ball_radius - self.radius) * math.sin(angle)
        return [x, y]

    def move(self):
        global segmento_actual, center_x, center_y 
        if self.is_main:
            if self.state == "growing":
                new_x = self.position[0] + self.velocity[0]
                new_y = self.position[1] + self.velocity[1]

                rel_x = new_x - center_x
                rel_y = new_y - center_y
                distance = math.sqrt(rel_x**2 + rel_y**2)

                rebote = False

                if distance > big_ball_radius - self.radius:
                    angle = math.atan2(rel_y, rel_x)
                    new_x = center_x + (big_ball_radius - self.radius + 0.1) * math.cos(angle)
                    new_y = center_y + (big_ball_radius - self.radius + 0.1) * math.sin(angle)
                    
                    normal = [rel_x / distance, rel_y / distance]
                    self.velocity = self.reflect(self.velocity, normal)
                    rebote = True

                if new_x < center_x:
                    new_x = center_x
                    self.velocity[0] = abs(self.velocity[0])
                    rebote = True
                if new_y < center_y:
                    new_y = center_y
                    self.velocity[1] = abs(self.velocity[1])
                    rebote = True

                if rebote:
                    self.collision_count += 1
                    self.play_sonido_apofenia()
                    print("Colisión detectada, reproduciendo sonido")
                    if self.actual_size < self.max_radius:
                        self.actual_size = min(self.actual_size * 1.03, self.max_radius)
                    if self.actual_size >= self.max_radius * 0.995:
                        self.state = "max_size"
                        self.max_size_timer = 0
                        
                        self.position[0] += (center_x - self.position[0]) * 0.1
                        self.position[1] += (center_y - self.position[1]) * 0.1
                        return
                    
                self.position = [new_x, new_y]
                
                tiempo_actual = pygame.time.get_ticks() / 1000.0 + tiempo_inicio_cancion
                if segmento_actual < len(beat_times) and tiempo_actual >= beat_times[segmento_actual]:
                    self.play_sonido_apofenia()
                    segmento_actual += 1

                distance = math.sqrt((self.position[0] - center_x)**2 + (self.position[1] - center_y)**2)
                if distance > big_ball_radius - self.radius:
                    angle = math.atan2(self.position[1] - center_y, self.position[0] - center_x)
                    self.position[0] = center_x + (big_ball_radius - self.radius) * math.cos(angle)
                    self.position[1] = center_y + (big_ball_radius - self.radius) * math.sin(angle)

                self.position[0] = max(center_x, min(self.position[0], center_x + big_ball_radius - self.radius))
                self.position[1] = max(center_y, min(self.position[1], center_y + big_ball_radius - self.radius))

            elif self.state == "max_size":
                self.max_size_timer += 1
                if self.max_size_timer >= self.max_size_duration:
                    self.state = "shrinking"
                    self.position = self.original_position

            elif self.state == "shrinking":
                self.actual_size = max(self.actual_size - self.shrink_rate, self.min_size)
                if self.actual_size <= self.min_size:
                    self.state = "growing"
                    self.actual_size = self.min_size

            self.radius = self.actual_size

            self.trail.append(self.get_position())
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)

            distance = math.sqrt((self.position[0] - center_x)**2 + (self.position[1] - center_y)**2)
            if distance > big_ball_radius - self.radius:
                angle = math.atan2(self.position[1] - center_y, self.position[0] - center_x)
                self.position[0] = center_x + (big_ball_radius - self.radius) * math.cos(angle)
                self.position[1] = center_y + (big_ball_radius - self.radius) * math.sin(angle)

            self.position[0] = max(center_x, min(self.position[0], center_x + big_ball_radius - self.radius))
            self.position[1] = max(center_y, min(self.position[1], center_y + big_ball_radius - self.radius))

            self.trail.append(self.get_position())
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)

            distance = math.sqrt((self.position[0] - center_x)**2 + (self.position[1] - center_y)**2)
        if distance > big_ball_radius - self.radius:
            angle = math.atan2(self.position[1] - center_y, self.position[0] - center_x)
            self.position[0] = center_x + (big_ball_radius - self.radius) * math.cos(angle)
            self.position[1] = center_y + (big_ball_radius - self.radius) * math.sin(angle)

        self.position[0] = max(center_x, min(self.position[0], center_x + big_ball_radius - self.radius))
        self.position[1] = max(center_y, min(self.position[1], center_y + big_ball_radius - self.radius))

        self.trail.append(self.get_position())
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        
    def reflect(self, velocity, normal):
        dot_product = velocity[0]*normal[0] + velocity[1]*normal[1]
        return [
            velocity[0] - 2 * dot_product * normal[0],
            velocity[1] - 2 * dot_product * normal[1]
        ]

    def get_position(self):
        return int(self.position[0]), int(self.position[1])

    def mirror_position(self, main_quarter):
        if main_quarter.state == "max_size":
            self.position = [center_x, center_y]
        else:
            rel_x = main_quarter.position[0] - center_x
            rel_y = main_quarter.position[1] - center_y
                                        
            if self.quadrant == 1:
                self.position[0] = center_x - rel_x
                self.position[1] = center_y + rel_y
            elif self.quadrant == 2:
                self.position[0] = center_x - rel_x
                self.position[1] = center_y - rel_y
            elif self.quadrant == 3:
                self.position[0] = center_x + rel_x
                self.position[1] = center_y - rel_y
        
        self.radius = main_quarter.radius
        self.actual_size = main_quarter.actual_size
        self.state = main_quarter.state
        self.max_size_timer = main_quarter.max_size_timer

    def update_color(self):
        self.color_transition += self.color_transition_speed
        if self.color_transition >= 1:
            self.color_transition = 0
            self.current_color = self.target_color
            self.color_index = (self.color_index + 1) % len(self.colors)
            self.target_color = self.colors[self.color_index]
        
        r = int(self.current_color[0] + (self.target_color[0] - self.current_color[0]) * self.color_transition)
        g = int(self.current_color[1] + (self.target_color[1] - self.current_color[1]) * self.color_transition)
        b = int(self.current_color[2] + (self.target_color[2] - self.current_color[2]) * self.color_transition)
        self.interpolated_color = (r, g, b)

    def should_leave_trail(self):
        return not self.has_reached_max_size() and is_inside_big_circle(self.position[0], self.position[1], self.radius, VISUAL_MARGIN)
    
    def has_reached_max_size(self):
        return self.actual_size >= self.max_radius * 0.995
    
def draw_quarter_circle(surface, color, center, radius, quadrant, line_width=0, trail=False):
    start_angle = quadrant * math.pi/2
    end_angle = (quadrant + 1) * math.pi/2
    
    points = [center]
    num_points = 60
    for i in range(num_points + 1):
        angle = start_angle + (end_angle - start_angle) * i / num_points
        x = center[0] + int(radius * math.cos(angle))
        y = center[1] + int(radius * math.sin(angle))
        
        dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        if dist > big_ball_radius:
            ratio = (big_ball_radius + 0.5) / dist 
            x = center_x + (x - center_x) * ratio
            y = center_y + (y - center_y) * ratio
        
        
        points.append((int(x), int(y)))
    
    if len(points) > 2:
        pygame.draw.polygon(surface, color, points)
        
        if trail:
            border_color = (0, 0, 0, 80)  
            
            def draw_ultra_thin_line(start, end):
                x1, y1 = start
                x2, y2 = end
                dx = x2 - x1
                dy = y2 - y1
                steps = max(abs(dx), abs(dy))
                if steps == 0:
                    return
                
                x_step = dx / steps
                y_step = dy / steps
                
                for i in range(int(steps)):
                    if random.random() < 0.5:  
                        x = int(x1 + i * x_step)
                        y = int(y1 + i * y_step)
                        pygame.gfxdraw.pixel(surface, x, y, border_color)
            
            for i in range(len(points) - 1):
                draw_ultra_thin_line(points[i], points[i+1])
            
            draw_ultra_thin_line(points[-1], center)
        else:
            border_color = WHITE
            border_color_alpha = border_color + (64,)
            
            for i in range(1, len(points)):
                pygame.gfxdraw.pixel(surface, int(points[i][0]), int(points[i][1]), border_color_alpha)
            
            def draw_line(start, end):
                x1, y1 = start
                x2, y2 = end
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                sx = 1 if x1 < x2 else -1
                sy = 1 if y1 < y2 else -1
                err = dx - dy
                
                while True:
                    pygame.gfxdraw.pixel(surface, int(x1), int(y1), border_color_alpha)
                    if x1 == x2 and y1 == y2:
                        break
                    e2 = 2 * err
                    if e2 > -dy:
                        err -= dy
                        x1 += sx
                    if e2 < dx:
                        err += dx
                        y1 += sy
            
            draw_line(center, points[1])
            draw_line(center, points[-1])
def draw_big_circle(surface):
    pygame.draw.circle(surface, WHITE, (center_x, center_y), big_ball_radius + 1, BIG_CIRCLE_BORDER_WIDTH)
    pygame.draw.circle(surface, BLACK, (center_x, center_y), big_ball_radius - BIG_CIRCLE_BORDER_WIDTH // 2)

def draw_static_circle(surface, center, radius):
    pygame.draw.circle(surface, BLACK, center, radius)

def render_text(surface, text, position, font_size=20, color=WHITE, bg_color=BLACK):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(bottomright=position)
    pygame.draw.rect(surface, bg_color, text_rect.inflate(10, 10))
    surface.blit(text_surface, text_rect)

quarters = [
    QuarterCircle(0, is_main=True),
    QuarterCircle(1),
    QuarterCircle(2),
    QuarterCircle(3)
]

clock = pygame.time.Clock()

permanent_trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

frame_count = 0
max_frames = 60 * 60  

all_quarters_max_size = False

segmento_actual = 0
clock = pygame.time.Clock()

# Justo antes de tu bucle principal, añade:
tiempo_inicio = pygame.time.get_ticks() / 1000.0


while frame_count < max_frames:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            frame_count = max_frames 
    
    
    # Aquí va el código para sincronizar los sonidos
    tiempo_actual = pygame.time.get_ticks() / 1000.0 - tiempo_inicio + tiempo_inicio_cancion
    if segmento_actual < len(beat_times) and tiempo_actual >= beat_times[segmento_actual]:
        main_quarter.play_sonido_apofenia()
        segmento_actual += 1
 

    screen.fill(BLACK)
    pygame.draw.circle(screen, WHITE, (center_x, center_y), big_ball_radius + BIG_CIRCLE_BORDER_WIDTH // 2, BIG_CIRCLE_BORDER_WIDTH)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), big_ball_radius)
    
    draw_static_circle(screen, (center_x, center_y), STATIC_CIRCLE_RADIUS)

    if not all_quarters_max_size:
        all_quarters_max_size = all(quarter.has_reached_max_size() for quarter in quarters)
        if all_quarters_max_size:
            permanent_trail_surface.fill((0, 0, 0, 0))
    
    # En el bucle principal, donde calculas tiempo_actual
    
    main_quarter = quarters[0]
    main_quarter.move()
    main_quarter.update_color()
    
    for quarter in quarters:
        if quarter.state in ["max_size", "shrinking"]:
            quarter.actual_size = main_quarter.actual_size
            quarter.radius = quarter.actual_size
            quarter.state = main_quarter.state
            quarter.max_size_timer = main_quarter.max_size_timer

    for quarter in quarters[1:]:
        quarter.mirror_position(main_quarter)
        quarter.update_color()
        quarter.trail.append(quarter.get_position())
        if len(quarter.trail) > quarter.trail_length:
            quarter.trail.pop(0)

    if not all_quarters_max_size and main_quarter.state != "max_size":
        for quarter in quarters:
            if quarter.should_leave_trail():
                for pos in quarter.trail:
                    if is_inside_big_circle(pos[0], pos[1], quarter.radius, VISUAL_MARGIN):
                        color_with_alpha = quarter.interpolated_color + (180,)
                        draw_quarter_circle(permanent_trail_surface, color_with_alpha, pos, quarter.radius, quarter.quadrant, trail=True)

    screen.blit(permanent_trail_surface, (0, 0))

    for quarter in quarters:
        position = quarter.get_position() if quarter.state != "max_size" else (center_x, center_y)
        draw_quarter_circle(screen, quarter.interpolated_color, position, quarter.radius, quarter.quadrant)

    size_text = f"Size: {main_quarter.actual_size:.1f} | Collisions: {main_quarter.collision_count}"
    render_text(screen, size_text, (width - 10, height - 10), font_size=24)

    pygame.display.flip()
    
    frame = pygame.surfarray.array3d(screen)
    frame = frame.transpose([1, 0, 2])
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video.write(frame)
    
    clock.tick(90)
    frame_count += 1

video.release()


def combinar_video_audio(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Recorta el audio para que coincida con la duración del video si es necesario
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)
    
    video_final = video.set_audio(audio)
    video_final.write_videofile(output_path, codec='libx264', audio_codec='aac')

# Después de tu bucle principal y de cerrar el video
video.release()

video_sin_audio = 'output.mp4'
audio_file = r"D:\Plantillas personalizadas de Office\UpWork\Tiktok_Animation\Post_Malone_Swae_Lee_-_Sunflower_Spider-Man_Into_the_Spider-Verse_[_YouConvert.net_].mp3"
video_con_audio = 'output_con_audio.mp4'

try:
    combinar_video_audio(video_sin_audio, audio_file, video_con_audio)
    print("Video y audio combinados exitosamente.")
except Exception as e:
    print(f"Error al combinar video y audio: {e}")

pygame.quit()
cv2.destroyAllWindows()

