# catch_the_objects_pygame.py
# Pygame reimplementation of the Turtle "Catch the objects" game
# Team ID: [13] - converted to pygame by ChatGPT

import pygame
import random
import math
import os
import sys

# -------- CONFIG ----------
SCREEN_W, SCREEN_H = 800, 800
FPS = 60

PLAYER_SPEED = 6
FALL_SPEED_CHOICES = [2, 3, 4, 5, 6, 7, 8]  # speeds used for falling objects
ANIMALS_COUNT = 10    # 5 tigers + 5 lions
ESSENTIALS_COUNT = 10 # 5 rocks + 5 logs
# collision radii approximating turtle.distance checks
ANIMAL_COLLIDE_RADIUS = 40
ESSENTIAL_COLLIDE_RADIUS = 40
DROPLET_COLLIDE_RADIUS = 20

# --------- HELPERS ----------
def load_image(name, colorkey=None):
    path = os.path.join(os.path.dirname(__file__), name)
    try:
        image = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Unable to load image '{name}'. Make sure the file exists in the script folder.")
        raise e
    return image

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# --------- SPRITES ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, img_right, img_left):
        super().__init__()
        self.img_right = img_right
        self.img_left = img_left
        self.image = self.img_right
        self.rect = self.image.get_rect(center=(SCREEN_W // 2, SCREEN_H - 100))
        self.pos = pygame.Vector2(self.rect.center)
    def update(self, keys):
        if keys[pygame.K_RIGHT]:
            self.image = self.img_right
            self.pos.x += PLAYER_SPEED
        elif keys[pygame.K_LEFT]:
            self.image = self.img_left
            self.pos.x -= PLAYER_SPEED
        # clamp inside horizontal boundaries (-300..300 in turtle world maps to screen)
        min_x = 50
        max_x = SCREEN_W - 50
        self.pos.x = max(min_x, min(max_x, self.pos.x))
        self.rect.centerx = int(self.pos.x)
    def center_pos(self):
        return (self.rect.centerx, self.rect.centery)

class FallingObject(pygame.sprite.Sprite):
    def __init__(self, image, kind):
        super().__init__()
        self.original = image
        self.image = image
        self.rect = self.image.get_rect()
        self.kind = kind  # 'animal', 'essential', 'droplet'
        self.reset_position()
    def reset_position(self):
        self.rect.x = random.randint(50, SCREEN_W - 50)
        self.rect.y = random.randint(-SCREEN_H//2, -20)
        self.speed = random.choice(FALL_SPEED_CHOICES)
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 50:
            self.reset_position()

# ---------- MAIN GAME ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Catch the objects - Pygame")
    clock = pygame.time.Clock()

    # Load images (ensure these names exist or change to your filenames)
    try:
        bg = load_image("forest.png")
        man_r = load_image("man_right(1).png")
        man_l = load_image("man_left(1).png")
        tiger_img = load_image("tiger(1).png")
        lion_img  = load_image("lion(1).png")
        rock_img  = load_image("rock(1).gif")
        log_img   = load_image("log(1).gif")
        drop_img  = load_image("drop(1).png")
        # optional: fire_img = load_image("fire.gif")
    except Exception as e:
        print("Missing images or load error. Exiting.")
        pygame.quit()
        sys.exit()

    # Scale or adjust images if too large
    def fit(img, maxw, maxh):
        w,h = img.get_size()
        scale = min(maxw/w, maxh/h, 1.0)
        if scale < 1.0:
            return pygame.transform.smoothscale(img, (int(w*scale), int(h*scale)))
        return img

    man_r = fit(man_r, 100, 120)
    man_l = fit(man_l, 100, 120)
    tiger_img = fit(tiger_img, 70, 70)
    lion_img = fit(lion_img, 70, 70)
    rock_img = fit(rock_img, 50, 50)
    log_img = fit(log_img, 60, 40)
    drop_img = fit(drop_img, 35, 35)
    bg = pygame.transform.smoothscale(bg, (SCREEN_W, SCREEN_H))

    # Create player
    player = Player(man_r, man_l)
    player_group = pygame.sprite.GroupSingle(player)

    # Create falling animals
    animals_group = pygame.sprite.Group()
    # add 5 tigers, 5 lions
    for _ in range(5):
        a = FallingObject(tiger_img, "animal_tiger")
        animals_group.add(a)
    for _ in range(5):
        a = FallingObject(lion_img, "animal_lion")
        animals_group.add(a)

    # Create essentials (rocks and logs)
    essentials_group = pygame.sprite.Group()
    for _ in range(5):
        e = FallingObject(rock_img, "essential_rock")
        essentials_group.add(e)
    for _ in range(5):
        e = FallingObject(log_img, "essential_log")
        essentials_group.add(e)

    # Droplet (single)
    droplet = FallingObject(drop_img, "droplet")
    droplet_group = pygame.sprite.GroupSingle(droplet)

    # Game variables
    lives = 3
    score = 0
    flameFlag = 0  # same semantics as original: if 1 animals don't reduce lives (kept for parity)

    # Font
    font = pygame.font.SysFont("Arial", 24)

    running = True
    game_over = False

    # initial write like the turtle code shows
    title_surf = font.render("Catch the objects !!!", True, (0,0,0))
    title_pos = (20, 10)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            keys = pygame.key.get_pressed()
            player_group.update(keys)
            animals_group.update()
            essentials_group.update()
            droplet_group.update()

            # collision checks: animals
            for animal in animals_group.sprites():
                # compute distance to player center
                if dist(animal.rect.center, player.center_pos()) < ANIMAL_COLLIDE_RADIUS:
                    # hit: reset animal and update score/lives like turtle code
                    animal.reset_position()
                    score -= 10
                    if flameFlag == 0:
                        lives -= 1
                    # else lives unchanged
                    # Update display happens by loop

            # essentials collisions (+10)
            for essential in essentials_group.sprites():
                if dist(essential.rect.center, player.center_pos()) < ESSENTIAL_COLLIDE_RADIUS:
                    essential.reset_position()
                    score += 10

            # droplet collision (+1 life)
            d = droplet_group.sprite
            if d and dist(d.rect.center, player.center_pos()) < DROPLET_COLLIDE_RADIUS:
                # hide droplet and move it far away (mimic droplet.ht() & goto(500,600))
                d.rect.topleft = (SCREEN_W + 200, -200)
                lives += 1

            # keep player inside horizontal bounds - already clamped in Player.update

            if lives <= 0:
                game_over = True

        # DRAW
        screen.blit(bg, (0,0))
        screen.blit(title_surf, title_pos)

        animals_group.draw(screen)
        essentials_group.draw(screen)
        droplet_group.draw(screen)
        player_group.draw(screen)

        # HUD
        hud = font.render(f"Score: {score}     Lives: {lives}", True, (10,10,10))
        screen.blit(hud, (10, SCREEN_H - 40))

        if game_over:
            go_font = pygame.font.SysFont("Arial", 48)
            go_surf = go_font.render("Game Over!!!", True, (200,0,0))
            sc_surf = font.render(f"Final Score: {score}", True, (0,0,0))
            screen.blit(go_surf, (SCREEN_W//2 - go_surf.get_width()//2, SCREEN_H//2 - 50))
            screen.blit(sc_surf, (SCREEN_W//2 - sc_surf.get_width()//2, SCREEN_H//2 + 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
