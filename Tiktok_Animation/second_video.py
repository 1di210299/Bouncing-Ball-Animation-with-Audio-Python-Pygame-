import pygame
import math
import re
import random
from pygame.locals import K_f  # Import constant for 'f' key

# Code by Matt Connected
# Keep to yourself


# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(300)

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in a Circle with Sound")

# Circle properties
circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 200

# Ball properties
ball_radius = 40
ball_pos = [WIDTH // 2 + (random.randint(150,160)), HEIGHT // 2 + 160 - circle_radius + ball_radius]
ball_velocity = [0, 2]  # Starting velocity
gravity = 0.1
bounce_increase_factor = 1.00  # Increase ball size by 3% on each bounce
speed_increase_factor = 1.01
max_ball_radius = 999  # Maximum size of the ball
ball_color = [255, 0, 0]  # Start with red

circle_border_thickness = 0  # Adjust the thickness as needed

# Color change speed
color_change_speed = 1





# Stamping properties
stamp_positions = []  # List to store ball positions for stamping
frame_counter = 0  # Frame counter
stamp_interval = 2  # Interval at which to stamp the ball


max_speed_x = 10  # Maximum horizontal speed
max_speed_y = 9  # Maximum vertical speed

# Function to limit the speed
def limit_speed(velocity, max_speed):
    if velocity > max_speed:
        return max_speed
    elif velocity < -max_speed:
        return -max_speed
    return velocity

# Function to cycle through rainbow colors
def cycle_color(color, speed):
    if color[0] == 255 and color[1] < 255 and color[2] == 0:
        color[1] += speed
    elif color[1] == 255 and color[0] > 0 and color[2] == 0:
        color[0] -= speed
    elif color[1] == 255 and color[2] < 255 and color[0] == 0:
        color[2] += speed
    elif color[2] == 255 and color[1] > 0 and color[0] == 0:
        color[1] -= speed
    elif color[2] == 255 and color[0] < 255 and color[1] == 0:
        color[0] += speed
    elif color[0] == 255 and color[2] > 0 and color[1] == 0:
        color[2] -= speed
    for i in range(3):
        color[i] = min(max(color[i], 0), 255)
    return color


# Function to calculate reflection angle
def reflect(ball_pos, circle_center, ball_velocity):
    # Calculate normal vector at the collision point
    dx, dy = ball_pos[0] - circle_center[0], ball_pos[1] - circle_center[1]
    normal = [dx, dy]
    normal_length = math.sqrt(normal[0]**2 + normal[1]**2)

    # Normalize the normal vector
    normal = [normal[0] / normal_length, normal[1] / normal_length]

    # Reflect the velocity vector
    dot_product = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1]
    ball_velocity[0] -= 2 * dot_product * normal[0]
    ball_velocity[1] -= 2 * dot_product * normal[1]

    return ball_velocity

def adjust_ball_position(ball_pos, circle_center, ball_radius, circle_radius):
    # Adjust the ball position to stay inside the circle
    direction_vector = [ball_pos[0] - circle_center[0], ball_pos[1] - circle_center[1]]
    direction_magnitude = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
    normalized_direction = [direction_vector[0] / direction_magnitude, direction_vector[1] / direction_magnitude]
    adjusted_position = [circle_center[0] + normalized_direction[0] * (circle_radius - ball_radius),
                         circle_center[1] + normalized_direction[1] * (circle_radius - ball_radius)]
    return adjusted_position

def display_text(text, position, font_name='Arial', font_size=36, color=(128, 128, 128), bold=False, italic=False):
    font = pygame.font.SysFont(font_name, font_size, bold, italic)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)
running = True
clock = pygame.time.Clock()


full_song = pygame.mixer.Sound(r"")
songPlaying = False
song_timer = 0
SONG_RESET_TIME = 350
last_print_time = 0


