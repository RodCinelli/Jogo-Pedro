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
 - Build com auto‑py‑to‑exe (Windows)
 - Erros comuns no executável (OpenGL/Arcade)
 - Publicar no GitHub Releases


## Visão Geral
- Objetivo: derrotar todos os inimigos antes que o tempo acabe, preservando sua vida. Colete corações e pegue a Super Espada para dobrar seu dano.
- Mundo: terreno com plataformas centrais e escadarias, spawns de inimigos no chão e andares, e um baú no topo com upgrade de espada. O trecho final agora possui duas plataformas nevadas: uma dupla estreita (quinta plataforma) pensada como degrau de acesso e uma arena larga (sexta plataforma) onde enfrentamos os Skeleton Warriors.
- Plataformas tematizadas: o andar dos goblins recebe um matiz esverdeado (heras), o dos trolls fica alaranjado (vegetação árida) e o dos orcs ganha manchas vermelhas lembrando sangue; acima deles a escadaria nevada conduz ao topo.
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
- Coração (cura 1.0): chance de queda 25% ao abater inimigos.
- Baú da Super Espada: no topo das plataformas. Ao coletar:
  - Dano do ataque dobra (de 1 para 2).
  - Efeito visual “sword glow” e banner informativo.

Referências no código:
- Queda de coração: `game.py:775–783` (drop 25%)
- Baú e efeito: `game.py:294–306` (posicionamento) e `game.py:830–857` (efeitos e banner)


## Inimigos (HP, dano, padrões)
Todos os inimigos dão +100 pontos ao morrer e podem derrubar coração (25%).

- Slime
  - HP: 3
  - Dano de contato: 0.5
  - Velocidade: 1.5
  - Padrão: anda pra frente e pra trás em um corredor (ping‑pong).
- Goblin
  - HP: 3
  - Dano de contato: 1.0
  - Velocidade: 2.0
  - Padrão: anda (ping‑pong) em plataformas dos andares.
- Troll
  - HP: 4
  - Dano de contato: 1.0
  - Velocidade: 1.8
  - Padrão: anda (ping‑pong) nas plataformas superiores; substitui os goblins das pontas do segundo andar e exibe pele alaranjada.
- Orc
  - HP: 5
  - Dano de contato: 1.5
  - Velocidade: 1.5
  - Padrão: anda (ping‑pong), mais lento e mais resistente.
- Skeleton Warrior
  - HP: 4
  - Dano de contato: 1.0
  - Velocidade: 1.7
  - Padrão: patrulha a sexta plataforma nevada com escudo e maça, exigindo duelos corpo a corpo mais técnicos no topo.
- Bat
  - HP: 2
  - Dano de contato: 1.0
  - Velocidade base: 2.5 (um pouco mais rápida que os walkers)
  - Voo normal: trajetória em onda (amplitude moderada) ao redor da altura inicial.
  - Rasante (ataque mergulhando):
    - Ativa quando o jogador está no ar, próximo horizontalmente (< ~240 px), e o bat está acima.
    - Persegue o jogador DURANTE o rasante (horizontal + altura), mas interrompe imediatamente se o jogador tocar o chão (nunca persegue no solo).
    - Duração máxima do rasante ~1.2s; ao finalizar entra em recarga (~2.5s).
    - Colisão durante rasante: se descer e colidir com plataformas, “encosta” no topo e encerra o rasante (não atravessa plataformas).
    - Cooldown inicial ao spawn para evitar rasante imediato.

Referências no código:
- Spawns e atributos: `game.py:320–620`
- IA e animação: `game.py:657–804` (inclui rasante, colisões e recargas)

## UI dos Inimigos (Nome e Barra de Vida)
- Nome sempre visível sobre cada inimigo, com cor temática do tipo:
  - Slime: verde (80, 200, 120)
  - Goblin: verde (60, 170, 90)
  - Troll: laranja (230, 140, 70)
  - Orc: vermelho (200, 70, 70)
  - Skeleton Warrior: prata (190, 190, 200)
  - Bat: roxo (150, 100, 200)
- Barra de vida: só aparece após o inimigo sofrer dano pela primeira vez; antes disso, apenas o nome é mostrado.
- Performance: rótulos de texto são pré-criados no momento do spawn e apenas reposicionados a cada frame.

