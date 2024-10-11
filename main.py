import pygame, os, time, random

pygame.font.init()

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Invaders 1")

# 画像の読み込み
PLAYER_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ship_player.png")),(50,50))
RED_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ship_red.png")),(50,50))
GREEN_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ship_green.png")),(50,50))
BLUE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ship_blue.png")),(50,50))

LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "laser.png")),(30,30))

# レーザーの型枠（クラス）
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, window):
        window.blit(self.img, (self.x + 10, self.y))
        
    def move(self, vel):
        self.y += vel
        
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)

# 宇宙船の型枠（クラス）
class Ship:
    # 30は0.5秒
    COOLDOWN = 30
    
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WINDOW_HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 20
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # 宇宙船の幅と高さを取得するために使う関数
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WINDOW_HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:  
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SHIP, LASER),
        "green": (GREEN_SHIP, LASER),
        "blue": (BLUE_SHIP, LASER)
    }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
   
    def move(self, vel):
        self.y += vel
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y + 20, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("Avenir", 50)
    lost_font = pygame.font.SysFont("Avenir", 100)
    
    enemies = []
    wave_length = 5
    enemy_vel = 1
    
    player_vel = 5
    laser_vel = 5
    
    player = Player(WINDOW_WIDTH/2 - 25, WINDOW_HEIGHT/1.1 - 25)
    
    clock = pygame.time.Clock()
    
    lost = False
    lost_count = 0
    
    def redraw_window():
        # 背景の塗りつぶし
        WINDOW.fill((30,30,30))
        
        for enemy in enemies:
            enemy.draw(WINDOW)
        
        player.draw(WINDOW)
        
        # テキスト描写
        # f"文字列{変数}"で、変数を取得して文字列の中に入れられる(Python 3.6以降)
        lives_label = main_font.render(f"Lives : {lives}", 1, (255, 200, 200))
        levels_lavel = main_font.render(f"Level : {level}", 1, "white")
        
        # 上で用意したテキストを実際に配置する
        WINDOW.blit(lives_label, (10,10))
        WINDOW.blit(levels_lavel, (WINDOW_WIDTH - levels_lavel.get_width() - 10,10))
        
        if lost:
            lost_label = lost_font.render("Game Over", 1, "white")
            WINDOW.blit(lost_label, (WINDOW_WIDTH/2 - lost_label.get_width()/2, WINDOW_HEIGHT/2 - lost_label.get_height()/2))
        
        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            
        if lost:
            # FPS * 3 は、3秒を意味する
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WINDOW_WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)
        
        for event in pygame.event.get():
            # ✕ボタンを押すとゲーム終了
            if event.type == pygame.QUIT:
                run = False
        # プレイヤー機の移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WINDOW_WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < WINDOW_HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            
        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            
            # ランダムなタイミングで射撃させる
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
        
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > WINDOW_HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                
        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("Avenir", 100)
    run = True
    while run:
        WINDOW.fill((30,30,30))
        title_label = title_font.render("Click to Start", 1, ("white"))
        WINDOW.blit(title_label, (WINDOW_WIDTH/2 - title_label.get_width()/2, WINDOW_HEIGHT/2 - title_label.get_height()/2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # マウスクリックでmainループを呼び出す
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()