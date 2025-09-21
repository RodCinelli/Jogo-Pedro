import arcade
import random
import math
import sqlite3
import os
import time
import io
import wave
from array import array
from PIL import Image
import pyglet
from assets.sprites import (
    make_warrior_textures,
    make_ground_texture,
    make_platform_texture,
    make_slime_textures,
    make_bat_textures,
    make_heart_texture,
    make_chest_texture,
    make_troll_textures,
    make_orc_textures,
    make_goblin_textures,
    make_skeleton_warrior_textures,
    make_skeleton_archer_textures,
    make_arrow_textures,
    make_cloud_texture,
    make_sword_fx_texture,
    make_sun_texture,
    make_moon_texture,
    make_star_texture,
    make_raindrop_texture,
    make_lightning_texture,
)

# Configurações da janela e do jogo
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Warrior Platform"

PLAYER_MOVE_SPEED = 4.0
PLAYER_JUMP_SPEED = 12.0
GRAVITY = 0.6

ENEMY_SPEED = 2.0
# Velocidades por tipo (ajustadas)
SLIME_SPEED = 1.5
GOBLIN_SPEED = 2.0
TROLL_SPEED = 1.8
ORC_SPEED = 1.5
BAT_SPEED = 2.5  # morcego ligeiramente mais rápido que os walkers
ATTACK_DURATION = 0.36
ATTACK_HIT_START = 0.12
ATTACK_HIT_END = 0.28
PLAYER_MAX_HP = 5  # em corações, permite meio-coração
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
        self.sky_list = arcade.SpriteList()
        self.rain_list = arcade.SpriteList()
        self.bolt_list = arcade.SpriteList()
        self.fx_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()
        self.skeleton_archer_textures = make_skeleton_archer_textures()
        self.arrow_textures = make_arrow_textures(28, 6)

        self.player = arcade.Sprite()
        self.physics_engine = None
        self.score = 0
        self.score_text = None
        self.timer_text = None
        self.state = 'title'
        self.player_name = ''
        self.top_scores = []
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
        self.db_path = os.path.join(os.getcwd(), 'warrior_platform.db')
        # Inicializa banco (scores/perfis)
        # Lista de players de SFX ativos para evitar GC precoce
        self._sfx_players = []
        self.ensure_db()
        self.setup()

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.pickup_list = arcade.SpriteList()
        # Recria listas visuais do céu/clima para não sobrar sprites entre partidas
        self.clouds = arcade.SpriteList()
        self.sky_list = arcade.SpriteList()
        self.rain_list = arcade.SpriteList()
        self.bolt_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()
        self.skeleton_archer_textures = make_skeleton_archer_textures()
        self.arrow_textures = make_arrow_textures(28, 6)
        self.score = 0
        self.score_text = arcade.Text("Score: 0", 10, self.height - 30, arcade.color.WHITE, 16)
        # Timer de 10 minutos
        self.time_limit = 600.0
        self.time_remaining = self.time_limit
        # Posição inicial baseada no tamanho atual da janela
        self.timer_text = arcade.Text("Tempo: 10:00", self.width - 10, self.height - 30, arcade.color.WHITE, 16, anchor_x="right")
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
        # Clima
        # day_sunny | day_cloudy | day_rain | night_clear | night_cloudy | night_rain
        self.weather = random.choice(['day_sunny', 'day_cloudy', 'day_rain', 'night_clear', 'night_cloudy', 'night_rain'])
        self.sky_color = (50, 70, 110)
        self.lightning_flash = 0.0
        self.lightning_cd = 0.0
        # SFX (efeitos) – inicializados em init_sfx()
        self.sfx = {}

        # ChÃ£o
        ground_tex = make_ground_texture(self.width, 40)
        ground = arcade.Sprite()
        ground.texture = ground_tex
        ground.center_x = self.width // 2
        ground.center_y = 20
        self.wall_list.append(ground)
        self.ground_top = ground.top

        # Configuração do clima e céu (nuvens, sol/lua, chuva)
        # Cores básicas do céu por clima
        if self.weather.startswith('day_'):
            # dia
            if self.weather == 'day_sunny':
                self.sky_color = (100, 140, 200)
            elif self.weather == 'day_cloudy':
                self.sky_color = (70, 90, 130)
            else:  # day_rain
                self.sky_color = (60, 80, 110)
        else:
            # noite
            if self.weather == 'night_clear':
                self.sky_color = (18, 22, 34)
            elif self.weather == 'night_cloudy':
                self.sky_color = (22, 26, 40)
            else:  # night_rain
                self.sky_color = (20, 24, 36)

        # Nuvens (espalhadas e ajustadas pelo clima)
        generate_clouds = self.weather in ('day_cloudy', 'day_rain', 'night_cloudy', 'night_rain')
        if generate_clouds:
            num_cols = 8
            margin_x = 140
            x_step = (self.width - 2 * margin_x) / (num_cols - 1)
            y_rows = [self.height - 200, self.height - 160, self.height - 240, self.height - 120]
            for i in range(num_cols):
                w = random.randint(120, 240)
                h = random.randint(50, 90)
                cloud = arcade.Sprite()
                base_alpha = 210
                if self.weather == 'day_cloudy':
                    base_alpha = random.randint(210, 245)
                elif self.weather == 'night_cloudy':
                    base_alpha = random.randint(110, 165)
                elif self.weather.endswith('rain'):
                    base_alpha = random.randint(180, 210)
                cloud.texture = make_cloud_texture(w, h, alpha=base_alpha)
                jitter = random.randint(-30, 30)
                cloud.center_x = int(margin_x + i * x_step + jitter)
                cloud.center_y = y_rows[i % len(y_rows)] + random.randint(-15, 15)
                self.clouds.append(cloud)

        # Sol/Lua/Estrelas/Raindrops
        if self.weather == 'day_sunny':
            sun = arcade.Sprite()
            sun.texture = make_sun_texture(72)
            sun.center_x = self.width - 120
            sun.center_y = self.height - 120
            self.sky_list.append(sun)
        elif self.weather == 'night_clear':
            moon = arcade.Sprite()
            moon.texture = make_moon_texture(58)
            moon.center_x = self.width - 160
            moon.center_y = self.height - 140
            self.sky_list.append(moon)
            # estrelas
            for _ in range(40):
                st = arcade.Sprite()
                st.texture = make_star_texture(random.randint(2, 3))
                st.center_x = random.randint(10, self.width - 10)
                st.center_y = random.randint(int(self.height * 0.6), self.height - 10)
                st.alpha = random.randint(160, 230)
                self.sky_list.append(st)
        elif self.weather == 'night_cloudy':
            moon = arcade.Sprite()
            moon.texture = make_moon_texture(58)
            moon.center_x = self.width - 160
            moon.center_y = self.height - 140
            self.sky_list.append(moon)
        if self.weather.endswith('rain'):
            # gotas de chuva
            drops = int(220 * (self.width / 1920))
            drop_tex = make_raindrop_texture(2, 10)
            for _ in range(drops):
                d = arcade.Sprite()
                d.texture = drop_tex
                d.center_x = random.randint(0, self.width)
                d.center_y = random.randint(260, self.height)
                d.speed = random.uniform(260, 420)
                d.wind = random.uniform(-20, 20)
                self.rain_list.append(d)

        # Plataforma simples
        plat_tex = make_platform_texture(220, 20)
        plat = arcade.Sprite()
        plat.texture = plat_tex
        # Centraliza a plataforma baixa
        plat.center_x = self.width // 2
        plat.center_y = 150

        # Escadas de plataformas (altura de pulo ~120px)
        # Centralizadas em relação ao centro da tela. Distâncias pequenas para permitir pulos entre as superiores.
        stair_tex_w = 180
        stair_tex = make_platform_texture(stair_tex_w, 20)
        def _tinted_platform(base_texture: arcade.Texture, suffix: str, color: tuple[int, int, int], blend: float) -> arcade.Texture:
            base_img = base_texture.image.copy()
            overlay = Image.new("RGBA", base_img.size, (color[0], color[1], color[2], 255))
            tinted = Image.blend(base_img, overlay, blend)
            base_name = getattr(base_texture, "name", None) or "platform"
            return arcade.Texture(name=f"{base_name}_{suffix}", image=tinted)

        green_platform_tex = _tinted_platform(stair_tex, "ivy", (70, 130, 90), 0.35)
        dry_platform_tex = _tinted_platform(stair_tex, "dry", (184, 134, 72), 0.32)
        blood_platform_tex = _tinted_platform(stair_tex, "blood", (170, 50, 50), 0.30)
        snow_tex_w = 440
        snow_base_tex = make_platform_texture(snow_tex_w, 20)
        snow_platform_tex = _tinted_platform(snow_base_tex, "snow", (235, 240, 255), 0.55)
        snow_step_w = 280
        snow_step_base = make_platform_texture(snow_step_w, 18)
        snow_step_tex = _tinted_platform(snow_step_base, "snow_step", (235, 240, 255), 0.55)

        plat.texture = _tinted_platform(plat_tex, "ivy_main", (70, 130, 90), 0.35)
        self.wall_list.append(plat)

        max_jump_px = int((PLAYER_JUMP_SPEED ** 2) / (2 * GRAVITY))
        step_h = int(max_jump_px * 0.78)
        center_x = self.width // 2
        dxs = [180, 170]  # níveis 2 e 3 (superiores mais próximos para salto)
        stairs_left = [(center_x - dxs[i], ground.top + step_h * (i + 2)) for i in range(len(dxs))]
        stairs_right = [(center_x + dxs[i], ground.top + step_h * (i + 2)) for i in range(len(dxs))]
        # Guardar plataformas por andar (não criar inimigos aqui)
        row2_stairs = []
        row3_stairs = []
        for x, y in stairs_left + stairs_right:
            p = arcade.Sprite()
            if y == ground.top + step_h * 2:
                p.texture = dry_platform_tex
            elif y == ground.top + step_h * 3:
                p.texture = blood_platform_tex
            else:
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

        # Plataformas extras para popular e espaçar mais a tela
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
                ep.texture = green_platform_tex if i == 0 else dry_platform_tex
                ep.center_x = ex
                ep.center_y = y
                self.wall_list.append(ep)
                patrol_min = ex - (stair_tex_w // 2 - 10)
                patrol_max = ex + (stair_tex_w // 2 - 10)
                if i == 0:
                    row1_extras.append((ex, ep.top, patrol_min, patrol_max))
                else:
                    row2_extras.append((ex, ep.top, patrol_min, patrol_max))

        # Baú do espada melhor na plataforma mais alta (direita)
        top_y = max(y for _, y in stairs_left + stairs_right)
        center_top = arcade.Sprite()
        center_top.texture = stair_tex
        center_top.center_x = self.width // 2
        center_top.center_y = top_y + step_h
        self.wall_list.append(center_top)
        self.spawn_chest(center_top.center_x, center_top.center_y + 18)
        # Centro para órbita dos morcegos
        self.chest_orbit_center = (center_top.center_x, center_top.center_y + 18)

        # Quintas plataformas (escada nevada)
        stair_offset = 210
        stair_y = center_top.center_y + int(step_h * 0.8)
        fifth_platforms = []
        patrol_pad = snow_step_w // 2 - 14
        for dx in (-stair_offset, stair_offset):
            stair_step = arcade.Sprite()
            stair_step.texture = snow_step_tex
            stair_step.center_x = center_top.center_x + dx
            stair_step.center_y = stair_y
            self.wall_list.append(stair_step)
            patrol_min = stair_step.center_x - patrol_pad
            patrol_max = stair_step.center_x + patrol_pad
            fifth_platforms.append((stair_step.center_x, stair_step.top, patrol_min, patrol_max))

        self.fifth_platforms = fifth_platforms

        if fifth_platforms:
            edge_offset = snow_step_w // 2 - 270
            for idx, (cx, top, mn, mx) in enumerate(fifth_platforms):
                facing_right = (idx == 0)
                spawn_x = cx + (edge_offset if facing_right else -edge_offset)
                self.spawn_skeleton_archer(x=spawn_x, y=top, min_x=mn, max_x=mx, facing_right=facing_right)

        # Sexta plataforma acima do baú (extensa e com aparência de neve)
        snow_platform = arcade.Sprite()
        snow_platform.texture = snow_platform_tex
        snow_platform.center_x = center_top.center_x
        snow_platform.center_y = stair_y + step_h
        self.wall_list.append(snow_platform)

        sixth_patrol_pad = snow_tex_w // 2 - 24
        sixth_min = snow_platform.center_x - sixth_patrol_pad
        sixth_max = snow_platform.center_x + sixth_patrol_pad
        sixth_top = snow_platform.top
        self.sixth_platform_bounds = (snow_platform.center_x, sixth_top, sixth_min, sixth_max)

        # Inimigos da sexta plataforma (esqueletos defendendo o topo)
        for offset in (-140, 140):
            self.spawn_skeleton(x=snow_platform.center_x + offset, y=sixth_top, min_x=sixth_min, max_x=sixth_max)

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
        # Solo: slimes (lentos, 0.5 coração de dano)
        self.spawn_slime(x=400, y=ground.top, min_x=360, max_x=740)
        self.spawn_slime(x=900, y=ground.top, min_x=780, max_x=1150)
        self.spawn_slime(x=1400, y=ground.top, min_x=1260, max_x=1680)

        # Primeiro andar (extras nível 1): goblins
        for x, top, mn, mx in row1_extras:
            self.spawn_goblin(x=x, y=top, min_x=mn, max_x=mx)

        # Segundo andar (extras nível 2): 2 trolls nas pontas + 1 orc no centro
        if row2_extras:
            row2_sorted = sorted(row2_extras, key=lambda t: t[0])
            # pontas -> trolls
            gx, gt, gmn, gmx = row2_sorted[0]
            self.spawn_troll(x=gx, y=gt, min_x=gmn, max_x=gmx)
            gx, gt, gmn, gmx = row2_sorted[-1]
            self.spawn_troll(x=gx, y=gt, min_x=gmn, max_x=gmx)
            # centro -> orc
            mid_idx = len(row2_sorted) // 2
            ox, ot, omn, omx = row2_sorted[mid_idx]
            self.spawn_orc(x=ox, y=ot, min_x=omn, max_x=omx)

        # Última plataforma antes do baú (andares escada mais altos): 2 orcs
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
        # Nome/color do inimigo (pré-criado para performance)
        enemy.display_name = "Slime"
        enemy.name_color = (80, 200, 120, 255)
        enemy.name_font = 12
        enemy.name_text = arcade.Text(enemy.display_name, x, y + 20, enemy.name_color, enemy.name_font, anchor_x="center")
        enemy.name_shadow = arcade.Text(enemy.display_name, x + 1, y + 19, (0, 0, 0, 200), enemy.name_font, anchor_x="center")
        # Vida/combate
        enemy.max_hp = 3
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 0.5
        enemy.show_hp_bar = False
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
        # Nome/color do inimigo
        enemy.display_name = "Bat"
        enemy.name_color = (150, 100, 200, 255)
        enemy.name_font = 12
        enemy.name_text = arcade.Text(enemy.display_name, x, y + 20, enemy.name_color, enemy.name_font, anchor_x="center")
        enemy.name_shadow = arcade.Text(enemy.display_name, x + 1, y + 19, (0, 0, 0, 200), enemy.name_font, anchor_x="center")
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
        # Evita mergulho imediato ao iniciar a fase
        enemy.dive_cooldown = 2.5
        # Parâmetros do mergulho (direção e alvo vertical capturados no início)
        enemy.dive_dir = 0
        enemy.dive_target_y = y
        enemy.contact_damage = 1.0
        enemy.show_hp_bar = False
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
        # Nome/color do inimigo
        enemy.display_name = "Goblin"
        enemy.name_color = (60, 170, 90, 255)
        enemy.name_font = 12
        enemy.name_text = arcade.Text(enemy.display_name, x, y + 20, enemy.name_color, enemy.name_font, anchor_x="center")
        enemy.name_shadow = arcade.Text(enemy.display_name, x + 1, y + 19, (0, 0, 0, 200), enemy.name_font, anchor_x="center")
        enemy.max_hp = 3
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 1.0
        enemy.show_hp_bar = False
        self.enemy_list.append(enemy)


    def spawn_troll(self, x: float, y: float, min_x: float, max_x: float):
        enemy = arcade.Sprite()
        enemy_tex = make_troll_textures()
        enemy.enemy_tex = enemy_tex
        enemy.texture = enemy_tex["walk_right"][0]
        enemy.center_x = x
        enemy.bottom = y
        enemy.change_x = TROLL_SPEED
        enemy.bound_left = min_x
        enemy.bound_right = max_x
        enemy.anim_timer = 0.0
        enemy.anim_index = 0
        enemy.facing_right = True
        enemy.type = "troll"
        # Nome/color do inimigo
        enemy.display_name = "Troll"
        enemy.name_color = (230, 140, 70, 255)
        enemy.name_font = 12
        enemy.name_text = arcade.Text(enemy.display_name, x, y + 20, enemy.name_color, enemy.name_font, anchor_x="center")
        enemy.name_shadow = arcade.Text(enemy.display_name, x + 1, y + 19, (0, 0, 0, 200), enemy.name_font, anchor_x="center")
        enemy.max_hp = 5
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 1.5
        enemy.show_hp_bar = False
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
        # Nome/color do inimigo
        enemy.display_name = "Orc"
        enemy.name_color = (200, 70, 70, 255)
        enemy.name_font = 12
        enemy.name_text = arcade.Text(enemy.display_name, x, y + 20, enemy.name_color, enemy.name_font, anchor_x="center")
        enemy.name_shadow = arcade.Text(enemy.display_name, x + 1, y + 19, (0, 0, 0, 200), enemy.name_font, anchor_x="center")
        enemy.max_hp = 5
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 1.5
        enemy.show_hp_bar = False
        self.enemy_list.append(enemy)

    def spawn_skeleton(self, x: float, y: float, min_x: float, max_x: float):
        enemy = arcade.Sprite()
        enemy_tex = make_skeleton_warrior_textures()
        enemy.enemy_tex = enemy_tex
        enemy.texture = enemy_tex["walk_right"][0]
        enemy.center_x = x
        enemy.bottom = y
        enemy.change_x = 1.7
        enemy.bound_left = min_x
        enemy.bound_right = max_x
        enemy.anim_timer = 0.0
        enemy.anim_index = 0
        enemy.facing_right = True
        enemy.type = "skeleton"
        enemy.display_name = "Skeleton Warrior"
        enemy.name_color = (190, 190, 200, 255)
        enemy.name_font = 12
        enemy.name_text = arcade.Text(enemy.display_name, x, y + 26, enemy.name_color, enemy.name_font, anchor_x="center")
        enemy.name_shadow = arcade.Text(enemy.display_name, x + 1, y + 25, (0, 0, 0, 200), enemy.name_font, anchor_x="center")
        enemy.max_hp = 4
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 1.0
        enemy.show_hp_bar = False
        self.enemy_list.append(enemy)

    def spawn_skeleton_archer(self, x: float, y: float, min_x: float, max_x: float, facing_right: bool):
        enemy = arcade.Sprite()
        enemy_tex = self.skeleton_archer_textures or make_skeleton_archer_textures()
        enemy.enemy_tex = enemy_tex
        enemy.texture = enemy_tex["walk_right"][0] if facing_right else enemy_tex["walk_left"][0]
        enemy.center_x = x
        enemy.bottom = y
        enemy.change_x = 0.0
        enemy.bound_left = x
        enemy.bound_right = x
        enemy.stand_x = x
        enemy.anim_timer = 0.0
        enemy.anim_index = 0
        enemy.facing_right = facing_right
        enemy.type = "skeleton_archer"
        enemy.display_name = "Skeleton Archer"
        enemy.name_color = (190, 190, 200, 255)
        enemy.name_font = 12
        enemy.name_text = arcade.Text(enemy.display_name, x, y + 26, enemy.name_color, enemy.name_font, anchor_x="center")
        enemy.name_shadow = arcade.Text(enemy.display_name, x + 1, y + 25, (0, 0, 0, 200), enemy.name_font, anchor_x="center")
        enemy.max_hp = 3
        enemy.hp = enemy.max_hp
        enemy.hurt_timer = 0.0
        enemy.dead = False
        enemy.death_timer = 0.0
        enemy.scored = False
        enemy.contact_damage = 1.0
        enemy.show_hp_bar = False
        enemy.shoot_cooldown = 0.0
        enemy.shoot_interval = 3.0
        enemy.projectile_speed = 7.0
        enemy.arrow_damage = 1.0
        enemy.arrow_textures = self.arrow_textures
        self.enemy_list.append(enemy)

    def spawn_archer_arrow(self, shooter: arcade.Sprite, direction: int):
        arrow = arcade.Sprite()
        textures = self.arrow_textures or make_arrow_textures(28, 6)
        tex_key = "right" if direction >= 0 else "left"
        arrow.texture = textures[tex_key]
        arrow.center_x = shooter.center_x + direction * 22
        arrow.center_y = shooter.center_y + 2
        arrow.change_x = direction * getattr(shooter, 'projectile_speed', 7.0)
        arrow.damage = getattr(shooter, 'arrow_damage', 1.0)
        arrow.distance = 0.0
        arrow.max_distance = 1400.0
        self.projectile_list.append(arrow)

    def _update_projectiles(self, delta_time: float) -> bool:
        for arrow in list(self.projectile_list):
            arrow.center_x += arrow.change_x
            arrow.distance = getattr(arrow, 'distance', 0.0) + abs(arrow.change_x)
            if arrow.distance >= getattr(arrow, 'max_distance', 1400.0) or arrow.right < 0 or arrow.left > self.width:
                arrow.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision_with_list(arrow, self.wall_list):
                arrow.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision(self.player, arrow):
                if self.player_invuln <= 0:
                    dmg = getattr(arrow, 'damage', 1.0)
                    self.player_hp = max(0.0, self.player_hp - float(dmg))
                    self.player_invuln = PLAYER_INVULN
                    self.play_sfx('hurt', 1.0)
                    push = 12 if arrow.change_x > 0 else -12
                    self.player.center_x += push
                    if self.player_hp <= 0.0:
                        self.end_game('game_over')
                        return True
                arrow.remove_from_sprite_lists()
        return False

    def on_draw(self):
        self.clear()
        # Tela de título (usa Text para performance)
        if self.state == 'title':
            # Usa dimensões reais da janela e centraliza; textos em cache para performance
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (20, 20, 30))
            self._ensure_title_ui()
            # Caixa de texto
            x0, y0, x1, y1 = self._title_box
            arcade.draw_lrbt_rectangle_filled(x0, x1, y0, y1, (44, 46, 64))
            arcade.draw_lrbt_rectangle_outline(x0, x1, y0, y1, (90, 94, 122), border_width=2)
            # Atualiza nome com caret piscando
            caret = '_' if (time.perf_counter() % 1.0) < 0.5 else ' '
            self.name_field_text.text = (self.player_name or '') + caret
            self.name_field_text.draw()
            # Botão
            bx0, by0, bx1, by1 = self.start_btn
            hover = getattr(self, 'mouse_x', None) is not None and bx0 <= self.mouse_x <= bx1 and by0 <= getattr(self, 'mouse_y', -1) <= by1
            btn_color = (80, 140, 90) if hover else (70, 120, 80)
            arcade.draw_lrbt_rectangle_filled(bx0, bx1, by0, by1, btn_color)
            arcade.draw_lrbt_rectangle_outline(bx0, bx1, by0, by1, (30, 60, 36), border_width=2)
            self.button_text.draw()
            # Textos fixos
            self.title_text.draw()
            self.prompt_text.draw()
            for t in self.controls_texts:
                t.draw()
            return

        # Céu simples
        arcade.draw_lrbt_rectangle_filled(0, self.width, 260, self.height, self.sky_color)
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, 260, (60, 90, 70))
        self.sky_list.draw()
        self.clouds.draw()
        if self.weather.endswith('rain'):
            self.rain_list.draw()
            self.bolt_list.draw()
            # Flash branco rápido simulando relâmpago
            if getattr(self, 'lightning_flash', 0.0) > 0.0:
                a = max(0, min(255, int(180 * (self.lightning_flash / 0.15))))
                if a > 0:
                    arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (255, 255, 255, a))

        self.wall_list.draw()
        self.enemy_list.draw()
        self.projectile_list.draw()
        self.pickup_list.draw()
        self.player_list.draw()
        # Efeitos (slash, espada do baú)
        self.fx_list.draw()
        # Barras de vida e nomes sobre inimigos (labels pré-criados para performance)
        for e in self.enemy_list:
            w = 28
            ratio = max(0.0, min(1.0, e.hp / e.max_hp))
            x0 = e.center_x - w / 2
            y0 = e.top + 6
            # Barra de vida só aparece após o inimigo sofrer dano
            if getattr(e, 'show_hp_bar', False) and e.hp > 0:
                arcade.draw_lrbt_rectangle_filled(x0, x0 + w, y0, y0 + 4, (40, 40, 40))
                arcade.draw_lrbt_rectangle_filled(x0, x0 + w * ratio, y0, y0 + 4, (80, 220, 100))
            # Nome do inimigo (textos criados no spawn)
            if hasattr(e, 'name_text') and hasattr(e, 'name_shadow'):
                name_y = y0 + (8 if getattr(e, 'show_hp_bar', False) else 2)
                e.name_shadow.x = e.center_x + 1
                e.name_shadow.y = name_y - 1
                e.name_text.x = e.center_x
                e.name_text.y = name_y
                e.name_shadow.draw()
                e.name_text.draw()
        
        # Banner de upgrade (fade in/out, centralizado) — textos em cache
        if getattr(self, 'banner_timer', 0) > 0:
            t = self.banner_timer
            fade_in, fade_out, total = 0.3, 0.3, 3.0
            a = 1.0
            if t > total - fade_out:
                a = max(0.0, (total - t) / fade_out)
            elif t < fade_in:
                a = max(0.0, t / fade_in)
            alpha = int(255 * a)
            btxt = self.banner_text or "Super Espada Adquirida! Dobro de dano ativado!"
            self._ensure_banner_ui(btxt)
            # Atualiza transparência e desenha
            self.banner_shadow_text.color = (0, 0, 0, alpha)
            self.banner_main_text.color = (255, 215, 0, alpha)
            self.banner_shadow_text.draw()
            self.banner_main_text.draw()

        # Vida do jogador (corações com meio-coração)
        heart_w, heart_h = 18, 12
        full = int(self.player_hp)
        has_half = (self.player_hp - full) >= 0.5
        for i in range(self.player_max_hp):
            x0 = 10 + i * (heart_w + 6)
            # espaço único (score ~height-30, corações ~height-60)
            y0 = self.height - 60
            # base vazia
            arcade.draw_lrbt_rectangle_filled(x0, x0 + heart_w, y0, y0 + heart_h, (80, 70, 70))
            if i < full:
                arcade.draw_lrbt_rectangle_filled(x0, x0 + heart_w, y0, y0 + heart_h, (220, 60, 80))
            elif i == full and has_half:
                arcade.draw_lrbt_rectangle_filled(x0, x0 + heart_w / 2, y0, y0 + heart_h, (220, 60, 80))
        self.score_text.text = f"Score: {self.score}"
        # alinhar com a margem superior como o timer (usar dimensões atuais)
        self.score_text.x = 10
        self.score_text.y = self.height - 30
        self.score_text.draw()
        # Timer (mm:ss) — ancorado no canto superior direito (usar tamanho atual da janela)
        t = max(0, int(self.time_remaining))
        mm, ss = divmod(t, 60)
        self.timer_text.text = f"Tempo: {mm:02d}:{ss:02d}"
        self.timer_text.color = arcade.color.WHITE if self.time_remaining > 30 else arcade.color.SALMON
        self.timer_text.x = self.width - 10
        self.timer_text.y = self.height - 30
        self.timer_text.draw()

        # Overlays de fim com Top 5 (textos em cache)
        if self.state in ('victory', 'game_over'):
            ww, wh = self.width, self.height
            arcade.draw_lrbt_rectangle_filled(0, ww, 0, wh, (0, 0, 0, 150))
            self._ensure_end_ui()
            # Desenha elementos
            self.end_title_text.draw()
            self.end_heading_text.draw()
            for t in self.end_scores_texts:
                t.draw()
            self.end_hint_text.draw()
    def on_update(self, delta_time: float):
        # Estados que não atualizam o mundo
        if self.state != 'playing':
            if getattr(self, 'banner_timer', 0) > 0:
                self.banner_timer -= delta_time
            # Clean up finished SFX players even when paused/end screens
            self._cleanup_sfx_players()
            return

        # Movimento por teclas
        self.player.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_MOVE_SPEED
            self.facing_right = False
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = PLAYER_MOVE_SPEED
            self.facing_right = True

        # Física do jogador
        self.physics_engine.update()
        # Limpa players de SFX finalizados
        self._cleanup_sfx_players()

        # Timer: perde se acabar o tempo com inimigos restantes
        self.time_remaining = max(0.0, self.time_remaining - delta_time)
        if self.time_remaining <= 0.0 and len(self.enemy_list) > 0:
            self.end_game('game_over')
            return


        # Impede o jogador de sair pela esquerda/direita da tela
        if self.player.left < 0:
            self.player.left = 0
            if self.player.change_x < 0:
                self.player.change_x = 0
        if self.player.right > self.width:
            self.player.right = self.width
            if self.player.change_x > 0:
                self.player.change_x = 0

        if self.game_over:
            return

        # Atualiza inimigos (movimento ping-pong/voo + animação + vida)
        for e in list(self.enemy_list):
            # Mortos: tocar animação e remover
            if e.dead:
                e.death_timer += delta_time
                if e.death_timer > 0.45:
                    if not e.scored:
                        self.score += 100
                        e.scored = True
                        # Drop de coração 30%
                        if random.random() < 0.25:
                            self.spawn_heart(e.center_x, e.center_y + 18)
                    e.remove_from_sprite_lists()
                    continue
                # animação de morte
                if e.type in ("slime", "goblin", "troll", "orc", "skeleton", "skeleton_archer"):
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
            if e.type == "skeleton_archer":
                current_cd = getattr(e, 'shoot_cooldown', 0.0)
                current_cd = max(0.0, current_cd - delta_time)
                e.shoot_cooldown = current_cd
                direction = 1 if e.facing_right else -1
                player_dx = self.player.center_x - e.center_x
                horizontal = (player_dx * direction) > 0 and abs(player_dx) < self.width * 0.7
                vertical = abs(self.player.center_y - (e.center_y + 24)) < 120
                if horizontal and vertical and current_cd <= 0.0:
                    self.spawn_archer_arrow(e, direction)
                    e.shoot_cooldown = getattr(e, 'shoot_interval', 3.0)
            if e.type == "bat":
                # Patrulha em onda + mergulho controlado (sem perseguir no solo)
                prev_y = e.center_y
                if e.diving:
                    e.dive_timer += delta_time
                    # Persegue o jogador APENAS enquanto ele estiver no ar
                    player_on_ground = self.player.bottom <= self.ground_top + 6
                    target_y = None
                    if not player_on_ground:
                        dir_x = 1 if self.player.center_x > e.center_x else -1
                        e.change_x = (BAT_SPEED + 0.2) * dir_x
                        target_y = self.player.center_y
                        if e.center_y > target_y + 8:
                            e.center_y -= 4
                        else:
                            e.center_y += 1  # overshoot leve
                    else:
                        # Jogador no chão: não perseguir; encerra o mergulho
                        e.diving = False
                        e.dive_cooldown = 2.5
                    # Evita atravessar plataformas durante o rasante
                    if e.diving and e.center_y < prev_y:
                        wall_hits = arcade.check_for_collision_with_list(e, self.wall_list)
                        if wall_hits:
                            # Encosta no topo da plataforma e encerra o mergulho
                            top_y = max(w.top for w in wall_hits)
                            e.bottom = top_y
                            e.diving = False
                            e.dive_cooldown = 2.5
                    # Encerra por tempo ou por alcançar a altura alvo (quando perseguindo no ar)
                    if e.diving and (e.dive_timer > 1.2 or (target_y is not None and abs(e.center_y - target_y) < 10)):
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
                            # Captura direção/altura no início do mergulho (não persegue depois)
                            e.dive_dir = 1 if self.player.center_x > e.center_x else -1
                            e.dive_target_y = self.player.center_y
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
                    e.anim_index = (e.anim_index + 1) % (2 if e.type in ("slime", "goblin", "troll", "orc", "skeleton", "skeleton_archer") else 4)
                if e.type in ("slime", "goblin", "troll", "orc", "skeleton", "skeleton_archer"):
                    key = "hurt_right" if e.facing_right else "hurt_left"
                else:
                    key = "fly_right" if e.facing_right else "fly_left"
            else:
                if e.anim_timer > 0.18:
                    e.anim_timer = 0
                    e.anim_index = (e.anim_index + 1) % 4
                if e.type in ("slime", "goblin", "troll", "orc", "skeleton", "skeleton_archer"):
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
                self.play_sfx('hurt', 1.0)
                # knockback
                push = 14 if self.player.center_x < e.center_x else -14
                self.player.center_x += push
            if self.player_hp <= 0.0:
                    self.end_game('game_over')
                    return

        if self._update_projectiles(delta_time):
            return

        # Vitória: todos os inimigos foram derrotados
        if self.state == 'playing' and len(self.enemy_list) == 0:
            self.end_game('victory')
            return

        # Ataque simples com hitbox na direção do guerreiro
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
                    # Exibir barra de vida a partir do primeiro dano
                    try:
                        h.show_hp_bar = True
                    except Exception:
                        pass
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
                self.play_sfx('pickup', 1.0)
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
                self.play_sfx('powerup', 1.0)
                item.remove_from_sprite_lists()

        # Banner
        if getattr(self, 'banner_timer', 0) > 0:
            self.banner_timer -= delta_time

        # --- Clima dinâmico ---
        if self.weather.endswith('rain'):
            # movimento das gotas
            for d in self.rain_list:
                d.center_y -= d.speed * delta_time
                d.center_x += d.wind * delta_time
                if d.center_y < 260:
                    d.center_y = self.height + random.randint(0, 80)
                    d.center_x = random.randint(0, self.width)
            # relâmpagos ocasionais
            if self.lightning_cd > 0:
                self.lightning_cd -= delta_time
            else:
                if random.random() < 0.02:
                    bolt = arcade.Sprite()
                    bolt.texture = make_lightning_texture(8, 140)
                    bolt.center_x = random.randint(120, self.width - 120)
                    bolt.center_y = random.randint(int(self.height * 0.7), self.height - 40)
                    bolt.alpha = 255
                    bolt.life = 0.0
                    self.bolt_list.append(bolt)
                    self.lightning_flash = 0.15
                    self.lightning_cd = 2.5
            # atenua/some com raios
            for b in list(self.bolt_list):
                b.life += delta_time
                b.alpha = max(0, int(255 * (1.0 - b.life / 0.2)))
                if b.life >= 0.2:
                    b.remove_from_sprite_lists()
            if self.lightning_flash > 0:
                self.lightning_flash = max(0.0, self.lightning_flash - delta_time)

    def on_key_press(self, key, modifiers):
        # Entrada na tela de título
        if self.state == 'title':
            if key == arcade.key.ENTER:
                # Exige nome para iniciar
                if (self.player_name or '').strip():
                    self.start_game()
                return
            elif key == arcade.key.BACKSPACE:
                self.player_name = self.player_name[:-1]
                return
            elif key == arcade.key.ESCAPE:
                self.close()
                return
            # Não adicionar caracteres aqui para evitar duplicação com on_text
            return

        # Tela de Game Over / Vitória
        if self.state in ('game_over', 'victory'):
            if key == arcade.key.ENTER:
                # Volta ao título e reinicia o mundo
                self.state = 'title'
                self.setup()
                return
            elif key == arcade.key.ESCAPE:
                self.close()
                return

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
        elif key == arcade.key.UP:
            if self.physics_engine and self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.SPACE:
            if not self.is_attacking:
                self.is_attacking = True
                self.attack_time = ATTACK_DURATION
                self.enemies_hit = set()
                self.play_sfx('attack', 1.0)
        elif key == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_text(self, text: str):
        if self.state == 'title':
            if len(text) == 1 and text.isprintable() and len(self.player_name) < 16:
                self.player_name += text
            return
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

    def end_game(self, status: str):
        # status: 'game_over' ou 'victory'
        try:
            # Registra score no banco
            self.record_score(self.player_name.strip() or 'Player', int(self.score))
        except Exception:
            # Fallback em arquivo
            try:
                self.save_score(self.player_name.strip() or 'Player', int(self.score))
            except Exception:
                pass
        # Atualiza top scores em memória
        try:
            self.top_scores = self.get_top_scores(5)
        except Exception:
            self.top_scores = []
        # Ajusta estado
        self.state = status
        self.game_over = (status == 'game_over')
        # Para o banner caso esteja ativo
        self.banner_timer = 0.0
        # Sons finais por estado
        try:
            if status == 'game_over':
                self.play_sfx('game_over', 1.0)
            elif status == 'victory':
                self.play_sfx('victory', 1.0)
        except Exception:
            pass

    # --- Efeitos sonoros (SFX) ---
    def init_sfx(self):
        self.sfx = {
            'attack': self._make_sfx_attack(),
            'hurt': self._make_sfx_hurt(),
            'powerup': self._make_sfx_powerup(),
            'pickup': self._make_sfx_pickup(),
            'game_over': self._make_sfx_game_over(),
            'victory': self._make_sfx_victory(),
        }

    def play_sfx(self, name: str, volume: float = 1.0):
        src = self.sfx.get(name)
        if not src:
            return
        try:
            player = pyglet.media.Player()
            # Volume em escala 0.0 a 1.0 (100%)
            player.volume = max(0.0, min(1.0, float(volume)))
            player.queue(src)
            player.play()
            # Mantém referência até terminar para não cortar o som
            self._sfx_players.append(player)
        except Exception:
            pass

    def _cleanup_sfx_players(self):
        # Remove players que já finalizaram a reprodução
        alive = []
        for p in self._sfx_players:
            try:
                if getattr(p, 'playing', False):
                    alive.append(p)
                else:
                    try:
                        p.delete()
                    except Exception:
                        pass
            except Exception:
                pass
        self._sfx_players = alive

    def _make_pcm(self, samples: array, rate: int = 22050):
        bio = io.BytesIO()
        with wave.open(bio, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(samples.tobytes())
        bio.seek(0)
        try:
            return pyglet.media.load('sfx.wav', file=bio, streaming=False)
        except Exception:
            return None

    def _make_sfx_attack(self):
        rate = 22050
        dur = 0.18
        n = int(rate * dur)
        buf = array('h', [0] * n)
        for i in range(n):
            t = i / rate
            f = 220 + 880 * (1 - t / dur)
            env = max(0.0, 1.0 - t / dur)
            v = int(3000 * env * math.sin(2 * math.pi * f * t))
            buf[i] = v
        return self._make_pcm(buf, rate)

    def _make_sfx_hurt(self):
        rate = 22050
        dur = 0.15
        n = int(rate * dur)
        buf = array('h', [0] * n)
        noise = 0.4
        for i in range(n):
            t = i / rate
            f = 160
            env = max(0.0, 1.0 - t / dur)
            s = math.sin(2 * math.pi * f * t)
            v = int(2500 * env * (0.6 * s + noise * (random.random() * 2 - 1)))
            buf[i] = v
        return self._make_pcm(buf, rate)

    def _make_sfx_powerup(self):
        rate = 22050
        dur = 0.35
        n = int(rate * dur)
        buf = array('h', [0] * n)
        for i in range(n):
            t = i / rate
            f = 600 + 900 * (t / dur)
            env = 0.6 if t < dur * 0.7 else 0.6 * (1 - (t - dur * 0.7) / (dur * 0.3))
            v = int(2500 * max(0.0, env) * math.sin(2 * math.pi * f * t))
            buf[i] = v
        return self._make_pcm(buf, rate)

    def _make_sfx_pickup(self):
        # Two quick rising beeps
        rate = 22050
        segments = [(880, 0.08), (1320, 0.10)]
        out = array('h')
        for freq, dur in segments:
            n = int(rate * dur)
            for i in range(n):
                t = i / rate
                env = max(0.0, 1.0 - (t / dur))
                s = math.sin(2 * math.pi * freq * t)
                out.append(int(2600 * env * s))
            # tiny gap
            gap = int(rate * 0.01)
            out.extend([0] * gap)
        return self._make_pcm(out, rate)

    def _make_sfx_game_over(self):
        # Three descending tones
        rate = 22050
        segments = [(440, 0.18), (330, 0.18), (262, 0.22)]
        out = array('h')
        for freq, dur in segments:
            n = int(rate * dur)
            for i in range(n):
                t = i / rate
                # Slow decay per segment
                env = max(0.0, 1.0 - 0.9 * (t / dur))
                s = math.sin(2 * math.pi * freq * t)
                out.append(int(3000 * env * s))
            out.extend([0] * int(rate * 0.015))
        return self._make_pcm(out, rate)

    def _make_sfx_victory(self):
        # Simple ascending fanfare
        rate = 22050
        segments = [(784, 0.16), (988, 0.16), (1176, 0.20)]
        out = array('h')
        for freq, dur in segments:
            n = int(rate * dur)
            for i in range(n):
                t = i / rate
                # Quick attack, short release
                env = 1.0 if t < dur * 0.85 else max(0.0, 1.0 - (t - dur * 0.85) / (dur * 0.15))
                s = math.sin(2 * math.pi * freq * t)
                out.append(int(2800 * env * s))
            out.extend([0] * int(rate * 0.012))
        return self._make_pcm(out, rate)

    # --- Entradas de mouse para tela inicial ---
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x, self.mouse_y = x, y

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.state == 'title' and getattr(self, 'start_btn', None):
            bx0, by0, bx1, by1 = self.start_btn
            if bx0 <= x <= bx1 and by0 <= y <= by1:
                # Exige nome para iniciar
                if (self.player_name or '').strip():
                    self.start_game()

    # --- Helpers ---
    def start_game(self):
        self.player_name = (self.player_name or 'Player').strip()[:16]
        try:
            self.save_profile(self.player_name)
        except Exception:
            pass
        self.state = 'playing'
        self.setup()
        # Sons do jogo (ataque, dano, powerup)
        self.init_sfx()

    def _ensure_title_ui(self):
        # Recria textos quando necessário (primeira vez ou redimensionamento)
        need_build = False
        if not hasattr(self, '_title_ui_size'):
            need_build = True
        elif self._title_ui_size != (self.width, self.height):
            need_build = True

        if not need_build:
            # Ainda precisamos atualizar o texto do nome (feito no on_draw) —
            # mas layout/posições permanecem
            return

        self._title_ui_size = (self.width, self.height)
        cx, cy = self.width // 2, self.height // 2
        title_size = int(min(self.width, self.height) * 0.04)
        prompt_size = int(title_size * 0.5)
        btn_w = int(self.width * 0.16)
        btn_h = max(36, int(self.height * 0.038))
        box_w = btn_w
        box_h = max(32, int(self.height * 0.03))

        # Título e prompt
        self.title_text = arcade.Text(
            "Warrior Platform", cx, cy + int(self.height * 0.13), arcade.color.GOLD, title_size, anchor_x="center"
        )
        prompt_y = cy + int(self.height * 0.065)
        self.prompt_text = arcade.Text(
            "Digite seu nome:", cx, prompt_y, arcade.color.ANTIQUE_WHITE, prompt_size, anchor_x="center"
        )

        # Caixa de nome
        x0, x1 = cx - box_w // 2, cx + box_w // 2
        gap = int(prompt_size * 1.2)
        y1 = prompt_y - gap
        y0 = y1 - box_h
        self._title_box = (x0, y0, x1, y1)
        input_font = max(18, int(prompt_size * 0.9))
        field_cx = (x0 + x1) // 2
        self.name_field_text = arcade.Text("", field_cx, y0 + (box_h - input_font) // 2, arcade.color.WHITE, input_font, anchor_x="center")

        # Botão iniciar
        bx0, bx1 = cx - btn_w // 2, cx + btn_w // 2
        btn_gap = int(self.height * 0.03)
        by0 = y0 - btn_gap - btn_h
        by1 = by0 + btn_h
        self.start_btn = (bx0, by0, bx1, by1)
        self.button_text = arcade.Text(
            "Começar Jogo (Enter)", cx, by0 + (btn_h - prompt_size) // 2, arcade.color.WHITE, max(20, int(prompt_size * 0.9)), anchor_x="center"
        )

        # Manual de controles
        manual_size = max(14, int(prompt_size * 0.75))
        line_gap = max(22, int(manual_size * 1.4))
        spacing = max(26, int(btn_h * 1.0))
        base_y = by0 - spacing
        controls = [
            "Setas Esquerda/Direita: Mover",
            "Seta para Cima: Pular",
            "Barra de Espaço: Atacar",
            "ENTER: Iniciar   |   ESC: Sair",
        ]
        self.controls_texts = []
        for i, txt in enumerate(controls):
            self.controls_texts.append(
                arcade.Text(txt, cx, base_y - i * line_gap, arcade.color.LIGHT_GRAY, manual_size, anchor_x="center")
            )

    def _ensure_end_ui(self):
        # Garante top_scores preenchido
        if not getattr(self, 'top_scores', None):
            try:
                self.top_scores = self.get_top_scores(5)
            except Exception:
                self.top_scores = []

        ww, wh = self.width, self.height
        key = (ww, wh, self.state, tuple((nm, int(sc)) for (nm, sc) in (self.top_scores or [])))
        if getattr(self, '_end_ui_key', None) == key:
            return
        self._end_ui_key = key

        # Título (Venceu/Game Over)
        title_txt = "VOCÊ VENCEU!" if self.state == 'victory' else "GAME OVER"
        self.end_title_text = arcade.Text(title_txt, ww // 2, wh // 2 + 140, arcade.color.WHITE, 32, anchor_x="center")
        # Cabeçalho Top 5
        self.end_heading_text = arcade.Text("Top 5 Scores:", ww // 2, wh // 2 + 100, arcade.color.ANTI_FLASH_WHITE, 20, anchor_x="center")
        # Linhas Top 5
        self.end_scores_texts = []
        y = wh // 2 + 70
        for i, (nm, sc) in enumerate((self.top_scores or [])[:5], start=1):
            col = arcade.color.GOLD if i == 1 else arcade.color.WHITE
            self.end_scores_texts.append(arcade.Text(f"{i}. {nm} - {sc}", ww // 2, y, col, 18, anchor_x="center"))
            y -= 24
        # Dica
        self.end_hint_text = arcade.Text("Pressione ENTER para voltar ao título", ww // 2, wh // 2 - 60, arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def _ensure_banner_ui(self, text: str):
        # Reconstrói textos do banner ao mudar tamanho da janela ou conteúdo
        win_w, win_h = self.width, self.height
        key = (text, win_w, win_h)
        if getattr(self, '_banner_ui_key', None) == key and hasattr(self, 'banner_main_text'):
            return
        self._banner_ui_key = key
        banner_shift = int(win_w * 0.015)  # ~0.7% da largura
        # Sombra
        self.banner_shadow_text = arcade.Text(text, win_w // 2 + banner_shift + 2, win_h - 42, (0, 0, 0, 255), 18, anchor_x="center")
        # Principal
        self.banner_main_text = arcade.Text(text, win_w // 2 + banner_shift, win_h - 40, (255, 215, 0, 255), 18, anchor_x="center")

        # --- Persistência (SQLite + fallback em arquivo) ---
    def ensure_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
            cur.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, player_name TEXT, score INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            conn.commit()
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def save_profile(self, name: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO players(name) VALUES (?)", (name.strip() or 'Player',))
            conn.commit()
        finally:
            conn.close()

    def record_score(self, name: str, score: int):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO scores(player_name, score) VALUES (?, ?)", (name.strip() or 'Player', int(score)))
            conn.commit()
        finally:
            conn.close()

    def get_top_scores(self, limit: int = 5):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT player_name, MAX(score) as s FROM scores GROUP BY player_name ORDER BY s DESC LIMIT ?", (limit,))
            return cur.fetchall()
        except Exception:
            return []
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def save_score(self, name: str, score: int):
        # Fallback em arquivo (além do SQLite)
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


