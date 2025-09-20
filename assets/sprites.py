import random
import arcade
from PIL import Image, ImageDraw, ImageOps


def _outline(d: ImageDraw.ImageDraw, rect, color=(20, 20, 28, 255)):
    x0, y0, x1, y1 = rect
    d.rectangle([x0, y0, x1, y1], outline=color)



def make_warrior_textures():
    """Gera o guerreiro com elmo de cavaleiro, armadura vermelha com detalhes amarelos
    e espada a ~30 graus (semi-horizontal) pronta para ataque.
    """
    w, h = 48, 64
    # Cores: vermelho/amarelo
    armor = (200, 60, 60, 255)
    armor_dark = (140, 30, 30, 255)
    accent = (230, 200, 60, 255)
    skin = (234, 200, 170, 255)
    boot = (60, 40, 30, 255)
    sword_handle = (140, 90, 30, 255)
    sword_guard = (230, 200, 80, 255)
    sword_blade = (225, 230, 240, 255)

    def frame(leg_phase: int, arm_pose: str):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        # Pernas/botas com passada visível
        left_forward = leg_phase in (0, 2)
        lx0, lx1 = 16, 22
        rx0, rx1 = 26, 32
        if left_forward:
            d.rectangle([lx0 + 1, 16, lx1 + 1, 28], fill=armor_dark)
            d.rectangle([rx0 - 1, 18, rx1 - 1, 24], fill=armor_dark)
            d.rectangle([16 + 1, 12, 22 + 1, 18], fill=boot)
            d.rectangle([26 - 1, 12, 32 - 1, 18], fill=boot)
        else:
            d.rectangle([lx0 + 1, 18, lx1 + 1, 24], fill=armor_dark)
            d.rectangle([rx0 - 1, 16, rx1 - 1, 28], fill=armor_dark)
            d.rectangle([16 - 1, 12, 22 - 1, 18], fill=boot)
            d.rectangle([26 + 1, 12, 32 + 1, 18], fill=boot)

        # Tronco/peitoral com placas e detalhe amarelo
        d.rectangle([14, 28, 34, 46], fill=armor)
        d.rectangle([14, 40, 34, 42], fill=armor_dark)
        d.rectangle([14, 34, 34, 36], fill=armor_dark)
        d.rectangle([14, 28, 34, 30], fill=accent)
        _outline(d, [14, 28, 34, 46])
        # Ombreiras
        d.rectangle([12, 44, 18, 50], fill=armor_dark)
        d.rectangle([30, 44, 36, 50], fill=armor_dark)
        d.rectangle([12, 48, 18, 50], fill=accent)
        d.rectangle([30, 48, 36, 50], fill=accent)

        # Elmo de cavaleiro (fechado com viseira)
        d.rectangle([16, 56, 32, 62], fill=armor_dark)  # casco
        # crista/amarela superior
        d.rectangle([18, 62, 30, 64], fill=accent)
        # rosto sob viseira
        d.rectangle([18, 46, 30, 58], fill=skin)
        # viseira estreita + narizeira
        d.rectangle([18, 52, 30, 54], fill=(20, 30, 50, 255))
        d.rectangle([23, 54, 25, 58], fill=armor_dark)
        _outline(d, [18, 46, 30, 58])

        # Braço e Espada (~45 graus em relação à horizontal)
        if arm_pose == "down":
            d.rectangle([30, 44, 32, 50], fill=sword_handle)
            d.rectangle([32, 46, 36, 48], fill=sword_guard)
            # lâmina diagonal (~45°)
            d.polygon([(36, 46), (49, 33), (51, 35), (38, 48)], fill=sword_blade)
        elif arm_pose == "mid":
            d.rectangle([30, 42, 32, 48], fill=sword_handle)
            d.rectangle([32, 44, 36, 46], fill=sword_guard)
            d.polygon([(36, 44), (49, 31), (51, 33), (38, 46)], fill=sword_blade)
        elif arm_pose == "up":
            d.rectangle([28, 50, 30, 62], fill=sword_handle)
            d.rectangle([28, 60, 36, 62], fill=sword_guard)
            d.rectangle([36, 58, 42, 62], fill=sword_blade)
        elif arm_pose == "wind":
            d.rectangle([30, 42, 32, 58], fill=sword_handle)
            d.rectangle([29, 56, 35, 58], fill=sword_guard)
            d.rectangle([35, 54, 46, 58], fill=sword_blade)
        elif arm_pose == "swing":
            d.rectangle([22, 40, 34, 44], fill=sword_handle)
            d.rectangle([22, 44, 34, 46], fill=sword_guard)
            d.rectangle([34, 42, 48, 46], fill=sword_blade)
        elif arm_pose == "follow":
            d.rectangle([30, 28, 32, 42], fill=sword_handle)
            d.rectangle([29, 40, 35, 42], fill=sword_guard)
            d.rectangle([32, 28, 42, 30], fill=sword_blade)

        # Cinto detalhe
        d.rectangle([14, 36, 34, 38], fill=(40, 30, 20, 255))

        return img

    # animações
    idle = [frame(0, "down"), frame(2, "down")]
    run = [frame(0, "down"), frame(1, "mid"), frame(2, "down"), frame(3, "mid")]
    attack = [frame(0, "wind"), frame(1, "up"), frame(2, "swing"), frame(3, "follow"), frame(0, "down")]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    textures = {
        "idle_right": [tex("idle_r0", idle[0]), tex("idle_r1", idle[1])],
        "run_right": [tex("run_r0", run[0]), tex("run_r1", run[1]), tex("run_r2", run[2]), tex("run_r3", run[3])],
        "attack_right": [tex("atk_r0", attack[0]), tex("atk_r1", attack[1]), tex("atk_r2", attack[2]), tex("atk_r3", attack[3]), tex("atk_r4", attack[4])],
        "idle_left": [tex("idle_l0", mirror(idle[0])), tex("idle_l1", mirror(idle[1]))],
        "run_left": [tex("run_l0", mirror(run[0])), tex("run_l1", mirror(run[1])), tex("run_l2", mirror(run[2])), tex("run_l3", mirror(run[3]))],
        "attack_left": [tex("atk_l0", mirror(attack[0])), tex("atk_l1", mirror(attack[1])), tex("atk_l2", mirror(attack[2])), tex("atk_l3", mirror(attack[3])), tex("atk_l4", mirror(attack[4]))],
    }
    return textures


