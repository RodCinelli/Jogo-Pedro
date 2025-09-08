import arcade
import random
import math
from assets.sprites import (
    make_warrior_textures,
    make_ground_texture,
    make_platform_texture,
    make_slime_textures,
    make_bat_textures,
    make_heart_texture,
    make_chest_texture,
    make_orc_textures,
    make_goblin_textures,
    make_cloud_texture,
    make_sword_fx_texture,
)

# ConfiguraÃ§Ãµes bÃ¡sicas
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Rogue Platformer"

PLAYER_MOVE_SPEED = 4.0
PLAYER_JUMP_SPEED = 12.0
GRAVITY = 0.6

ENEMY_SPEED = 2.0
# Velocidades por tipo (ajustadas)
SLIME_SPEED = 1.4
GOBLIN_SPEED = 2.2
ORC_SPEED = 1.6
BAT_SPEED = GOBLIN_SPEED + 0.4  # morcego um pouco mais rápido que goblin
ATTACK_DURATION = 0.36
ATTACK_HIT_START = 0.12
ATTACK_HIT_END = 0.28
PLAYER_MAX_HP = 5  # em coraÃ§Ãµes, permite meio-coraÃ§Ã£o
PLAYER_INVULN = 1.0
ENEMY_CONTACT_DAMAGE = 1


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color((35, 40, 60))
        # Fullscreen
        self.set_fullscreen(True)

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.pickup_list = arcade.SpriteList()
        self.clouds = arcade.SpriteList()
        self.fx_list = arcade.SpriteList()

        self.player = arcade.Sprite()
        self.physics_engine = None
        self.score = 0
        self.score_text = None
        self.timer_text = None
        self.player_max_hp = PLAYER_MAX_HP
        self.player_hp = float(self.player_max_hp)
        self.player_invuln = 0.0
        self.player_damage = 1
        self.game_over = False
        self.input_name = ""
        self.game_over_title = None
        self.game_over_prompt = None

        self.left_pressed = False
        self.right_pressed = False
        self.facing_right = True

        self.anim_timer = 0.0
        self.anim_index = 0
        self.is_attacking = False
        self.attack_time = 0.0
        self.attack_sprite = arcade.SpriteSolidColor(60, 36, (255, 255, 255, 1))  # hitbox invisÃ­vel
        self.enemies_hit = set()

        self.textures = make_warrior_textures()

        self.setup()

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.pickup_list = arcade.SpriteList()
        self.clouds = arcade.SpriteList()
        self.score = 0
        self.score_text = arcade.Text("Score: 0", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)
        # Timer de 5 minutos
        self.time_limit = 300.0
        self.time_remaining = self.time_limit
        self.timer_text = arcade.Text("Tempo: 05:00", SCREEN_WIDTH - 170, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)
        self.player_hp = float(self.player_max_hp)
        self.player_invuln = 0.0
        self.player_damage = 1
        self.super_sword = False
        self.banner_timer = 0.0
        self.banner_text = ""
        self.game_over = False
        self.input_name = ""
        self.game_over_title = None
        self.game_over_prompt = None

        # ChÃ£o
        ground_tex = make_ground_texture(SCREEN_WIDTH, 40)
        ground = arcade.Sprite()
        ground.texture = ground_tex
        ground.center_x = SCREEN_WIDTH // 2
        ground.center_y = 20
        self.wall_list.append(ground)
        self.ground_top = ground.top

        # Nuvens no ceu (espalhadas uniformemente e mais altas)
        num_cols = 8
        margin_x = 140
        x_step = (SCREEN_WIDTH - 2 * margin_x) / (num_cols - 1)
        # linhas perto do topo da tela
        y_rows = [SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 160, SCREEN_HEIGHT - 240, SCREEN_HEIGHT - 120]
        for i in range(num_cols):
            w = random.randint(120, 240)
            h = random.randint(50, 90)
            cloud = arcade.Sprite()
            cloud.texture = make_cloud_texture(w, h, alpha=random.randint(190, 235))
            # Distribui uniformemente no eixo X e alterna linhas de Y
            jitter = random.randint(-30, 30)
            cloud.center_x = int(margin_x + i * x_step + jitter)
            cloud.center_y = y_rows[i % len(y_rows)] + random.randint(-15, 15)
            self.clouds.append(cloud)

        # Plataforma simples
        plat_tex = make_platform_texture(220, 20)
        plat = arcade.Sprite()
        plat.texture = plat_tex
        # Centraliza a plataforma baixa
        plat.center_x = SCREEN_WIDTH // 2
        plat.center_y = 150
        self.wall_list.append(plat)

        # Escadas de plataformas (altura de pulo ~120px)
        # Centralizadas em relaÃ§Ã£o ao centro da tela. DistÃ¢ncias pequenas para permitir pulos entre as superiores.
        stair_tex_w = 180
        stair_tex = make_platform_texture(stair_tex_w, 20)
        max_jump_px = int((PLAYER_JUMP_SPEED ** 2) / (2 * GRAVITY))
        step_h = int(max_jump_px * 0.78)
        center_x = SCREEN_WIDTH // 2
        dxs = [180, 170]  # nÃ­veis 2 e 3 (superiores mais prÃ³ximos para salto)
        stairs_left = [(center_x - dxs[i], ground.top + step_h * (i + 2)) for i in range(len(dxs))]
        stairs_right = [(center_x + dxs[i], ground.top + step_h * (i + 2)) for i in range(len(dxs))]
        # Guardar plataformas por andar (nÃ£o criar inimigos aqui)
        row2_stairs = []
        row3_stairs = []
        for x, y in stairs_left + stairs_right:
            p = arcade.Sprite()
            p.texture = stair_tex
            p.center_x = x
            p.center_y = y
            self.wall_list.append(p)
            patrol_min = x - (stair_tex_w // 2 - 10)
            patrol_max = x + (stair_tex_w // 2 - 10)
            if y == ground.top + step_h * 2:
                row2_stairs.append((x, p.top, patrol_min, patrol_max))
            elif y == ground.top + step_h * 3:
                row3_stairs.append((x, p.top, patrol_min, patrol_max))

        # Plataformas extras para popular e espaÃ§ar mais a tela
        dx_base = 160
        # Afastar um pouco as duas plataformas centrais do primeiro andar
        extra_levels = [
            [-3 * dx_base, -1 * dx_base - 40, 1 * dx_base + 40, 3 * dx_base],
            [-2 * dx_base, 0, 2 * dx_base],
        ]
        row1_extras = []
        row2_extras = []
        for i, row in enumerate(extra_levels):
            y = ground.top + step_h * (i + 1)
            for dx in row:
                ex = center_x + dx
                ep = arcade.Sprite()
                ep.texture = stair_tex
                ep.center_x = ex
                ep.center_y = y
                self.wall_list.append(ep)
                patrol_min = ex - (stair_tex_w // 2 - 10)
                patrol_max = ex + (stair_tex_w // 2 - 10)
                if i == 0:
                    row1_extras.append((ex, ep.top, patrol_min, patrol_max))
                else:
                    row2_extras.append((ex, ep.top, patrol_min, patrol_max))

        # BaÃº do espada melhor na plataforma mais alta (direita)
        top_y = max(y for _, y in stairs_left + stairs_right)
        center_top = arcade.Sprite()
        center_top.texture = stair_tex
        center_top.center_x = SCREEN_WIDTH // 2
        center_top.center_y = top_y + step_h
        self.wall_list.append(center_top)
        self.spawn_chest(center_top.center_x, center_top.center_y + 18)
        # Centro para órbita dos morcegos
        self.chest_orbit_center = (center_top.center_x, center_top.center_y + 18)

        # Jogador
        self.player = arcade.Sprite()
        self.player.center_x = 100
        self.player.center_y = ground.top + 30
        self.player.scale = 1.0
        # textura inicial
        self.player.texture = self.textures["idle_right"][0]
        self.player_list.append(self.player)

        # FÃ­sica do jogador
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.wall_list, gravity_constant=GRAVITY)

        # Inimigos
        # Solo: slimes (lentos, 0.5 coraÃ§Ã£o de dano)
        self.spawn_slime(x=400, y=ground.top, min_x=360, max_x=740)
        self.spawn_slime(x=900, y=ground.top, min_x=780, max_x=1150)
        self.spawn_slime(x=1400, y=ground.top, min_x=1260, max_x=1680)

        # Primeiro andar (extras nÃ­vel 1): goblins
        for x, top, mn, mx in row1_extras:
            self.spawn_goblin(x=x, y=top, min_x=mn, max_x=mx)

        # Segundo andar (extras nÃ­vel 2): 2 goblins nas pontas + 1 orc no centro
        if row2_extras:
            row2_sorted = sorted(row2_extras, key=lambda t: t[0])
            # pontas -> goblins
            gx, gt, gmn, gmx = row2_sorted[0]
            self.spawn_goblin(x=gx, y=gt, min_x=gmn, max_x=gmx)
            gx, gt, gmn, gmx = row2_sorted[-1]
            self.spawn_goblin(x=gx, y=gt, min_x=gmn, max_x=gmx)
            # centro -> orc
            mid_idx = len(row2_sorted) // 2
            ox, ot, omn, omx = row2_sorted[mid_idx]
            self.spawn_orc(x=ox, y=ot, min_x=omn, max_x=omx)

        # Ãšltima plataforma antes do baÃº (andares escada mais altos): 2 orcs
        for x, top, mn, mx in row3_stairs:
            self.spawn_orc(x=x, y=top, min_x=mn, max_x=mx)

        # Morcegos: 3 voando sobre o topo, como antes
        self.spawn_bat(x=300, y=400, min_x=150, max_x=600)
        self.spawn_bat(x=900, y=520, min_x=780, max_x=1200)
        self.spawn_bat(x=1400, y=460, min_x=1200, max_x=1700)

    def spawn_slime(self, x: float, y: float, min_x: float, max_x: float):
        enemy = arcade.Sprite()
        enemy_tex = make_slime_textures()
        enemy.enemy_tex = enemy_tex
        enemy.texture = enemy_tex["walk_right"][0]
        enemy.center_x = x
        enemy.bottom = y
        enemy.change_x = SLIME_SPEED
        enemy.bound_left = min_x
        enemy.bound_right = max_x
        enemy.anim_timer = 0.0
        enemy.anim_index = 0
        enemy.facing_right = True
        enemy.type = "slime"
        # Vida/combate
        enemy.max_hp = 3
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 0.5
        self.enemy_list.append(enemy)

    def spawn_bat(self, x: float, y: float, min_x: float, max_x: float):
        enemy = arcade.Sprite()
        enemy_tex = make_bat_textures()
        enemy.enemy_tex = enemy_tex
        enemy.texture = enemy_tex["fly_right"][0]
        enemy.center_x = x
        enemy.center_y = y
        enemy.start_y = y
        enemy.change_x = BAT_SPEED
        enemy.bound_left = min_x
        enemy.bound_right = max_x
        enemy.anim_timer = 0.0
        enemy.anim_index = 0
        enemy.facing_right = True
        enemy.type = "bat"
        # Vida/combate
        enemy.max_hp = 2
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.wave_t = 0.0
        enemy.diving = False
        enemy.dive_timer = 0.0
        enemy.dive_cooldown = 0.0
        enemy.contact_damage = 1.0
        self.enemy_list.append(enemy)

    def spawn_goblin(self, x: float, y: float, min_x: float, max_x: float):
        enemy = arcade.Sprite()
        enemy_tex = make_goblin_textures()
        enemy.enemy_tex = enemy_tex
        enemy.texture = enemy_tex["walk_right"][0]
        enemy.center_x = x
        enemy.bottom = y
        enemy.change_x = GOBLIN_SPEED
        enemy.bound_left = min_x
        enemy.bound_right = max_x
        enemy.anim_timer = 0.0
        enemy.anim_index = 0
        enemy.facing_right = True
        enemy.type = "goblin"
        enemy.max_hp = 3
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 1.0
        self.enemy_list.append(enemy)

    def spawn_orc(self, x: float, y: float, min_x: float, max_x: float):
        enemy = arcade.Sprite()
        enemy_tex = make_orc_textures()
        enemy.enemy_tex = enemy_tex
        enemy.texture = enemy_tex["walk_right"][0]
        enemy.center_x = x
        enemy.bottom = y
        enemy.change_x = ORC_SPEED
        enemy.bound_left = min_x
        enemy.bound_right = max_x
        enemy.anim_timer = 0.0
        enemy.anim_index = 0
        enemy.facing_right = True
        enemy.type = "orc"
        enemy.max_hp = 4
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 1.5
        self.enemy_list.append(enemy)

    def on_draw(self):
        self.clear()

        # CÃ©u simples
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 260, SCREEN_HEIGHT, (50, 70, 110))
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, 260, (60, 90, 70))
        self.clouds.draw()

        self.wall_list.draw()
        self.enemy_list.draw()
        self.pickup_list.draw()
        self.player_list.draw()
        # Efeitos (slash, espada do baú)
        self.fx_list.draw()
        # Barras de vida nos inimigos
        for e in self.enemy_list:
            if getattr(e, 'max_hp', None):
                w = 28
                ratio = max(0.0, min(1.0, e.hp / e.max_hp))
                x0 = e.center_x - w / 2
                y0 = e.top + 6
                arcade.draw_lrbt_rectangle_filled(x0, x0 + w, y0, y0 + 4, (40, 40, 40))
                arcade.draw_lrbt_rectangle_filled(x0, x0 + w * ratio, y0, y0 + 4, (80, 220, 100))
        
        # Banner de upgrade
        if getattr(self, 'banner_timer', 0) > 0:
            t = self.banner_timer
            fade_in = 0.3
            fade_out = 0.3
            total = 3.0
            a = 1.0
            if t > total - fade_out:
                a = max(0.0, (total - t) / fade_out)
            elif t < fade_in:
                a = max(0.0, t / fade_in)
            alpha = int(255 * a)
            text = self.banner_text or "Super Espada Adquirida! Dobro de dano ativado!"
            x = SCREEN_WIDTH // 2 - 280
            y = SCREEN_HEIGHT - 40
            arcade.draw_text(text, x + 2, y - 2, (0, 0, 0, alpha), 18)
            arcade.draw_text(text, x, y, (255, 215, 0, alpha), 18)

        # Vida do jogador (corações com meio-coração)
        heart_w, heart_h = 18, 12
        full = int(self.player_hp)
        has_half = (self.player_hp - full) >= 0.5
        for i in range(self.player_max_hp):
            x0 = 10 + i * (heart_w + 6)
            y0 = SCREEN_HEIGHT - 60
            # base vazia
            arcade.draw_lrbt_rectangle_filled(x0, x0 + heart_w, y0, y0 + heart_h, (80, 70, 70))
            if i < full:
                arcade.draw_lrbt_rectangle_filled(x0, x0 + heart_w, y0, y0 + heart_h, (220, 60, 80))
            elif i == full and has_half:
                arcade.draw_lrbt_rectangle_filled(x0, x0 + heart_w / 2, y0, y0 + heart_h, (220, 60, 80))
        self.score_text.text = f"Score: {self.score}"
        self.score_text.draw()
        # Timer (mm:ss)
        t = max(0, int(self.time_remaining))
        mm, ss = divmod(t, 60)
        self.timer_text.text = f"Tempo: {mm:02d}:{ss:02d}"
        self.timer_text.color = arcade.color.WHITE if self.time_remaining > 30 else arcade.color.SALMON
        self.timer_text.draw()

        # Tela de Game Over
        if self.game_over:
            if self.game_over_title is None:
                self.game_over_title = arcade.Text(
                    "GAME OVER",
                    SCREEN_WIDTH // 2 - 140,
                    SCREEN_HEIGHT // 2 + 80,
                    arcade.color.WHITE,
                    32,
                )
                self.game_over_prompt = arcade.Text(
                    "Digite seu nome e pressione Enter:",
                    SCREEN_WIDTH // 2 - 260,
                    SCREEN_HEIGHT // 2 + 30,
                    arcade.color.ANTIQUE_WHITE,
                    20,
                )
                self.game_over_name = arcade.Text(
                    self.input_name,
                    SCREEN_WIDTH // 2 - 260,
                    SCREEN_HEIGHT // 2 - 10,
                    arcade.color.YELLOW,
                    20,
                )
                self.final_score_text = arcade.Text(
                    f"Score: {self.score}",
                    SCREEN_WIDTH // 2 - 260,
                    SCREEN_HEIGHT // 2 - 50,
                    arcade.color.LIGHT_GREEN,
                    20,
                )
            # Fundo translÃºcido
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 150))
            self.game_over_title.draw()
            self.game_over_prompt.draw()
            self.game_over_name.text = self.input_name + "_"
            self.game_over_name.draw()
            self.final_score_text.text = f"Score: {self.score}"
            self.final_score_text.draw()

    def on_update(self, delta_time: float):
        # Movimento por teclas
        self.player.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_MOVE_SPEED
            self.facing_right = False
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = PLAYER_MOVE_SPEED
            self.facing_right = True

        # FÃ­sica do jogador
        self.physics_engine.update()

        # Timer: perde se acabar o tempo com inimigos restantes
        if not self.game_over:
            self.time_remaining = max(0.0, self.time_remaining - delta_time)
            if self.time_remaining <= 0.0 and len(self.enemy_list) > 0:
                self.game_over = True

        if self.game_over:
            return


        # Impede o jogador de sair pela esquerda/direita da tela
        if self.player.left < 0:
            self.player.left = 0
            if self.player.change_x < 0:
                self.player.change_x = 0
        if self.player.right > SCREEN_WIDTH:
            self.player.right = SCREEN_WIDTH
            if self.player.change_x > 0:
                self.player.change_x = 0

        if self.game_over:
            return

        # Atualiza inimigos (movimento ping-pong/voo + animaÃ§Ã£o + vida)
        for e in list(self.enemy_list):
            # Mortos: tocar animaÃ§Ã£o e remover
            if e.dead:
                e.death_timer += delta_time
                if e.death_timer > 0.45:
                    if not e.scored:
                        self.score += 100
                        e.scored = True
                        # Drop de coraÃ§Ã£o 30%
                        if random.random() < 0.3:
                            self.spawn_heart(e.center_x, e.center_y + 18)
                    e.remove_from_sprite_lists()
                    continue
                # animação de morte
                if e.type in ("slime", "goblin", "orc"):
                    e.facing_right = e.change_x >= 0
                    idx = min(int(e.death_timer / 0.15), 2)
                    key = "die_right" if e.facing_right else "die_left"
                    e.texture = e.enemy_tex[key][idx]
                else:
                    # morcego não tem frames de morte: esmaece enquanto mantém o voo
                    e.alpha = max(0, int(255 * (1.0 - e.death_timer / 0.45)))
                continue

            # Vivo: movimento
            e.center_x += e.change_x
            if e.type == "bat":
                # Dive logic + patrulha em onda (comportamento anterior)
                if e.diving:
                    e.dive_timer += delta_time
                    dir_x = 1 if self.player.center_x > e.center_x else -1
                    e.change_x = (BAT_SPEED + 0.2) * dir_x
                    if e.center_y > self.player.center_y + 8:
                        e.center_y -= 4
                    else:
                        e.center_y += 1  # overshoot leve
                    if e.dive_timer > 1.2 or abs(e.center_y - self.player.center_y) < 10:
                        e.diving = False
                        e.dive_cooldown = 2.5
                else:
                    e.wave_t += delta_time
                    amp = 18
                    base_y = e.start_y + amp * math.sin(e.wave_t * 6)
                    e.center_y += (base_y - e.center_y) * 0.15
                    if e.dive_cooldown > 0:
                        e.dive_cooldown -= delta_time
                    else:
                        player_on_ground = self.player.bottom <= self.ground_top + 6
                        if (not player_on_ground) and abs(self.player.center_x - e.center_x) < 240 and e.center_y > self.player.center_y + 40:
                            e.diving = True
                            e.dive_timer = 0.0
            if e.center_x < e.bound_left:
                e.center_x = e.bound_left
                e.change_x *= -1
            if e.center_x > e.bound_right:
                e.center_x = e.bound_right
                e.change_x *= -1
            e.anim_timer += delta_time
            if e.hurt_timer > 0:
                e.hurt_timer -= delta_time
                if e.anim_timer > 0.12:
                    e.anim_timer = 0
                    e.anim_index = (e.anim_index + 1) % (2 if e.type in ("slime", "goblin", "orc") else 4)
                if e.type in ("slime", "goblin", "orc"):
                    key = "hurt_right" if e.facing_right else "hurt_left"
                else:
                    key = "fly_right" if e.facing_right else "fly_left"
            else:
                if e.anim_timer > 0.18:
                    e.anim_timer = 0
                    e.anim_index = (e.anim_index + 1) % 4
                if e.type in ("slime", "goblin", "orc"):
                    key = "walk_right" if e.facing_right else "walk_left"
                else:  # bat
                    key = "fly_right" if e.facing_right else "fly_left"
            frames = e.enemy_tex[key]
            e.texture = frames[e.anim_index % len(frames)]

            # Dano de contato ao jogador
            if not e.dead and self.player_invuln <= 0 and arcade.check_for_collision(self.player, e):
                dmg = getattr(e, 'contact_damage', 1.0)
                self.player_hp = max(0.0, self.player_hp - float(dmg))
                self.player_invuln = PLAYER_INVULN
                # knockback
                push = 14 if self.player.center_x < e.center_x else -14
                self.player.center_x += push
                if self.player_hp <= 0.0:
                    self.game_over = True
                    return

        # Ataque simples com hitbox na direÃ§Ã£o do guerreiro
        if self.is_attacking:
            self.attack_time -= delta_time
            progress = ATTACK_DURATION - self.attack_time
            off_x = 26 if self.facing_right else -26
            self.attack_sprite.center_x = self.player.center_x + off_x
            self.attack_sprite.center_y = self.player.center_y + 8
            active = ATTACK_HIT_START <= progress <= ATTACK_HIT_END
            if self.attack_time <= 0:
                self.is_attacking = False

            if active:
                hits = arcade.check_for_collision_with_list(self.attack_sprite, self.enemy_list)
                for h in hits:
                    if h in self.enemies_hit:
                        continue
                    self.enemies_hit.add(h)
                    # dano/knockback
                    h.hp -= self.player_damage
                    if h.hp <= 0:
                        h.dead = True
                        h.death_timer = 0.0
                    else:
                        h.hurt_timer = 0.25
                        h.center_x += 10 if self.facing_right else -10

        # Animação do jogador (ciclo de frames)
        self.anim_timer += delta_time
        if self.anim_timer > 0.12:
            self.anim_timer = 0.0
            self.anim_index += 1

        state = "idle"
        if self.is_attacking:
            state = "attack"
        elif abs(self.player.change_x) > 0.1:
            state = "run"

        key = f"{state}_{'right' if self.facing_right else 'left'}"
        frames = self.textures[key]
        if state == "attack":
            # Seleciona frame pelo progresso do ataque
            progress = (ATTACK_DURATION - self.attack_time) / ATTACK_DURATION
            idx = min(int(progress * len(frames)), len(frames) - 1)
        else:
            idx = self.anim_index % len(frames)
        self.player.texture = frames[idx]

        # Decai invulnerabilidade do jogador para permitir tomar dano novamente
        if self.player_invuln > 0.0:
            self.player_invuln = max(0.0, self.player_invuln - delta_time)

        # Atualiza efeitos visuais (espada do baú)
        for fx in list(self.fx_list):
            fx.life += delta_time
            if getattr(fx, 'effect_type', '') == 'sword_pickup':
                dur = getattr(fx, 'duration', 1.6)
                fx.center_y += 40 * delta_time
                fx.alpha = max(0, int(255 * (1 - fx.life / dur)))
                if fx.life >= dur:
                    fx.remove_from_sprite_lists()

        # Coleta de pickups (corações)
        for item in arcade.check_for_collision_with_list(self.player, self.pickup_list):
            if hasattr(item, 'is_heart') and item.is_heart:
                if self.player_hp < float(self.player_max_hp):
                    self.player_hp = min(float(self.player_max_hp), self.player_hp + 1.0)
                item.remove_from_sprite_lists()
            elif hasattr(item, 'is_chest') and item.is_chest:
                # Upgrade de espada: dobra o dano e mostra efeitos
                self.player_damage = 2
                self.super_sword = True
                fx = arcade.Sprite()
                fx.texture = make_sword_fx_texture(22, 48)
                fx.center_x = item.center_x
                fx.center_y = item.center_y + 12
                fx.effect_type = 'sword_pickup'
                fx.life = 0.0
                fx.duration = 1.6
                fx.alpha = 255
                self.fx_list.append(fx)
                self.banner_text = "Super Espada Adquirida! Dobro de dano ativado!"
                self.banner_timer = 3.0
                item.remove_from_sprite_lists()

        # Banner
        if getattr(self, 'banner_timer', 0) > 0:
            self.banner_timer -= delta_time
        # Coleta de pickups (coraÃ§Ãµes)


    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.ENTER:
                self.save_score(self.input_name.strip() or "Player", self.score)
                self.setup()
            elif key == arcade.key.BACKSPACE:
                self.input_name = self.input_name[:-1]
            elif key == arcade.key.ESCAPE:
                self.close()
            return

        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            if self.physics_engine and self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.Z or key == arcade.key.Q:
            if not self.is_attacking:
                self.is_attacking = True
                self.attack_time = ATTACK_DURATION
                self.enemies_hit = set()
        elif key == arcade.key.ESCAPE:
            self.close()
    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_text(self, text: str):
        if self.game_over:
            if len(text) == 1 and text.isprintable() and len(self.input_name) < 16:
                self.input_name += text

    def spawn_heart(self, x: float, y: float):
        heart = arcade.Sprite()
        heart.texture = make_heart_texture(18, 16)
        heart.center_x = x
        heart.center_y = y
        heart.is_heart = True
        self.pickup_list.append(heart)

    def spawn_chest(self, x: float, y: float):
        chest = arcade.Sprite()
        chest.texture = make_chest_texture(28, 22)
        chest.center_x = x
        chest.center_y = y
        chest.is_chest = True
        self.pickup_list.append(chest)

    def save_score(self, name: str, score: int):
        try:
            with open("scores.txt", "a", encoding="utf-8") as f:
                f.write(f"{name};{score}\n")
        except Exception:
            pass


def main():
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()







