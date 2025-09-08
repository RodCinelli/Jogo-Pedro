import random
import arcade
from PIL import Image, ImageDraw, ImageOps


def _outline(d: ImageDraw.ImageDraw, rect, color=(20, 20, 28, 255)):
    x0, y0, x1, y1 = rect
    d.rectangle([x0, y0, x1, y1], outline=color)


def make_warrior_textures():
    """Warrior com machado, pixel-art simples com mais detalhes e animações."""
    w, h = 48, 64
    armor = (72, 120, 220, 255)
    armor_dark = (52, 90, 170, 255)
    skin = (234, 200, 170, 255)
    boot = (60, 40, 30, 255)
    axe_handle = (140, 90, 30, 255)
    axe_head = (210, 210, 220, 255)

    def frame(leg_phase: int, arm_pose: str):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        # Bota/canela
        d.rectangle([16, 12, 22, 18], fill=boot)
        d.rectangle([26, 12, 32, 18], fill=boot)
        # Pernas (levemente alternadas)
        if leg_phase in (0, 2):
            d.rectangle([16, 18, 22, 28], fill=armor_dark)
            d.rectangle([26, 18, 32, 26], fill=armor_dark)
        else:
            d.rectangle([16, 18, 22, 26], fill=armor_dark)
            d.rectangle([26, 18, 32, 28], fill=armor_dark)

        # Tronco/peitoral
        d.rectangle([14, 28, 34, 46], fill=armor)
        _outline(d, [14, 28, 34, 46])
        # Ombreiras
        d.rectangle([12, 44, 18, 50], fill=armor_dark)
        d.rectangle([30, 44, 36, 50], fill=armor_dark)

        # Cabeça/Elmo simples
        d.rectangle([18, 46, 30, 58], fill=skin)
        d.rectangle([16, 56, 32, 60], fill=armor_dark)
        _outline(d, [18, 46, 30, 58])

        # Braço e Machado (posições mais ricas)
        if arm_pose == "down":
            d.rectangle([32, 38, 34, 50], fill=axe_handle)
            d.rectangle([34, 46, 44, 53], fill=axe_head)
        elif arm_pose == "mid":
            d.rectangle([32, 44, 34, 56], fill=axe_handle)
            d.rectangle([26, 54, 34, 60], fill=axe_head)
        elif arm_pose == "up":
            d.rectangle([28, 50, 30, 62], fill=axe_handle)
            d.rectangle([20, 58, 30, 62], fill=axe_head)
        elif arm_pose == "wind":  # preparação do golpe
            d.rectangle([30, 42, 32, 58], fill=axe_handle)
            d.rectangle([22, 56, 30, 62], fill=axe_head)
        elif arm_pose == "swing":  # golpe atravessando
            d.rectangle([22, 40, 34, 44], fill=axe_handle)
            d.rectangle([34, 36, 44, 44], fill=axe_head)
        elif arm_pose == "follow":  # final do golpe, para baixo
            d.rectangle([30, 28, 32, 42], fill=axe_handle)
            d.rectangle([30, 26, 40, 32], fill=axe_head)

        # Cinto detalhe
        d.rectangle([14, 36, 34, 38], fill=(40, 30, 20, 255))

        return img

    # Animações: idle (respiro), run (4 frames), attack (5 frames com machado)
    idle = [frame(0, "down"), frame(2, "down")]
    run = [frame(0, "down"), frame(1, "mid"), frame(2, "down"), frame(3, "mid")]
    attack = [
        frame(0, "wind"),  # preparação
        frame(1, "up"),    # machado no alto
        frame(2, "swing"), # golpe atravessando
        frame(3, "follow"),# seguimento
        frame(0, "down"),  # recuperação
    ]

    def tex(name, img):
        # Corrige orientação vertical (PIL usa origem no topo)
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


def make_ground_texture(width: int, height: int) -> arcade.Texture:
    """Gera textura do chão com grama e terra com ruído simples."""
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
    # Lâminas de grama
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
    # Tábuas verticais
    plank_w = 28
    for x in range(0, width, plank_w):
        d.line([x, 0, x, height], fill=dark)
        # nós da madeira
        for _ in range(2):
            px = x + random.randint(6, plank_w - 6)
            py = random.randint(4, height - 6)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], outline=dark, fill=light)
    # Borda superior
    d.rectangle([0, height - 3, width, height], fill=light)

    return arcade.Texture(name=f"plat_{width}x{height}", image=img)


