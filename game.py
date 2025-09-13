# -*- coding: utf-8 -*-
# わり算シューティング（Web対応版）

import pygame
import random
import math

# ------------------ 基本設定 ------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
TITLE = "わり算シューティング"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# フォント（Web対応：環境依存フォントを避ける）
def load_font(size):
    return pygame.font.SysFont(None, size)

FONT_S = load_font(22)
FONT_M = load_font(32)
FONT_L = load_font(52)

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (120, 120, 120)
LIGHTGRAY = (180, 180, 180)
RED   = (240, 60, 60)
GREEN = (60, 220, 120)
BLUE  = (60, 140, 255)
YELLOW= (255, 220, 50)
ORANGE= (255, 150, 60)
PURPLE= (190, 80, 255)

# ------------------------------------------------
# WIDTH, HEIGHT = 900, 600
FPS = 60
TITLE = "わり算シューティング"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# フォント
def load_font(size):
    try:
        return pygame.font.Font("meiryo", size)  # OS依存の既定フォント
    except:
        return pygame.font.SysFont("meiryo", size)
FONT_S = load_font(22)
FONT_M = load_font(32)
FONT_L = load_font(52)

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (120, 120, 120)
LIGHTGRAY = (180, 180, 180)
RED   = (240, 60, 60)
GREEN = (60, 220, 120)
BLUE  = (60, 140, 255)
YELLOW= (255, 220, 50)
ORANGE= (255, 150, 60)
PURPLE= (190, 80, 255)

# ------------------ ユーティリティ ------------------
def blit_text_center(surface, text, font, color, center):
    img = font.render(text, True, color)
    rect = img.get_rect(center=center)
    surface.blit(img, rect)
    return rect

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ------------------ 背景（星空） ------------------
class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randrange(0, WIDTH)
        self.y = random.randrange(-HEIGHT, HEIGHT)
        self.speed = random.uniform(0.5, 2.5)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.x = random.randrange(0, WIDTH)
            self.y = random.randrange(-100, 0)
            self.speed = random.uniform(0.5, 2.5)
            self.size = random.randint(1, 3)

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(150)]

# ------------------ プレイヤー/弾 ------------------
class Player:
    def __init__(self):
        self.w = 70
        self.h = 16
        self.y = HEIGHT - 50
        self.x = WIDTH // 2
        self.color = BLUE
        self.cooldown = 0  # 連射制限

    def update(self, mouse_x):
        self.x = clamp(mouse_x, self.w // 2, WIDTH - self.w // 2)
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surf):
        rect = pygame.Rect(0, 0, self.w, self.h)
        rect.center = (self.x, self.y)
        pygame.draw.rect(surf, self.color, rect, border_radius=8)
        # 小さなコックピット風
        pygame.draw.rect(surf, LIGHTGRAY, (self.x - 8, self.y - 10, 16, 10), border_radius=4)

    def can_shoot(self):
        return self.cooldown == 0

    def shoot(self):
        self.cooldown = 10  # クールダウン
        return Bullet(self.x, self.y - self.h // 2)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = -10
        self.r = 4

    def update(self):
        self.y += self.speed

    def offscreen(self):
        return self.y < -10

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.r)

# ------------------ 隕石（選択肢） ------------------
class Meteor:
    def __init__(self, x, value, speed):
        self.x = x
        self.y = -40
        self.value = value
        self.speed = speed
        self.r = 28
        self.alive = True
        self.fade = 255  # フェードアウト

    def update(self):
        if self.alive:
            self.y += self.speed
        else:
            self.fade -= 15
            if self.fade < 0:
                self.fade = 0

    def draw(self, surf):
        alpha = clamp(self.fade, 0, 255)
        color = (min(200, 120 + self.value * 10), 100, 100)  # ほんのり色変化
        # フェード用サーフェス
        temp = pygame.Surface((self.r * 2 + 4, self.r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(temp, (*color, alpha), (self.r + 2, self.r + 2), self.r)
        surf.blit(temp, (int(self.x - self.r - 2), int(self.y - self.r - 2)))
        # 数字
        if alpha > 40:
            blit_text_center(surf, str(self.value), FONT_M, WHITE, (int(self.x), int(self.y)))

    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r * 2, self.r * 2)

    def offscreen(self):
        return self.y - self.r > HEIGHT

# ------------------ パーティクル（爆発/お祝い） ------------------
class Particle:
    def __init__(self, x, y, color=ORANGE, power=4):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, power)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.x = x
        self.y = y
        self.life = random.randint(18, 32)
        self.color = color
        self.r = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 重力
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.r)

# ------------------ 問題生成 ------------------
DIFFICULTIES = [
    {
        "name": "初級",
        "max_dividend": 20,
        "divisors": list(range(1, 6)),   # 1~5段
        "fall_speed": (2.4, 3.4)
    },
    {
        "name": "中級",
        "max_dividend": 60,
        "divisors": list(range(6, 10)),  # 6~9段
        "fall_speed": (3.0, 4.2)
    },
    {
        "name": "上級",
        "max_dividend": 81,
        "divisors": list(range(1, 10)),  # すべて
        "fall_speed": (3.6, 5.0)
    },
]