def make_sword_fx_texture(width: int = 18, height: int = 42) -> arcade.Texture:
    """Espada com brilho para efeito de upgrade do baú."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    handle = (150, 100, 60, 255)
    guard = (210, 200, 150, 255)
    blade = (235, 240, 250, 255)
    glow = (255, 240, 120, 120)
    # brilho ao redor
    d.ellipse([2, 2, width - 2, height - 2], fill=(255, 255, 200, 25), outline=None)
    # punho
    d.rectangle([width // 2 - 1, height - 12, width // 2 + 1, height - 4], fill=handle)
    # guarda
    d.rectangle([width // 2 - 5, height - 14, width // 2 + 5, height - 12], fill=guard)
    # lâmina
    d.rectangle([width // 2 - 1, 4, width // 2 + 1, height - 14], fill=blade)
    d.rectangle([width // 2 - 0, 6, width // 2 + 0, height - 16], fill=(255, 255, 255, 180))
    # halo de brilho
    d.ellipse([width // 2 - 7, height - 18, width // 2 + 7, height - 8], fill=glow)
    return arcade.Texture(name=f"sword_fx_{width}x{height}", image=ImageOps.flip(img))


def make_slash_textures():
    """Conjunto de 3 frames de efeito de corte (slash), direita/esquerda."""
    w, h = 64, 48

    def frame(alpha: int, tilt: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        color = (255, 240, 160, alpha)
        core = (255, 255, 255, min(255, alpha + 40))
        # formato em cunha
        d.polygon([(10, 20 + tilt), (54, 14 + tilt), (54, 26 + tilt)], fill=color)
        d.polygon([(12, 21 + tilt), (46, 16 + tilt), (46, 24 + tilt)], fill=core)
        return img

    f0 = frame(180, -3)
    f1 = frame(220, 0)
    f2 = frame(160, 3)

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    right = [tex("slash_r0", f0), tex("slash_r1", f1), tex("slash_r2", f2)]
    left = [tex("slash_l0", mirror(f0)), tex("slash_l1", mirror(f1)), tex("slash_l2", mirror(f2))]
    return {"slash_right": right, "slash_left": left}


# --- Clima: sol, lua, estrela, chuva, raio ---
def make_sun_texture(diameter: int = 64) -> arcade.Texture:
    img = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = diameter // 2
    center = (r, r)
    body = (255, 215, 70, 255)
    glow = (255, 240, 150, 200)
    # corpo
    d.ellipse([4, 4, diameter - 4, diameter - 4], fill=body)
    # halo
    d.ellipse([0, 0, diameter, diameter], outline=glow, width=3)
    # raios simples
    for i in range(8):
        ang = i * 45
        if i % 2 == 0:
            l = r + 6
        else:
            l = r + 2
        # desenha pequenos traços ao redor
        if i % 2 == 0:
            # vertical/horizontal
            if ang == 0:
                d.line([center[0], 2, center[0], 10], fill=glow, width=2)
            elif ang == 90:
                d.line([2, center[1], 10, center[1]], fill=glow, width=2)
            elif ang == 180:
                d.line([center[0], diameter - 10, center[0], diameter - 2], fill=glow, width=2)
            else:
                d.line([diameter - 10, center[1], diameter - 2, center[1]], fill=glow, width=2)
    return arcade.Texture(name=f"sun_{diameter}", image=ImageOps.flip(img))


def make_moon_texture(diameter: int = 56) -> arcade.Texture:
    img = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = (230, 230, 240, 255)
    shade = (180, 180, 200, 220)
    d.ellipse([0, 0, diameter - 1, diameter - 1], fill=body)
    # craters
    for cx, cy, r in [(diameter*0.35, diameter*0.35, 4), (diameter*0.6, diameter*0.5, 3), (diameter*0.4, diameter*0.7, 5)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=shade)
    return arcade.Texture(name=f"moon_{diameter}", image=ImageOps.flip(img))


def make_star_texture(size: int = 3) -> arcade.Texture:
    s = max(2, size)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, s - 1, s - 1], fill=(255, 255, 255, 220))
    return arcade.Texture(name=f"star_{s}", image=ImageOps.flip(img))


def make_raindrop_texture(width: int = 2, height: int = 10) -> arcade.Texture:
    w = max(2, width)
    h = max(8, height)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (120, 170, 255, 200)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=w//2, fill=color)
    return arcade.Texture(name=f"raindrop_{w}x{h}", image=ImageOps.flip(img))


def make_lightning_texture(width: int = 8, height: int = 120) -> arcade.Texture:
    w = max(6, width)
    h = max(40, height)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bolt = (255, 240, 170, 255)
    # ziguezague simples
    path = [
        (w//2, 0),
        (w//2 - 2, h*0.25),
        (w//2 + 2, h*0.45),
        (w//2 - 3, h*0.65),
        (w//2 + 1, h*0.85),
        (w//2 - 2, h)
    ]
    d.line(path, fill=bolt, width=3)
    return arcade.Texture(name=f"lightning_{w}x{h}", image=ImageOps.flip(img))


def make_ground_texture(width: int, height: int) -> arcade.Texture:
    """Gera textura do chÃ£o com grama e terra com ruÃ­do simples."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    grass_h = max(6, int(height * 0.35))
    dirt_h = height - grass_h

    # Terra base
    d.rectangle([0, 0, width, dirt_h], fill=(112, 82, 54, 255))
    # Pontos de pedra
    for _ in range(width // 8):
        x = random.randint(0, width - 3)
        y = random.randint(2, dirt_h - 3)
        c = random.choice([(130, 100, 70, 255), (95, 70, 48, 255)])
        d.rectangle([x, y, x + 2, y + 2], fill=c)

    # Grama topo (duas faixas de tons)
    d.rectangle([0, dirt_h, width, height], fill=(62, 142, 78, 255))
    d.rectangle([0, height - 2, width, height], fill=(200, 240, 180, 255))
    # LÃ¢minas de grama
    for x in range(0, width, 6):
        top = height - random.randint(0, 2)
        d.line([x, dirt_h, x, top], fill=(70, 160, 90, 255))

    return arcade.Texture(name=f"ground_{width}x{height}", image=img)


def make_platform_texture(width: int, height: int) -> arcade.Texture:
    """Textura de plataforma de madeira com detalhes."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    base = (120, 92, 58, 255)
    dark = (86, 66, 42, 255)
    light = (170, 134, 90, 255)

    d.rectangle([0, 0, width, height], fill=base)
    # TÃ¡buas verticais
    plank_w = 28
    for x in range(0, width, plank_w):
        d.line([x, 0, x, height], fill=dark)
        # nÃ³s da madeira
        for _ in range(2):
            px = x + random.randint(6, plank_w - 6)
            py = random.randint(4, height - 6)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], outline=dark, fill=light)
    # Borda superior
    d.rectangle([0, height - 3, width, height], fill=light)

    return arcade.Texture(name=f"plat_{width}x{height}", image=img)


def make_slime_textures(base=(80, 200, 120, 255)):
    """Cria texturas de slime (walk/hurt/die) com frames bÃ¡sicos."""
    w, h = 36, 28

    def slime_frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        squish = [0, 2, 0, 2][phase % 4]
        body_h = h - 4 - squish
        d.rounded_rectangle([2, 2, w - 2, 2 + body_h], radius=8, fill=base, outline=(30, 120, 80, 255))
        # Olhos
        d.rectangle([10, body_h // 2 + 2, 12, body_h // 2 + 4], fill=(20, 40, 30, 255))
        d.rectangle([w - 12, body_h // 2 + 2, w - 10, body_h // 2 + 4], fill=(20, 40, 30, 255))
        # brilho
        d.ellipse([6, body_h + 2 - 8, 10, body_h + 2 - 4], fill=(220, 255, 240, 120))
        return img

    walk = [slime_frame(i) for i in range(4)]
    # Hurt: versÃ£o mais clara
    def tint(img, a=80):
        c = Image.new("RGBA", img.size, (255, 255, 255, a))
        return Image.alpha_composite(img, c)
    hurt = [tint(walk[1]), tint(walk[2])]
    # Die: encolhe em trÃªs passos
    def shrink(img, s):
        w, h = img.size
        nw, nh = int(w * s), int(h * s)
        tmp = img.resize((nw, nh), Image.NEAREST)
        pad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        pad.paste(tmp, ((w - nw) // 2, 2))
        return pad
    die = [shrink(walk[0], 0.8), shrink(walk[0], 0.55), shrink(walk[0], 0.3)]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    return {
        "walk_right": [tex("sl_r0", walk[0]), tex("sl_r1", walk[1]), tex("sl_r2", walk[2]), tex("sl_r3", walk[3])],
        "walk_left": [tex("sl_l0", mirror(walk[0])), tex("sl_l1", mirror(walk[1])), tex("sl_l2", mirror(walk[2])), tex("sl_l3", mirror(walk[3]))],
        "hurt_right": [tex("sl_hr0", hurt[0]), tex("sl_hr1", hurt[1])],
        "hurt_left": [tex("sl_hl0", mirror(hurt[0])), tex("sl_hl1", mirror(hurt[1]))],
        "die_right": [tex("sl_dr0", die[0]), tex("sl_dr1", die[1]), tex("sl_dr2", die[2])],
        "die_left": [tex("sl_dl0", mirror(die[0])), tex("sl_dl1", mirror(die[1])), tex("sl_dl2", mirror(die[2]))],
    }


def make_bat_textures(base=(150, 100, 200, 255)):
    """Cria texturas de morcego com 4 frames de voo."""
    w, h = 32, 20

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Corpo
        d.ellipse([12, 6, 20, 14], fill=base, outline=(60, 40, 90, 255))
        # CabeÃ§a/orelhas
        d.rectangle([9, 7, 12, 12], fill=base)
        d.polygon([(9, 12), (7, 16), (11, 14)], fill=(60, 40, 90, 255))
        # Asas variam pela fase
        if phase % 2 == 0:
            # asas estendidas
            d.polygon([(12, 10), (2, 6), (4, 14)], fill=base)
            d.polygon([(20, 10), (30, 6), (28, 14)], fill=base)
        else:
            # asas batendo
            d.polygon([(12, 10), (4, 2), (6, 10)], fill=base)
            d.polygon([(20, 10), (28, 2), (26, 10)], fill=base)
        return img

    fly = [frame(i) for i in range(4)]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    return {
        "fly_right": [tex("bat_r0", fly[0]), tex("bat_r1", fly[1]), tex("bat_r2", fly[2]), tex("bat_r3", fly[3])],
        "fly_left": [tex("bat_l0", mirror(fly[0])), tex("bat_l1", mirror(fly[1])), tex("bat_l2", mirror(fly[2])), tex("bat_l3", mirror(fly[3]))],
    }


def make_goblin_textures(base=(60, 170, 90, 255)):
    """Cria texturas simples de um goblin que anda (walk/hurt/die).

    MantÃ©m o mesmo conjunto de chaves do slime para reaproveitar lÃ³gica.
    """
    w, h = 36, 42

    body = base
    dark = (30, 90, 50, 255)
    eye = (20, 20, 20, 255)
    belt = (80, 60, 30, 255)

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Pernas alternadas com leve deslocamento horizontal
        leg_shift = [0, 2, 0, 2][phase % 4]
        off = 1 if phase % 2 == 0 else -1
        d.rectangle([10 + off, 2, 14 + off, 10 + leg_shift], fill=dark)
        d.rectangle([22 - off, 2, 26 - off, 10 + (2 - leg_shift)], fill=dark)
        # Tronco
        d.rectangle([8, 10, 28, 28], fill=body, outline=dark)
        # Cinto
        d.rectangle([8, 16, 28, 18], fill=belt)
        # CabeÃ§a com orelhas
        d.rectangle([10, 28, 26, 38], fill=body, outline=dark)
        d.polygon([(10, 38), (6, 36), (10, 34)], fill=dark)
        d.polygon([(26, 38), (30, 36), (26, 34)], fill=dark)
        # Olho
        d.rectangle([14, 32, 16, 34], fill=eye)
        d.rectangle([20, 32, 22, 34], fill=eye)
        return img

    walk = [frame(i) for i in range(4)]

    def tint(img, a=80):
        c = Image.new("RGBA", img.size, (255, 255, 255, a))
        return Image.alpha_composite(img, c)

    hurt = [tint(walk[1]), tint(walk[2])]

    def shrink(img, s):
        w0, h0 = img.size
        nw, nh = int(w0 * s), int(h0 * s)
        tmp = img.resize((nw, nh), Image.NEAREST)
        pad = Image.new("RGBA", (w0, h0), (0, 0, 0, 0))
        pad.paste(tmp, ((w0 - nw) // 2, 2))
        return pad

    die = [shrink(walk[0], 0.8), shrink(walk[0], 0.55), shrink(walk[0], 0.3)]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    return {
        "walk_right": [tex("gb_r0", walk[0]), tex("gb_r1", walk[1]), tex("gb_r2", walk[2]), tex("gb_r3", walk[3])],
        "walk_left": [tex("gb_l0", mirror(walk[0])), tex("gb_l1", mirror(walk[1])), tex("gb_l2", mirror(walk[2])), tex("gb_l3", mirror(walk[3]))],
        "hurt_right": [tex("gb_hr0", hurt[0]), tex("gb_hr1", hurt[1])],
        "hurt_left": [tex("gb_hl0", mirror(hurt[0])), tex("gb_hl1", mirror(hurt[1]))],
        "die_right": [tex("gb_dr0", die[0]), tex("gb_dr1", die[1]), tex("gb_dr2", die[2])],
        "die_left": [tex("gb_dl0", mirror(die[0])), tex("gb_dl1", mirror(die[1])), tex("gb_dl2", mirror(die[2]))],
    }




def make_troll_textures(base=(210, 120, 50, 255)):
    """Cria texturas de troll alaranjado com animações de caminhada, dano e morte."""
    w, h = 38, 46

    body = base
    dark = (130, 60, 30, 255)
    eye = (20, 20, 20, 255)
    belt = (120, 80, 40, 255)
    tusk = (240, 230, 210, 255)
    hair = (255, 190, 110, 255)
    club = (150, 100, 50, 255)
    club_dark = (100, 60, 30, 255)

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Pernas alternadas com leve oscilação vertical
        leg_shift = [0, 3, 0, 3][phase % 4]
        off = 1 if phase % 2 == 0 else -1
        d.rectangle([10 + off, 2, 14 + off, 12 + leg_shift], fill=dark)
        d.rectangle([22 - off, 2, 26 - off, 12 + (3 - leg_shift)], fill=dark)
        # Braço esquerdo relaxado
        d.rectangle([6, 18, 10, 30], fill=body, outline=dark)
        # Braço direito segurando um porrete
        club_y0 = 18 + (1 if phase % 2 == 0 else 0)
        d.rectangle([28, club_y0, 32, club_y0 + 10], fill=club, outline=club_dark)
        d.ellipse([27, club_y0 + 8, 35, club_y0 + 18], fill=club, outline=club_dark)
        d.rectangle([26, 18, 30, 32], fill=body, outline=dark)
        # Tronco largo
        d.rectangle([8, 14, 30, 32], fill=body, outline=dark)
        # Cinto
        d.rectangle([8, 22, 30, 24], fill=belt)
        # Cabeça com cabelo desgrenhado
        d.rectangle([10, 32, 28, 42], fill=body, outline=dark)
        d.polygon([(10, 42), (8, 46), (14, 44)], fill=hair)
        d.polygon([(28, 42), (30, 46), (24, 44)], fill=hair)
        d.rectangle([12, 42, 26, 44], fill=hair)
        # Olhos e presas
        d.rectangle([14, 36, 16, 38], fill=eye)
        d.rectangle([22, 36, 24, 38], fill=eye)
        d.rectangle([16, 34, 18, 36], fill=tusk)
        d.rectangle([20, 34, 22, 36], fill=tusk)
        # Nariz
        d.rectangle([18, 36, 20, 38], fill=dark)
        return img

    walk = [frame(i) for i in range(4)]

    def tint(img, a=70):
        c = Image.new("RGBA", img.size, (255, 255, 255, a))
        return Image.alpha_composite(img, c)

    hurt = [tint(walk[1]), tint(walk[2])]

    def shrink(img, s):
        w0, h0 = img.size
        nw, nh = int(w0 * s), int(h0 * s)
        tmp = img.resize((nw, nh), Image.NEAREST)
        pad = Image.new("RGBA", (w0, h0), (0, 0, 0, 0))
        pad.paste(tmp, ((w0 - nw) // 2, 2))
        return pad

    die = [shrink(walk[0], 0.8), shrink(walk[0], 0.55), shrink(walk[0], 0.3)]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    return {
        "walk_right": [tex("troll_r0", walk[0]), tex("troll_r1", walk[1]), tex("troll_r2", walk[2]), tex("troll_r3", walk[3])],
        "walk_left": [tex("troll_l0", mirror(walk[0])), tex("troll_l1", mirror(walk[1])), tex("troll_l2", mirror(walk[2])), tex("troll_l3", mirror(walk[3]))],
        "hurt_right": [tex("troll_hr0", hurt[0]), tex("troll_hr1", hurt[1])],
        "hurt_left": [tex("troll_hl0", mirror(hurt[0])), tex("troll_hl1", mirror(hurt[1]))],
        "die_right": [tex("troll_dr0", die[0]), tex("troll_dr1", die[1]), tex("troll_dr2", die[2])],
        "die_left": [tex("troll_dl0", mirror(die[0])), tex("troll_dl1", mirror(die[1])), tex("troll_dl2", mirror(die[2]))],
    }

def make_orc_textures(base=(200, 70, 70, 255)):
    """Texturas de um orc vermelho que anda (walk/hurt/die).

    Usa o mesmo conjunto de chaves dos walkers para encaixar na lÃ³gica atual.
    """
    w, h = 40, 48
    body = base
    dark = (120, 40, 40, 255)
    eye = (15, 15, 15, 255)
    belt = (90, 70, 40, 255)

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Pernas alternadas com leve deslocamento horizontal
        leg_shift = [0, 2, 0, 2][phase % 4]
        off = 1 if phase % 2 == 0 else -1
        d.rectangle([12 + off, 2, 16 + off, 12 + leg_shift], fill=dark)
        d.rectangle([24 - off, 2, 28 - off, 12 + (2 - leg_shift)], fill=dark)
        # Tronco robusto
        d.rectangle([8, 12, 32, 32], fill=body, outline=dark)
        # Cinto
        d.rectangle([8, 20, 32, 22], fill=belt)
        # Ombreiras escuras
        d.rectangle([6, 32, 12, 36], fill=dark)
        d.rectangle([28, 32, 34, 36], fill=dark)
        # CabeÃ§a com presas
        d.rectangle([10, 32, 30, 44], fill=body, outline=dark)
        d.rectangle([14, 36, 16, 38], fill=eye)
        d.rectangle([24, 36, 26, 38], fill=eye)
        d.rectangle([18, 32, 22, 34], fill=(230, 220, 220, 255))  # presas
        return img

    walk = [frame(i) for i in range(4)]

    def tint(img, a=70):
        c = Image.new("RGBA", img.size, (255, 255, 255, a))
        return Image.alpha_composite(img, c)

    hurt = [tint(walk[1]), tint(walk[2])]

    def shrink(img, s):
        w0, h0 = img.size
        nw, nh = int(w0 * s), int(h0 * s)
        tmp = img.resize((nw, nh), Image.NEAREST)
        pad = Image.new("RGBA", (w0, h0), (0, 0, 0, 0))
        pad.paste(tmp, ((w0 - nw) // 2, 2))
        return pad

    die = [shrink(walk[0], 0.8), shrink(walk[0], 0.55), shrink(walk[0], 0.3)]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    return {
        "walk_right": [tex("orc_r0", walk[0]), tex("orc_r1", walk[1]), tex("orc_r2", walk[2]), tex("orc_r3", walk[3])],
        "walk_left": [tex("orc_l0", mirror(walk[0])), tex("orc_l1", mirror(walk[1])), tex("orc_l2", mirror(walk[2])), tex("orc_l3", mirror(walk[3]))],
        "hurt_right": [tex("orc_hr0", hurt[0]), tex("orc_hr1", hurt[1])],
        "hurt_left": [tex("orc_hl0", mirror(hurt[0])), tex("orc_hl1", mirror(hurt[1]))],
        "die_right": [tex("orc_dr0", die[0]), tex("orc_dr1", die[1]), tex("orc_dr2", die[2])],
        "die_left": [tex("orc_dl0", mirror(die[0])), tex("orc_dl1", mirror(die[1])), tex("orc_dl2", mirror(die[2]))],
    }


def make_heart_texture(width: int = 18, height: int = 16) -> arcade.Texture:
    """Cria textura de coraÃ§Ã£o para pickups de vida."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    red = (220, 60, 80, 255)
    dark = (150, 30, 50, 255)
    # Dois cÃ­rculos no topo
    r = width // 4
    d.ellipse([2, 2, 2 + 2 * r, 2 + 2 * r], fill=red, outline=dark)
    d.ellipse([width - 2 - 2 * r, 2, width - 2, 2 + 2 * r], fill=red, outline=dark)
    # TriÃ¢ngulo inferior
    top_y = r + 3
    d.polygon([(2, top_y), (width - 2, top_y), (width // 2, height - 2)], fill=red, outline=dark)
    # Brilho
    d.ellipse([4, 4, 6, 6], fill=(255, 200, 210, 160))
    return arcade.Texture(name=f"heart_{width}x{height}", image=img)


def make_chest_texture(width: int = 28, height: int = 22) -> arcade.Texture:
    """Cria textura de baÃº com detalhes metÃ¡licos."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    wood = (150, 100, 60, 255)
    dark = (100, 70, 40, 255)
    metal = (210, 190, 110, 255)
    d.rectangle([1, 4, width - 2, height - 2], fill=wood, outline=dark)
    # Arcos
    d.rectangle([1, height // 2, width - 2, height - 2], outline=dark)
    # Faixas metÃ¡licas
    d.rectangle([width // 2 - 2, 4, width // 2 + 2, height - 2], fill=metal)
    d.rectangle([1, 8, width - 2, 10], fill=metal)
    # Fecho
    d.rectangle([width // 2 - 3, height // 2 + 2, width // 2 + 3, height // 2 + 8], fill=dark)
    return arcade.Texture(name=f"chest_{width}x{height}", image=img)


def make_cloud_texture(width: int = 180, height: int = 90, alpha: int = 235) -> arcade.Texture:
    """Gera uma textura de nuvem fofa usando elipses sobrepostas.

    - width/height: dimensÃµes do sprite
    - alpha: transparÃªncia do branco da nuvem
    """
    width = max(60, int(width))
    height = max(30, int(height))
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    base_white = (255, 255, 255, alpha)
    shade = (220, 230, 255, max(80, min(180, alpha - 40)))

    # Montinhos principais (quatro bolhas)
    h = height
    w = width
    bumps = [
        (int(w * 0.15), int(h * 0.45), int(w * 0.45), int(h * 0.95)),
        (int(w * 0.35), int(h * 0.25), int(w * 0.70), int(h * 0.95)),
        (int(w * 0.60), int(h * 0.40), int(w * 0.90), int(h * 0.95)),
        (int(w * 0.05), int(h * 0.55), int(w * 0.95), int(h * 0.98)),  # base alongada
    ]
    for i, (x0, y0, x1, y1) in enumerate(bumps):
        d.ellipse([x0, y0, x1, y1], fill=base_white)

    # Sombra inferior muito sutil
    d.rounded_rectangle([int(w * 0.05), int(h * 0.62), int(w * 0.95), int(h * 0.96)], radius=12, fill=shade)

    return arcade.Texture(name=f"cloud_{width}x{height}", image=img)








def make_wolf_textures(base=(190, 190, 200, 255)):
    """Lobo quadrúpede com animação de corrida simples."""
    w, h = 48, 28
    dark = (120, 120, 130, 255)
    nose = (90, 90, 100, 255)
    eye = (30, 30, 40, 255)

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        offset = [0, 2, 0, -2][phase % 4]
        body_y = 12
        # corpo
        d.rectangle([6, body_y, 36, body_y + 10], fill=base, outline=dark)
        # patas traseiras/diant. com leve animação
        leg_shift = [2, 0, -2, 0][phase % 4]
        d.rectangle([8, 4 + offset, 12, 12 + offset], fill=base, outline=dark)
        d.rectangle([30, 4 - offset, 34, 12 - offset], fill=base, outline=dark)
        d.rectangle([12, 0 + leg_shift, 16, 8 + leg_shift], fill=base, outline=dark)
        d.rectangle([26, 0 - leg_shift, 30, 8 - leg_shift], fill=base, outline=dark)
        # cabeça e focinho
        d.rectangle([36, body_y + 2, 44, body_y + 8], fill=base, outline=dark)
        d.polygon([(44, body_y + 3), (47, body_y + 4), (44, body_y + 7)], fill=base, outline=dark)
        d.rectangle([40, body_y + 5, 41, body_y + 6], fill=eye)
        d.rectangle([46, body_y + 6, 47, body_y + 7], fill=nose)
        # cauda
        d.polygon([(6, body_y + 7), (2, body_y + 10), (6, body_y + 9)], fill=base, outline=dark)
        return img

    walk = [frame(i) for i in range(4)]

    def tint(img, a=70):
        overlay = Image.new("RGBA", img.size, (255, 255, 255, a))
        return Image.alpha_composite(img, overlay)

    hurt = [tint(walk[1]), tint(walk[2])]

    def fade(img, alpha):
        faded = img.copy()
        faded.putalpha(alpha)
        return faded

    die = [fade(walk[0], 200), fade(walk[0], 120), fade(walk[0], 40)]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    return {
        "walk_right": [tex("wolf_wr0", walk[0]), tex("wolf_wr1", walk[1]), tex("wolf_wr2", walk[2]), tex("wolf_wr3", walk[3])],
        "walk_left": [tex("wolf_wl0", mirror(walk[0])), tex("wolf_wl1", mirror(walk[1])), tex("wolf_wl2", mirror(walk[2])), tex("wolf_wl3", mirror(walk[3]))],
        "hurt_right": [tex("wolf_hr0", hurt[0]), tex("wolf_hr1", hurt[1])],
        "hurt_left": [tex("wolf_hl0", mirror(hurt[0])), tex("wolf_hl1", mirror(hurt[1]))],
        "die_right": [tex("wolf_dr0", die[0]), tex("wolf_dr1", die[1]), tex("wolf_dr2", die[2])],
        "die_left": [tex("wolf_dl0", mirror(die[0])), tex("wolf_dl1", mirror(die[1])), tex("wolf_dl2", mirror(die[2]))],
    }



def make_skeleton_warrior_textures(base=(200, 200, 210, 255)):
    """Esqueleto com maça em postura de marcha."""
    w, h = 44, 56
    dark = (140, 140, 160, 255)
    bone = base
    mace_head = (160, 160, 170, 255)
    mace_spike = (200, 200, 210, 255)

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        sway = [0, 2, 0, -2][phase % 4]
        step = [2, 0, -2, 0][phase % 4]
        # pernas
        d.rectangle([16, 6, 20, 20 + step], fill=bone, outline=dark)
        d.rectangle([24, 6, 28, 20 - step], fill=bone, outline=dark)
        # cintura e costelas
        d.rectangle([14, 20, 30, 32], outline=dark, fill=None)
        for y in range(22, 31, 4):
            d.line([15, y, 29, y], fill=bone, width=1)
        # coluna
        d.line([22, 6, 22, 20], fill=bone, width=2)
        d.line([22, 32, 22, 46], fill=bone, width=2)
        # braços (direito segurando maça)
        d.line([30, 32, 36 + sway, 44], fill=bone, width=3)
        d.line([14, 32, 8 + sway, 44], fill=bone, width=3)
        # cabeça
        d.ellipse([16, 46, 28, 54], outline=dark, fill=bone)
        d.rectangle([18, 48, 19, 49], fill=(20, 20, 25, 255))
        d.rectangle([25, 48, 26, 49], fill=(20, 20, 25, 255))
        d.rectangle([20, 46, 24, 47], fill=(20, 20, 25, 255))
        # maça
        shaft_x = 36 + sway
        d.rectangle([shaft_x - 1, 30, shaft_x + 1, 44], fill=bone)
        d.ellipse([shaft_x - 5, 26, shaft_x + 5, 36], fill=mace_head, outline=dark)
        d.point((shaft_x - 3, 32), fill=mace_spike)
        d.point((shaft_x + 3, 32), fill=mace_spike)
        d.point((shaft_x, 26), fill=mace_spike)
        d.point((shaft_x, 36), fill=mace_spike)
        return img

    walk = [frame(i) for i in range(4)]

    def tint(img, a=80):
        overlay = Image.new("RGBA", img.size, (255, 255, 255, a))
        return Image.alpha_composite(img, overlay)

    hurt = [tint(walk[1]), tint(walk[2])]

    def crumble(img, scale):
        w, h = img.size
        tmp = img.resize((int(w * scale), int(h * scale)), Image.NEAREST)
        pad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        pad.paste(tmp, ((w - tmp.width) // 2, (h - tmp.height) // 2))
        return pad

    die = [crumble(walk[0], 0.85), crumble(walk[0], 0.6), crumble(walk[0], 0.35)]

    def tex(name, img):
        return arcade.Texture(name=name, image=ImageOps.flip(img))

    def mirror(img):
        return ImageOps.mirror(img)

    return {
        "walk_right": [tex("sk_wr0", walk[0]), tex("sk_wr1", walk[1]), tex("sk_wr2", walk[2]), tex("sk_wr3", walk[3])],
        "walk_left": [tex("sk_wl0", mirror(walk[0])), tex("sk_wl1", mirror(walk[1])), tex("sk_wl2", mirror(walk[2])), tex("sk_wl3", mirror(walk[3]))],
        "hurt_right": [tex("sk_hr0", hurt[0]), tex("sk_hr1", hurt[1])],
        "hurt_left": [tex("sk_hl0", mirror(hurt[0])), tex("sk_hl1", mirror(hurt[1]))],
        "die_right": [tex("sk_dr0", die[0]), tex("sk_dr1", die[1]), tex("sk_dr2", die[2])],
        "die_left": [tex("sk_dl0", mirror(die[0])), tex("sk_dl1", mirror(die[1])), tex("sk_dl2", mirror(die[2]))],
    }