Referências no código:
- Criação dos rótulos: `game.py` (funções `spawn_*` dos inimigos)
- Layout das plataformas superiores (quinta escada nevada e arena sexta): `game.py:334–368`
- Desenho/condição da barra: `game.py` (bloco de desenho dos inimigos em `on_draw`)


## Pontuação e Condições de Fim
- +100 pontos por inimigo derrotado (após animação de morte/desaparecer).
- Vitória: quando não há mais inimigos.
- Derrota: quando vida zera ou quando o tempo chega a 0 com inimigos restantes.
- Telas finais: mostram overlay com Top 5 pontuações e instrução para voltar.

Referências no código:
- Fim de jogo e placar: `game.py:872–984`


## Clima e Efeitos Visuais
- Plataformas com tonalização temática: verde para o nível dos goblins, laranja árido para os trolls e vermelho marcante para os orcs, mantendo o patamar do baú com a madeira clássica.
- Climas possíveis: dia ensolarado, dia nublado, dia chuvoso, noite limpa, noite nublada, noite chuvosa.
- Nuvens: densidade/alpha variam por clima.
- Chuva: gotas com vento e relâmpagos ocasionais com “flash” na tela.

Referências no código:
- Geração de céu/clima: `game.py:151–232`, `game.py:860–922`


## Áudio e Arte
- Sons: gerados proceduralmente (ataque, dano, pegar item, power‑up, vitória, game over) via Pyglet.
- Sprites: gerados por código com PIL (guerreiro, slimes, goblins, trolls, orcs, bats, coração, baú, efeitos, clima).

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


## Build com auto‑py‑to‑exe (Windows)
Passo a passo para gerar o executável e empacotar em ZIP.

- Instalar GUI: `pip install auto-py-to-exe`
- Abrir: `auto-py-to-exe`

Campos principais
- Script location: selecione `game.py`.
- Onefile/Onedir:
  - Recomendado: Onedir (pasta). Abre mais rápido e evita overhead do “unpack” do onefile.
  - Alternativa: Onefile (um único .exe). Mais prático, porém inicia mais lento.
- Console window: Window Based (`--noconsole`) para não abrir console.
- Icon: opcional (`.ico`).
- Output directory: pasta de saída (ex.: `dist/`).

Advanced (importante)
- Hidden Imports (adicione todos):
  - `arcade.gl`
  - `arcade.gl.backends`
  - `arcade.gl.backends.opengl`
  - `arcade.gl.backends.pyglet`
  - `assets.sprites`
- Additional command line arguments:
  - `--collect-submodules arcade.gl.backends --collect-submodules pyglet`
- Additional Files:
  - Não é necessário (sprites e sons são gerados por código). Se quiser incluir `README.md`, adicione aqui.

Build
- Clique em “Convert .py to .exe”.
- Saída típica:
  - Onedir: `dist/WarriorPlatform/` contendo `.exe` + DLLs.
  - Onefile: `dist/WarriorPlatform.exe`.

Observações específicas deste jogo
- Banco/arquivos gravados: `warrior_platform.db` e `scores.txt` são criados no diretório atual (`os.getcwd()`). Distribua o `.zip` para que o jogador extraia e rode em uma pasta com permissão de escrita (ex.: `Documentos/Jogos/WarriorPlatform`), não em “Arquivos de Programas”.
- Fullscreen: inicia em tela cheia; UI e mundo centralizam de acordo com a resolução do monitor.
- Dependências: Arcade/Pyglet/Pillow são empacotados automaticamente; não há pastas de assets externas.

Empacotar em ZIP para hospedagem
- Onedir (recomendado):
  - Entre em `dist/WarriorPlatform/` e compacte TODO o conteúdo (os arquivos precisam ficar no topo após extração).
  - Ex.: `WarriorPlatform-win64.zip`.
- Onefile:
  - Opcional compactar apenas o `.exe` (ou publicar direto).

Hospedar o ZIP
- Itch.io (recomendado): crie a página e faça upload do ZIP. Para updates rápidos: `butler push WarriorPlatform-win64.zip usuario/jogo:windows`.
- GitHub Releases: crie um release e anexe o ZIP.
- Qualquer site estático: faça upload do ZIP e adicione um botão de download.

Testar antes de publicar
- Execute em uma máquina “limpa” (VM):
  - Abre em fullscreen
  - Cria/atualiza `warrior_platform.db` e `scores.txt` sem erro
  - Áudio e inputs funcionam
