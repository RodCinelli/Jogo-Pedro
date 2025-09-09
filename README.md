# Warrior Platform — Dossiê do Jogo

Bem-vindo ao Warrior Platform, um platformer 2D com combate simples, IA variada de inimigos, clima dinâmico e pontuação persistida. Este README reúne tudo: instalação, controles, HUD, mecânicas, inimigos, itens, pontuação, clima, resolução e como ajustar parâmetros do jogo.


## Sumário
- Visão Geral
- Instalação e Execução
- Controles
- HUD (Interface)
- Mecânicas do Jogador
- Itens e Power‑ups
- Inimigos (HP, dano, padrões)
 - UI dos Inimigos (Nome e Barra de Vida)
- Pontuação e Condições de Fim
- Clima e Efeitos Visuais
- Áudio e Arte
- Persistência (Placares e Banco)
- Resolução e Dimensionamento
 - Otimizações de Performance
- Parâmetros e Ajustes (onde editar)


## Visão Geral
- Objetivo: derrotar todos os inimigos antes que o tempo acabe, preservando sua vida. Colete corações e pegue a Super Espada para dobrar seu dano.
- Mundo: terreno com plataformas centrais e escadarias, spawns de inimigos no chão e andares, e um baú no topo com upgrade de espada.
- Estilo: pixels gerados por código (sprites), clima dinâmico e efeitos simples que deixam a tela viva e legível.


## Instalação e Execução
Requisitos (Python 3.9+ recomendado):
- arcade
- pillow (PIL)

Instale as dependências:
- pip: `pip install arcade pillow`

Para executar:
- Windows/macOS/Linux: `python game.py`

Observações:
- O jogo inicia em tela cheia automaticamente.
- O arquivo de banco `warrior_platform.db` é criado no diretório do projeto na primeira execução.


## Controles
- Setas Esquerda/Direita: mover
- Seta para Cima: pular
- Barra de Espaço: atacar
- ENTER: iniciar na tela de título; confirmar/retornar em telas finais
- BACKSPACE: apagar caractere no campo de nome
- ESC: sair do jogo


## HUD (Interface)
- Corações (topo esquerdo): medem sua vida. Suporta meio coração (vida é fracionária).
- Score (topo esquerdo): +100 por inimigo derrotado.
- Timer (topo direito): 05:00 no início; se zerar com inimigos vivos, é derrota.
- Banner de upgrade: aparece por ~3s ao pegar a Super Espada.


## Mecânicas do Jogador
- Vida máxima: 5 corações (meio coração possível).
- Movimentação: velocidade 4.0; pulo 12.0; gravidade 0.6.
- Ataque:
  - Dano base: 1 (2 com Super Espada).
  - Duração: 0.36s; janela ativa de acerto entre ~0.12s e ~0.28s.
  - Hitbox do ataque é deslocada à frente do guerreiro (direção atual) e levemente acima do pé.
- Dano recebido e invulnerabilidade:
  - Ao receber dano por contato, aplica knockback horizontal e invulnerabilidade por 1.0s.

Referências no código:
- Constantes: `game.py:31` (SCREEN_*, velocidades, gravidade, ataque, vida, invulnerabilidade)


## Itens e Power‑ups
- Coração (cura 1.0): chance de queda 30% ao abater inimigos.
- Baú da Super Espada: no topo das plataformas. Ao coletar:
  - Dano do ataque dobra (de 1 para 2).
  - Efeito visual “sword glow” e banner informativo.

Referências no código:
- Queda de coração: `game.py:665–671` (drop 30%)
- Baú e efeito: `game.py:294–306` (posicionamento) e `game.py:830–857` (efeitos e banner)


## Inimigos (HP, dano, padrões)
Todos os inimigos dão +100 pontos ao morrer e podem derrubar coração (30%).

- Slime
  - HP: 3
  - Dano de contato: 0.5
  - Velocidade: 1.4
  - Padrão: anda pra frente e pra trás em um corredor (ping‑pong).
- Goblin
  - HP: 3
  - Dano de contato: 1.0
  - Velocidade: 2.2
  - Padrão: anda (ping‑pong) em plataformas dos andares.
- Orc
  - HP: 4
  - Dano de contato: 1.5
  - Velocidade: 1.6
  - Padrão: anda (ping‑pong), mais lento e mais resistente.
- Bat
  - HP: 2
  - Dano de contato: 1.0
  - Velocidade base: 2.6 (um pouco mais rápido que goblin)
  - Voo normal: trajetória em onda (amplitude moderada) ao redor da altura inicial.
  - Rasante (ataque mergulhando):
    - Ativa quando o jogador está no ar, próximo horizontalmente (< ~240 px), e o bat está acima.
    - Persegue o jogador DURANTE o rasante (horizontal + altura), mas interrompe imediatamente se o jogador tocar o chão (nunca persegue no solo).
    - Duração máxima do rasante ~1.2s; ao finalizar entra em recarga (~2.5s).
    - Colisão durante rasante: se descer e colidir com plataformas, “encosta” no topo e encerra o rasante (não atravessa plataformas).
    - Cooldown inicial ao spawn para evitar rasante imediato.