def make_slime_textures(base=(80, 200, 120, 255)):
    """Cria texturas de slime (walk/hurt/die) com frames básicos."""
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
    # Hurt: versão mais clara
    def tint(img, a=80):
        c = Image.new("RGBA", img.size, (255, 255, 255, a))
        return Image.alpha_composite(img, c)
    hurt = [tint(walk[1]), tint(walk[2])]
    # Die: encolhe em três passos
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
        # Cabeça/orelhas
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

    Mantém o mesmo conjunto de chaves do slime para reaproveitar lógica.
    """
    w, h = 36, 42

    body = base
    dark = (30, 90, 50, 255)
    eye = (20, 20, 20, 255)
    belt = (80, 60, 30, 255)

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Pernas alternadas
        leg_shift = [0, 2, 0, 2][phase % 4]
        d.rectangle([10, 2, 14, 10 + leg_shift], fill=dark)
        d.rectangle([22, 2, 26, 10 + (2 - leg_shift)], fill=dark)
        # Tronco
        d.rectangle([8, 10, 28, 28], fill=body, outline=dark)
        # Cinto
        d.rectangle([8, 16, 28, 18], fill=belt)
        # Cabeça com orelhas
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


def make_orc_textures(base=(200, 70, 70, 255)):
    """Texturas de um orc vermelho que anda (walk/hurt/die).

    Usa o mesmo conjunto de chaves dos walkers para encaixar na lógica atual.
    """
    w, h = 40, 48
    body = base
    dark = (120, 40, 40, 255)
    eye = (15, 15, 15, 255)
    belt = (90, 70, 40, 255)

    def frame(phase: int):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Pernas alternadas
        leg_shift = [0, 2, 0, 2][phase % 4]
        d.rectangle([12, 2, 16, 12 + leg_shift], fill=dark)
        d.rectangle([24, 2, 28, 12 + (2 - leg_shift)], fill=dark)
        # Tronco robusto
        d.rectangle([8, 12, 32, 32], fill=body, outline=dark)
        # Cinto
        d.rectangle([8, 20, 32, 22], fill=belt)
        # Ombreiras escuras
        d.rectangle([6, 32, 12, 36], fill=dark)
        d.rectangle([28, 32, 34, 36], fill=dark)
        # Cabeça com presas
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
    """Cria textura de coração para pickups de vida."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    red = (220, 60, 80, 255)
    dark = (150, 30, 50, 255)
    # Dois círculos no topo
    r = width // 4
    d.ellipse([2, 2, 2 + 2 * r, 2 + 2 * r], fill=red, outline=dark)
    d.ellipse([width - 2 - 2 * r, 2, width - 2, 2 + 2 * r], fill=red, outline=dark)
    # Triângulo inferior
    top_y = r + 3
    d.polygon([(2, top_y), (width - 2, top_y), (width // 2, height - 2)], fill=red, outline=dark)
    # Brilho
    d.ellipse([4, 4, 6, 6], fill=(255, 200, 210, 160))
    return arcade.Texture(name=f"heart_{width}x{height}", image=img)


def make_chest_texture(width: int = 28, height: int = 22) -> arcade.Texture:
    """Cria textura de baú com detalhes metálicos."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    wood = (150, 100, 60, 255)
    dark = (100, 70, 40, 255)
    metal = (210, 190, 110, 255)
    d.rectangle([1, 4, width - 2, height - 2], fill=wood, outline=dark)
    # Arcos
    d.rectangle([1, height // 2, width - 2, height - 2], outline=dark)
    # Faixas metálicas
    d.rectangle([width // 2 - 2, 4, width // 2 + 2, height - 2], fill=metal)
    d.rectangle([1, 8, width - 2, 10], fill=metal)
    # Fecho
    d.rectangle([width // 2 - 3, height // 2 + 2, width // 2 + 3, height // 2 + 8], fill=dark)
    return arcade.Texture(name=f"chest_{width}x{height}", image=img)


def make_cloud_texture(width: int = 180, height: int = 90, alpha: int = 235) -> arcade.Texture:
    """Gera uma textura de nuvem fofa usando elipses sobrepostas.

    - width/height: dimensões do sprite
    - alpha: transparência do branco da nuvem
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