ball_image = pygame.image.load("Foto.jpeg").convert_alpha()
ball_image_width = 80
ball_image_height = 90
ball_image = pygame.transform.scale(ball_image, (ball_image_width, ball_image_height))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == K_f:  # Check if 'F' key is pressed
                # Give the ball a random velocity to the right
                ball_velocity[0] += random.uniform(0.5, 2)
    current_time = pygame.time.get_ticks()
    # Update ball position
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]

    # Apply gravity
    ball_velocity[1] += gravity

    # Check for collision with the circle
    distance = math.sqrt((ball_pos[0] - circle_center[0])**2 + (ball_pos[1] - circle_center[1])**2)
    if distance > circle_radius - ball_radius:
        ball_velocity = reflect(ball_pos, circle_center, ball_velocity)

        # Increase speed after bounce
        ball_velocity[0] *= speed_increase_factor
        ball_velocity[1] *= speed_increase_factor
        ball_velocity[0] = limit_speed(ball_velocity[0], max_speed_x)
        ball_velocity[1] = limit_speed(ball_velocity[1], max_speed_y)
     #   print(ball_velocity[0])
     #   print(ball_velocity[1])

        ball_pos = adjust_ball_position(ball_pos, circle_center, ball_radius, circle_radius)
        if ball_radius < max_ball_radius:
            ball_radius *= bounce_increase_factor

        if not songPlaying:
            full_song.play(-1)  # Start the song
            songPlaying = True
        song_timer = current_time


    if songPlaying and current_time - song_timer > SONG_RESET_TIME:
        full_song.stop()  # Stop the song
        songPlaying = False

    ball_radius += 0.005

   # ball_image_width += 0.15
   # ball_image_height += 1.35
    ball_image_size = (ball_image_width * ball_radius/40, ball_image_height * ball_radius/40)
    ball_image = pygame.transform.scale(ball_image, ball_image_size)

    # Increment frame counter and check for stamping
    frame_counter += 1
    if frame_counter == stamp_interval:
        stamp_positions.append((int(ball_pos[0]), int(ball_pos[1]), int(ball_radius), ball_color.copy()))
        frame_counter = 0

    # Cycle ball color
    ball_color = cycle_color(ball_color, color_change_speed)

    # Clear screen
    if songPlaying:
        screen.fill((150,30,30))
    else:
        screen.fill((0, 0, 0))


    # Draw circle
    #pygame.draw.circle(screen, (255, 255, 255), circle_center, circle_radius, 1)

    #the border circle
    pygame.draw.circle(screen, (255,255,255), circle_center, circle_radius)
    #extra border to make it look smooth
    if songPlaying:
        pygame.draw.circle(screen, (150,30,30), circle_center, circle_radius, 5)
    else:
        pygame.draw.circle(screen, (0,0,0), circle_center, circle_radius, 5)

    # Draw stamps with white outline
    for x, y, r, color in stamp_positions:
       # pygame.draw.circle(screen, (255, 255, 255), (x, y), r + 2)  # White outline
        if songPlaying:
            pygame.draw.circle(screen, (150,30,30), (x, y), r)  # Ball stamp
        else:
            pygame.draw.circle(screen, (0,0,0), (x, y), r)  # Ball stamp

    # Draw ball with white outline
    pygame.draw.circle(screen, (255, 255, 255), (int(ball_pos[0]), int(ball_pos[1])), int(ball_radius) + 2)
    pygame.draw.circle(screen, (0,0,0), (int(ball_pos[0]), int(ball_pos[1])), int(ball_radius))

    image_x = int(ball_pos[0] - ball_image_size[0] / 2)
    image_y = int(ball_pos[1] - ball_image_size[1] / 2)
    screen.blit(ball_image, (image_x, image_y))




    # Update the display

    if current_time - last_print_time >= 1000:
            last_print_time = current_time
            seconds = current_time // 1000
            print(f"T:{seconds}")

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(120)

pygame.quit()