- Se notar que `assets` não foi incluído:
  - Confirme o argumento `--hidden-import assets.sprites`.
  - Alternativa robusta: adicionar um arquivo vazio `assets/__init__.py` ao projeto.

Dicas úteis
- Nome do executável: em “Name of Application”, defina `WarriorPlatform`.
- Assinatura opcional: assinar o `.exe` reduz avisos do SmartScreen (Windows).
- Onefile vs Onedir: para jogadores menos técnicos, Onefile pode ser mais conveniente; para desempenho/arranque, prefira Onedir.


## Erros comuns no executável (OpenGL/Arcade)
Se ver mensagens como “arcade.gl Backend Provider 'opengl' not found” ou “No module named 'arcade.gl.backends'”, o empacotador não incluiu os submódulos dinâmicos do Arcade.

Como corrigir (auto‑py‑to‑exe)
- Hidden imports (obrigatório): adicione em “Advanced → Hidden imports”
  - `arcade.gl`, `arcade.gl.backends`, `arcade.gl.backends.opengl`, `arcade.gl.backends.pyglet`, `assets.sprites`
- Additional args (recomendado): em “Advanced → Additional command line arguments”
  - `--collect-submodules arcade.gl.backends --collect-submodules pyglet`
- Modo de saída: prefira Onedir (pasta) em vez de Onefile.
- Reconstrução: apague `build/` e `dist/` antes de reconstruir.

Plano B (forçar provider e ajudar o empacotador)
- Opcional: fixar o provider do Arcade para “pyglet” no topo de `game.py`, antes de `import arcade`:
  - `import os`
  - `os.environ.setdefault("ARCADE_GL_PROVIDER", "pyglet")`
- Ainda mantenha os hidden‑imports acima.

Se continuar dando erro
- Hook dedicado: crie `hook-arcade.gl.backends.py` com:
  - `from PyInstaller.utils.hooks import collect_submodules`
  - `hiddenimports = collect_submodules('arcade.gl.backends')`
  - Em “Additional Hooks Dir”, aponte para a pasta do hook e reconstrua.
- Atualize ferramentas: use PyInstaller ≥ 5.13 e versões recentes de Arcade/Pyglet.
- Ambiente de execução: precisa de GPU/driver com OpenGL 3.3+ (VM/RDP sem aceleração pode falhar). Instale o Microsoft Visual C++ Redistributable, se necessário.

Checklist rápido (costuma resolver)
- Hidden imports: `arcade.gl.backends`, `arcade.gl.backends.opengl`, `arcade.gl.backends.pyglet`
- Additional args: `--collect-submodules arcade.gl.backends`
- Rebuild limpo: apagar `build/` e `dist/`

## Publicar no GitHub Releases
Passo a passo para publicar o ZIP do jogo no seu repositório.

1) Gere o ZIP final
- Onedir: compacte o conteúdo de `dist/WarriorPlatform/` para `WarriorPlatform-win64.zip` (os arquivos precisam ficar na raiz após extração).
- Onefile: compacte o `WarriorPlatform.exe` (opcional) ou publique diretamente o `.exe`.

2) Crie um Release pelo site do GitHub
- Vá em “Releases” → “Draft a new release”.
- Tag: por exemplo `v1.0.0`.
- Título: “Warrior Platform 1.0.0”.
- Arraste o(s) arquivo(s) ZIP para a área “Assets”.
- Opcional: anexe `SHA256SUMS.txt` com o hash do arquivo e um `README-Release.md` com instruções rápidas.
- Clique em “Publish release”.

3) CLI (opcional, com GitHub CLI)
- `gh release create v1.0.0 dist/WarriorPlatform-win64.zip --title "Warrior Platform 1.0.0" --notes "Extract and run WarriorPlatform.exe"`
- Link público prático: `https://github.com/SEU_USUARIO/SEU_REPO/releases/latest`

Boas práticas
- Nomeie por plataforma: `WarriorPlatform-win64.zip`, `WarriorPlatform-macOS.zip` etc.
- Inclua instruções para o jogador: “Extraia e execute `WarriorPlatform.exe` (evite ‘Arquivos de Programas’ por permissões)”.
- Publique também o hash SHA‑256 e, se possível, assine o executável para reduzir alertas do SmartScreen.


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