def make_problem(level_cfg):
    # divisor は指定の段から選ぶ
    d = random.choice(level_cfg["divisors"])
    # 商は1~9に限定。ただしmax_dividendを超えないよう上限調整
    q_max = min(9, level_cfg["max_dividend"] // d)
    if q_max < 1:
        # 万が一成立しない場合は再帰
        return make_problem(level_cfg)
    q = random.randint(1, q_max)
    a = d * q  # わられる数(被除数)
    # 4択の選択肢を作る（重複なし、1つ正解）
    choices = {q}
    while len(choices) < 4:
        # 正解近傍を中心に作る（1~9の範囲）
        delta = random.choice([-3, -2, -1, 1, 2, 3])
        cand = clamp(q + delta + random.randint(-1, 1), 1, 9)
        choices.add(cand)
    choices = list(choices)
    random.shuffle(choices)
    return a, d, q, choices

# ------------------ ゲーム状態 ------------------
STATE_MENU = 0
STATE_PLAY  = 1
STATE_LEVEL_CLEAR = 2
STATE_GAME_CLEAR  = 3

class Game:
    def __init__(self):
        self.state = STATE_MENU
        self.level_index = 0
        self.reset_for_level()

    def reset_for_level(self):
        self.player = Player()
        self.bullets = []
        self.meteors = []
        self.particles = []
        self.score = 0
        self.correct_count = 0
        self.question_ready = False
        self.problem = None  # (a, d, q, choices)
        self.target_value = None
        self.progress_total = 10  # 10問でクリア
        self.message_timer = 0

    def spawn_question(self):
        cfg = DIFFICULTIES[self.level_index]
        a, d, q, choices = make_problem(cfg)
        self.problem = (a, d, q, choices)
        self.target_value = q
        # 4 つの隕石を横方向に配置して落下
        columns = [WIDTH * x / 5 for x in (1, 2, 3, 4)]
        random.shuffle(columns)
        self.meteors = []
        for i, val in enumerate(choices):
            speed = random.uniform(*cfg["fall_speed"])
            self.meteors.append(Meteor(columns[i], val, speed))
        self.question_ready = True

    def update(self):
        # 背景
        for s in stars:
            s.update()

        if self.state == STATE_MENU:
            return

        # プレイヤー & 弾
        mx, my = pygame.mouse.get_pos()
        self.player.update(mx)
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if not b.offscreen()]

        # パーティクル
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # プレイ中の進行
        if self.state == STATE_PLAY:
            if not self.question_ready:
                self.spawn_question()

            # 隕石更新
            for m in self.meteors:
                m.update()

            # 衝突判定（弾 vs 隕石）
            for b in list(self.bullets):
                for m in self.meteors:
                    if m.alive and m.rect().collidepoint(b.x, b.y):
                        # 爆発パーティクル
                        for _ in range(24):
                            self.particles.append(Particle(m.x, m.y, ORANGE, power=6))
                        m.alive = False
                        # 弾は消える
                        if b in self.bullets:
                            self.bullets.remove(b)
                        # 正解判定
                        if m.value == self.target_value:
                            self.score += 10
                            self.correct_count += 1
                            # 他の隕石はフェードアウト
                            for other in self.meteors:
                                if other is not m:
                                    other.alive = False
                            self.message_timer = 30
                            # 次の問題へ
                            self.question_ready = False
                            # 進捗達成でレベルクリア
                            if self.correct_count >= self.progress_total:
                                # お祝いコンフェッティ
                                for _ in range(240):
                                    c = random.choice([YELLOW, GREEN, BLUE, ORANGE, PURPLE, WHITE])
                                    self.particles.append(Particle(WIDTH//2, HEIGHT//3, c, power=8))
                                self.state = STATE_LEVEL_CLEAR
                            break
                        else:
                            # 不正解：見た目だけの×演出（ペナルティ無し）
                            for _ in range(12):
                                self.particles.append(Particle(m.x, m.y, RED, power=5))
                        break

            # 画面下まで落ちたら消す（正解が落ちたら次問題へ）
            removed_any = False
            for m in self.meteors:
                if m.offscreen():
                    m.alive = False
                    removed_any = True
            if removed_any:
                # 正解が未撃破のまま落ちた場合は新しい問題を出す（ペナルティ無しでテンポ重視）
                self.question_ready = False

        elif self.state in (STATE_LEVEL_CLEAR, STATE_GAME_CLEAR):
            pass

    def draw_background(self):
        # 宇宙の演出：縦グラデ（簡易）
        for y in range(0, HEIGHT, 4):
            t = y / HEIGHT
            r = int(10 + 20 * (1 - t))
            g = int(10 + 10 * (1 - t))
            b = int(25 + 100 * t)
            pygame.draw.rect(screen, (r, g, b), (0, y, WIDTH, 4))
        for s in stars:
            s.draw(screen)

    def draw_hud(self):
        # タイトル & 問題表示
        if self.state == STATE_PLAY and self.problem:
            a, d, q, choices = self.problem
            blit_text_center(screen, f"わり算シューティング 〔{DIFFICULTIES[self.level_index]['name']}〕",
                             FONT_M, WHITE, (WIDTH//2, 28))
            blit_text_center(screen, f"{a} ÷ {d} = ？",
                             FONT_L, YELLOW, (WIDTH//2, 80))

            # スコア
            score_img = FONT_M.render(f"得点: {self.score}", True, WHITE)
            screen.blit(score_img, (20, 18))

            # 進捗バー（残り問題数）
            margin = 20
            bar_w = 300
            bar_h = 18
            x = WIDTH - bar_w - margin
            y = 22
            pygame.draw.rect(screen, LIGHTGRAY, (x, y, bar_w, bar_h), border_radius=10)
            ratio = self.correct_count / self.progress_total
            pygame.draw.rect(screen, GREEN, (x, y, int(bar_w * ratio), bar_h), border_radius=10)
            remain = self.progress_total - self.correct_count
            txt = FONT_S.render(f"のこり {remain} 問", True, BLACK)
            screen.blit(txt, (x + 8, y - 2))

            # ヒントメッセージ
            if self.message_timer > 0:
                blit_text_center(screen, "ナイスショット！", FONT_M, GREEN, (WIDTH//2, 130))
                self.message_timer -= 1

    def draw(self):
        self.draw_background()

        if self.state == STATE_MENU:
            blit_text_center(screen, "わり算シューティング", FONT_L, WHITE, (WIDTH//2, HEIGHT//2 - 120))
            blit_text_center(screen, "難易度をえらんでください", FONT_M, WHITE, (WIDTH//2, HEIGHT//2 - 60))

            # 難易度ボタン
            buttons = []
            labels = [cfg["name"] for cfg in DIFFICULTIES]
            for i, label in enumerate(labels):
                rect = pygame.Rect(0, 0, 240, 56)
                rect.center = (WIDTH//2, HEIGHT//2 + i * 80)
                pygame.draw.rect(screen, BLUE if i==0 else (80,80,160) if i==1 else PURPLE, rect, border_radius=16)
                blit_text_center(screen, label, FONT_M, WHITE, rect.center)
                buttons.append((rect, i))

            self.menu_buttons = buttons  # クリック検出用

            # 操作説明
            blit_text_center(
                screen,
                "マウスで移動・クリックでビーム / 正解の隕石を撃とう！",
                FONT_S, LIGHTGRAY, (WIDTH//2, HEIGHT - 40)
            )

        elif self.state == STATE_PLAY:
            self.player.draw(screen)
            for m in self.meteors:
                m.draw(screen)
            for b in self.bullets:
                b.draw(screen)
            for p in self.particles:
                p.draw(screen)
            self.draw_hud()

        elif self.state == STATE_LEVEL_CLEAR:
            blit_text_center(screen, f"{DIFFICULTIES[self.level_index]['name']} クリア！",
                             FONT_L, YELLOW, (WIDTH//2, HEIGHT//2 - 30))
            if self.level_index < len(DIFFICULTIES) - 1:
                blit_text_center(screen, "クリックで次の難易度へ", FONT_M, WHITE, (WIDTH//2, HEIGHT//2 + 30))
            else:
                blit_text_center(screen, "クリックでエンディングへ", FONT_M, WHITE, (WIDTH//2, HEIGHT//2 + 30))
            for p in self.particles:
                p.draw(screen)

        elif self.state == STATE_GAME_CLEAR:
            blit_text_center(screen, "全レベルクリア！おめでとう！", FONT_L, YELLOW, (WIDTH//2, HEIGHT//2 - 20))
            blit_text_center(screen, "クリックで最初にもどる", FONT_M, WHITE, (WIDTH//2, HEIGHT//2 + 40))
            for p in self.particles:
                p.draw(screen)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.state == STATE_MENU:
                # ボタン判定
                pos = e.pos
                for rect, idx in getattr(self, "menu_buttons", []):
                    if rect.collidepoint(pos):
                        self.level_index = idx
                        self.state = STATE_PLAY
                        self.reset_for_level()
                        return
            elif self.state == STATE_PLAY:
                if self.player.can_shoot():
                    self.bullets.append(self.player.shoot())
            elif self.state == STATE_LEVEL_CLEAR:
                # 次へ
                if self.level_index < len(DIFFICULTIES) - 1:
                    self.level_index += 1
                    self.reset_for_level()
                    self.state = STATE_PLAY
                else:
                    self.state = STATE_GAME_CLEAR
            elif self.state == STATE_GAME_CLEAR:
                self.state = STATE_MENU
                self.level_index = 0
                self.reset_for_level()

（ここから下はユーザーさんの元コードをそのまま使えます）
# ------------------------------------------------
# 👆 フォントと終了部分以外は修正不要
# （省略：クラス定義やゲーム処理はそのまま）

# ------------------ メインループ ------------------
def main():
    game = Game()
    running = True

    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            else:
                game.handle_event(e)

        game.update()
        game.draw()
        pygame.display.flip()

    pygame.quit()   # sys.exit() は削除（Webでエラー防止）

if __name__ == "__main__":
    main()