Referências no código:
- Spawns e atributos: `game.py:320–420`
- IA e animação: `game.py:657–740` (inclui rasante, colisões e recargas)

## UI dos Inimigos (Nome e Barra de Vida)
- Nome sempre visível sobre cada inimigo, com cor temática do tipo:
  - Slime: verde (80, 200, 120)
  - Goblin: verde (60, 170, 90)
  - Orc: vermelho (200, 70, 70)
  - Bat: roxo (150, 100, 200)
- Barra de vida: só aparece após o inimigo sofrer dano pela primeira vez; antes disso, apenas o nome é mostrado.
- Performance: rótulos de texto são pré-criados no momento do spawn e apenas reposicionados a cada frame.

Referências no código:
- Criação dos rótulos: `game.py` (funções `spawn_*` dos inimigos)
- Desenho/condição da barra: `game.py` (bloco de desenho dos inimigos em `on_draw`)


## Pontuação e Condições de Fim
- +100 pontos por inimigo derrotado (após animação de morte/desaparecer).
- Vitória: quando não há mais inimigos.
- Derrota: quando vida zera ou quando o tempo chega a 0 com inimigos restantes.
- Telas finais: mostram overlay com Top 5 pontuações e instrução para voltar.

Referências no código:
- Fim de jogo e placar: `game.py:872–984`


## Clima e Efeitos Visuais
- Climas possíveis: dia ensolarado, dia nublado, dia chuvoso, noite limpa, noite nublada, noite chuvosa.
- Nuvens: densidade/alpha variam por clima.
- Chuva: gotas com vento e relâmpagos ocasionais com “flash” na tela.

Referências no código:
- Geração de céu/clima: `game.py:151–232`, `game.py:860–922`


## Áudio e Arte
- Sons: gerados proceduralmente (ataque, dano, pegar item, power‑up, vitória, game over) via Pyglet.
- Sprites: gerados por código com PIL (guerreiro, slimes, goblins, orcs, bats, coração, baú, efeitos, clima).

Referências no código:
- SFX: `game.py:992–1160`
- Sprites e texturas: `assets/sprites.py`


## Persistência (Placares e Banco)
- Banco SQLite em `warrior_platform.db` (diretório do projeto).
  - Tabelas: `players(name)` e `scores(player_name, score, created_at)`.
  - Salvamento automático do score ao finalizar uma partida (vitória/derrota).
  - Top 5 exibido na tela final (maior score por jogador).
- Fallback adicional: `scores.txt` (anexa `nome;score`).

Referências no código:
- Banco e scores: `game.py:101–110`, `game.py:1049–1150`


## Resolução e Dimensionamento
- Tela cheia: o jogo usa sempre o tamanho real da janela/monitor.
- Título e gameplay centralizados com `self.width/self.height`.
- Mundo (chão/plataformas/baú) é ancorado ao centro horizontal da janela; o HUD usa as dimensões atuais para se posicionar.
- Sem letterboxing: a área útil se adapta a 1080p, 2K, 4K e diferentes proporções.

## Otimizações de Performance
- Título: textos cacheados e atualizados sem recriação por frame (`_ensure_title_ui`).
- Telas finais (vitória/game over): textos cacheados e recriados apenas quando scores, estado ou tamanho mudam (`_ensure_end_ui`).
- Banner de upgrade: textos cacheados por conteúdo/tamanho e só atualiza transparência no draw (`_ensure_banner_ui`).
- Nomes dos inimigos: criados no spawn e apenas reposicionados; barra de vida só aparece após o primeiro dano (menos draw e melhor legibilidade).
- Resultado: sem alocação de `arcade.Text` por frame nas telas e elementos citados, mantendo FPS alto.


## Parâmetros e Ajustes (onde editar)
Edite em `game.py` (topo do arquivo) para ajustar comportamentos:
- Velocidades: `PLAYER_MOVE_SPEED`, `PLAYER_JUMP_SPEED`, `SLIME_SPEED`, `GOBLIN_SPEED`, `ORC_SPEED`, `BAT_SPEED`.
- Física/Combate: `GRAVITY`, `ATTACK_DURATION`, `ATTACK_HIT_START`, `ATTACK_HIT_END`, `PLAYER_MAX_HP`, `PLAYER_INVULN`.
- IA do Bat: tempo de mergulho/cooldown na seção de atualização dos inimigos (`on_update`).
- Layout: larguras e posições de plataformas são derivadas de `self.width` e de parâmetros como `stair_tex_w`, `dx_base`.

Dica: para uma experiência “mais difícil”, aumentar ligeiramente `BAT_SPEED` ou reduzir `dive_cooldown` intensifica os rasantes. Para “mais leve”, faça o oposto.


## Créditos e Licença
- Código e assets gerados por script no próprio projeto.
- Dependências: Arcade, Pillow, Pyglet.
- Sob os direitos de Rodrigo Cinelli.
