import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
OUTER_TRIANGLE_SIZE = 400
INNER_TRIANGLE_SIZE = 40
GRAVITY = 0.5
FRAME_RATE = 60
GLOW_DURATION = 20
MAX_SPEED = 15
BOUNCE_DAMPING = 0.8
STEPS_PER_FRAME = 10  # Número de pasos pequeños por frame

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Triángulo pequeño rebotando con gravedad dentro de un triángulo grande")

def create_triangle(x, y, size):
    return [
        (x, y - size // 2),
        (x - size // 2, y + size // 2),
        (x + size // 2, y + size // 2)
    ]

outer_triangle = create_triangle(WIDTH // 2, HEIGHT // 2, OUTER_TRIANGLE_SIZE)
inner_triangle_pos = [WIDTH // 2, HEIGHT // 2 - OUTER_TRIANGLE_SIZE // 4]

def normalize(vector):
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    if length == 0:
        return [0, 0]
    return [vector[0] / length, vector[1] / length]

def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def reflect(velocity, normal):
    dot = dot_product(velocity, normal)
    return [velocity[0] - 2 * dot * normal[0], velocity[1] - 2 * dot * normal[1]]

def point_in_triangle(point, triangle):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    d1 = sign(point, triangle[0], triangle[1])
    d2 = sign(point, triangle[1], triangle[2])
    d3 = sign(point, triangle[2], triangle[0])
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    
    return not (has_neg and has_pos)

def limit_speed(velocity):
    speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
    if speed > MAX_SPEED:
        factor = MAX_SPEED / speed
        return [velocity[0] * factor, velocity[1] * factor]
    return velocity

def get_closest_point_on_edge(point, edge_start, edge_end):
    edge_vector = [edge_end[0] - edge_start[0], edge_end[1] - edge_start[1]]
    point_vector = [point[0] - edge_start[0], point[1] - edge_start[1]]
    
    t = max(0, min(1, dot_product(point_vector, edge_vector) / dot_product(edge_vector, edge_vector)))
    
    return [
        edge_start[0] + t * edge_vector[0],
        edge_start[1] + t * edge_vector[1]
    ]

def main():
    inner_pos = inner_triangle_pos.copy()
    inner_velocity = [0, 0]
    glow_timer = 0
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Dividir la actualización en pasos más pequeños
        for _ in range(STEPS_PER_FRAME):
            # Aplicar gravedad
            inner_velocity[1] += GRAVITY / STEPS_PER_FRAME
            
            # Actualizar posición
            new_pos = [
                inner_pos[0] + inner_velocity[0] / STEPS_PER_FRAME,
                inner_pos[1] + inner_velocity[1] / STEPS_PER_FRAME
            ]
            
            # Verificar colisiones con cada lado del triángulo exterior
            for i in range(3):
                edge_start = outer_triangle[i]
                edge_end = outer_triangle[(i+1)%3]
                edge_vector = [edge_end[0] - edge_start[0], edge_end[1] - edge_start[1]]
                normal = normalize([-edge_vector[1], edge_vector[0]])
                
                # Obtener el punto más cercano en el borde del triángulo exterior
                closest_point = get_closest_point_on_edge(new_pos, edge_start, edge_end)
                
                # Verificar si el nuevo punto está fuera del triángulo grande
                if not point_in_triangle(new_pos, outer_triangle):
                    # Ajustar la posición para que esté dentro del triángulo
                    new_pos = [
                        closest_point[0] + normal[0] * (INNER_TRIANGLE_SIZE / 2),
                        closest_point[1] + normal[1] * (INNER_TRIANGLE_SIZE / 2)
                    ]
                    
                    # Reflexión
                    inner_velocity = reflect(inner_velocity, normal)
                    inner_velocity = [v * BOUNCE_DAMPING for v in inner_velocity]
                    
                    glow_timer = GLOW_DURATION
                    break
            
            inner_pos = new_pos
            inner_velocity = limit_speed(inner_velocity)
        
        inner_triangle = create_triangle(int(inner_pos[0]), int(inner_pos[1]), INNER_TRIANGLE_SIZE)
        
        screen.fill(BLACK)
        
        if glow_timer > 0:
            glow_intensity = int(255 * (glow_timer / GLOW_DURATION))
            glow_color = (glow_intensity, glow_intensity, glow_intensity)
            pygame.draw.polygon(screen, glow_color, outer_triangle, 5)
            glow_timer -= 1
        else:
            pygame.draw.polygon(screen, WHITE, outer_triangle, 5)
        
        pygame.draw.polygon(screen, RED, inner_triangle)
        
        pygame.display.flip()
        
        clock.tick(FRAME_RATE)
    
    pygame.quit()

if __name__ == "__main__":
    main()
