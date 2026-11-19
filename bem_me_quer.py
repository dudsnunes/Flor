"""
Bem me quer, Mal me quer - pixel art en pygame.
Installation : pip install pygame
Contrôles : clic / Espace = arracher un pétale, R = recommencer, Échap = quitter
"""
import math
import random
import sys
import pygame

W, H, SCALE = 180, 240, 3  # résolution interne (pixel art) et zoom
N_PETALS = 12
CX, CY = 90, 108  # centre de la fleur
STEM_BOTTOM = (90, 208)
LOVES_COLOR = (255, 143, 192)  # #ff8fc0
NOT_COLOR = (169, 188, 255)    # #a9bcff
IDLE_COLOR = (192, 224, 36)

pygame.init()
info = pygame.display.Info()
start_scale = max(1, int(min(info.current_w * 0.8 // W, info.current_h * 0.8 // H)))
screen = pygame.display.set_mode((W * start_scale, H * start_scale), pygame.RESIZABLE)
pygame.display.set_caption("Bem me quer, mal me quer")
buf = pygame.Surface((W, H))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas,couriernew,monospace", 18, bold=True)

# ---------- décor statique ----------
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make_background():
    bg = pygame.Surface((W, H))
    top, bottom = (8, 12, 58), (110, 70, 150)
    bands = 7
    for y in range(H):
        t = min(1.0, y / (H * 0.8))
        v = t * bands
        i = int(v)
        frac = v - i
        for x in range(W):
            k = i + (1 if frac > BAYER[y % 4][x % 4] / 16 else 0)
            bg.set_at((x, y), lerp(top, bottom, min(k, bands) / bands))
    # collines
    for x in range(W):
        y1 = int(172 + 9 * math.sin(x * 0.035) + 5 * math.sin(x * 0.09 + 1))
        pygame.draw.line(bg, (28, 38, 110), (x, y1), (x, H))
        y2 = int(190 + 4 * math.sin(x * 0.06 + 2))
        pygame.draw.line(bg, (20, 70, 50), (x, y2), (x, H))
    # sol
    pygame.draw.rect(bg, (30, 90, 40), (0, 200, W, H - 200))
    return bg

random.seed(4)
BG = make_background()
STARS = [
    (random.randint(2, W - 2), random.randint(2, 120), random.random() * 6.28)
    for _ in range(45)
]
GRASS = [
    (
        random.randint(0, W),
        random.randint(194, 232),
        random.randint(3, 9),
        random.choice([(60, 150, 60), (40, 120, 50), (90, 180, 70)]),
    )
    for _ in range(40)  # exemplo de fechamento da lista
]

# ---------- logique du jeu ----------
def reset_game():
    count = random.choice([N_PETALS - 1, N_PETALS, N_PETALS + 1])
    petals = []
    for i in range(count):
        angle = (2 * math.pi * i) / count - math.pi / 2
        petals.append({"angle": angle, "falling": False, "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0})
    return petals, 0

petals, pulled = reset_game()

def draw_petal(surf, angle, ox=0, oy=0, alpha=255):
    px = CX + ox + math.cos(angle) * 20
    py = CY + oy + math.sin(angle) * 20
    petal_surf = pygame.Surface((26, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(petal_surf, (235, 240, 255, alpha), (0, 0, 26, 14))
    pygame.draw.ellipse(petal_surf, (255, 255, 255, alpha), (2, 2, 20, 9))
    rot = pygame.transform.rotate(petal_surf, -math.degrees(angle))
    rect = rot.get_rect(center=(int(px), int(py)))
    surf.blit(rot, rect)

def draw_text(surf, text, color, y):
    shadow = font.render(text, False, (15, 15, 35))
    img = font.render(text, False, color)
    x = (W - img.get_width()) // 2
    surf.blit(shadow, (x + 1, y + 1))
    surf.blit(img, (x, y))

# ---------- boucle principale ----------
while True:
    dt = clock.tick(60) / 1000.0
    t = pygame.time.get_ticks() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_r:
                petals, pulled = reset_game()
            elif event.key == pygame.K_SPACE:
                for p in petals:
                    if not p["falling"]:
                        p["falling"] = True
                        p["vx"] = random.uniform(-18, 18)
                        p["vy"] = random.uniform(-15, 5)
                        pulled += 1
                        break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for p in petals:
                if not p["falling"]:
                    p["falling"] = True
                    p["vx"] = random.uniform(-18, 18)
                    p["vy"] = random.uniform(-15, 5)
                    pulled += 1
                    break

    buf.blit(BG, (0, 0))

    # estrelas piscando
    for sx, sy, phase in STARS:
        c = 180 + int(75 * math.sin(t * 3 + phase))
        buf.set_at((sx, sy), (c, c, 255))

    # grama
    for gx, gy, gh, gcol in GRASS:
        sway = int(math.sin(t * 2 + gx * 0.1) * 1.5)
        pygame.draw.line(buf, gcol, (gx, gy), (gx + sway, gy - gh))

    # caule e folhas
    pygame.draw.line(buf, (50, 140, 60), (CX, CY), STEM_BOTTOM, 3)
    pygame.draw.ellipse(buf, (60, 160, 70), (CX - 18, CY + 45, 18, 9))
    pygame.draw.ellipse(buf, (60, 160, 70), (CX, CY + 55, 18, 9))

    # pétalas presas
    for p in petals:
        if not p["falling"]:
            draw_petal(buf, p["angle"])

    # miolo da flor
    pygame.draw.circle(buf, (210, 130, 20), (CX, CY), 12)
    pygame.draw.circle(buf, (255, 200, 40), (CX - 1, CY - 1), 10)

    # pétalas caindo
    for p in petals:
        if p["falling"] and p["y"] < H:
            p["x"] += p["vx"] * dt
            p["vy"] += 45 * dt
            p["y"] += p["vy"] * dt
            p["angle"] += 1.5 * dt
            draw_petal(buf, p["angle"], p["x"], p["y"])

    # texto na tela
    if pulled == 0:
        draw_text(buf, "Clique!", IDLE_COLOR, 18)
    elif pulled % 2 == 1:
        draw_text(buf, "Bem me quer", LOVES_COLOR, 18)
    else:
        draw_text(buf, "Mal me quer", NOT_COLOR, 18)

    # escala para a janela
    win_w, win_h = screen.get_size()
    scaled = pygame.transform.scale(buf, (win_w, win_h))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()
