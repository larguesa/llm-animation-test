# T2S Tech: AI-Native Delivery Pods (motion graphics, 30 s)

Entregável: `output/final.mp4`, em H.264 1920×1080, 30 fps, com 900 frames e 30,0 s de duração. O áudio é AAC estéreo a 48 kHz. Os valores medidos estão em `output/manifest.json`, em `deliverable.qa`. As contact sheets extraídas do próprio MP4 estão em `output/qa/`.

## Como reproduzir
```
sh src/build.sh      # compõe o áudio, renderiza os 900 frames sob o render.lock, faz o mux e gera QA + manifest
# Prévia rápida de frames avulsos (1 amostra por frame, sem motion blur), gravada em build/preview/:
/home/hermes/.hermes/tool-venvs/crawl4ai/bin/python src/render.py preview 6.5 15.5 29.5
```
Requisitos:
- ffmpeg/ffprobe.
- `python3` com numpy e Pillow, para o áudio e o QA.
- Python com Playwright e o Chromium headless em `/home/hermes/.cache/ms-playwright/chromium-1234/`.

Os passos pesados rodam sob o `render.lock`, em um único processo, com o encoder x264 limitado a 1 thread. Com `NSUB=6`, o render dos 900 frames levou 512 s nesta máquina (`build/build.log`). O resultado é determinístico: sementes fixas no ruído e nas posições e a mesma linha do tempo. A rasterização de fontes pode variar entre versões do Chromium.

## Técnica e decisões
- Cada frame é desenhado por código (Canvas 2D) no Chromium headless.
  - Não há screenshot do site, imagem gerada por IA, banco de imagens nem lettering gerado.
  - Todos os elementos são animados individualmente: cartões, linhas, ícones, textos e logotipo.
- Os textos são tipografia real, com as fontes oficiais do site (`input/fonts`, OFL):
  - Montserrat 700/800 nos títulos, eyebrows e botão, com o tracking negativo do CSS do site.
  - Rubik 400 no texto de apoio.
- O logotipo usa os paths vetoriais de `input/assets/assets__t2s-logo-light.svg`, copiados literalmente para `src/logo.js` e desenhados com Path2D nas cores originais: #00b4e8, #3264ff e #ffffff.
  - A animação escala as 6 pétalas e revela o wordmark por máscara.
  - O estado final tem a geometria exata do arquivo, com cerca de 520 px de largura.
- A identidade visual vem do CSS/HTML congelados:
  - Paleta `:root`: cyan #00b4e8, blue #3264ff, blue-deep #1e46bd, ink-deep #22262b, green, amber e red. Amber e red aparecem apenas como tensão nas demandas.
  - Cores dos `.role-card`: #2454e8, #3264ff, #2b5bec, #2856df e #1e49cc.
  - Fundo do `.hero`, com gradiente a 105° e brilho radial cyan.
  - Grade `.signal-grid` de 46 px em perspectiva (58°/−14°), com drift lento que dá um parallax discreto.
  - Eyebrow #72dfff com tracking de .16em.
  - Marcador de check cyan da `.check-list`, usado nos checkpoints.
  - Botão `.button.primary`, azul com raio de 3 px e seta ↗.
  - Easing inspirado no cubic-bezier(.22,1,.36,1) do site.
- O movimento usa:
  - máscaras de revelação palavra a palavra e antecipação com leve recuo antes dos deslocamentos;
  - overshoot sutil (outBack) e desaceleração quíntica;
  - motion blur por supersampling temporal, com 6 subframes e obturador de 180°, mais grão leve.
- As transições ocorrem por continuidade de forma:
  - demandas → grade → nós em órbita → núcleo;
  - núcleo → 5 cartões de função;
  - cartões → barras → trilho → linha de fluxo;
  - artefatos e nós → 6 pontos → as 6 pétalas do logotipo.
- Especialistas e agentes são representados por formas distintas, sem robôs humanoides:
  - Especialista: disco cyan sólido com halo e silhueta mínima.
  - Agente supervisionado: quadrado azul contornado, com um losango interno.
  - Os dois tipos aparecem juntos em cada função e em cada artefato.

## Roteiro executado (tempos do código)
- 0–5 s: nove cartões de demanda dispersos e oscilando, ligados por dependências tracejadas em amber/red.
  - Demandas: Backlog, Integração, Legado, Novo requisito, Bug em produção, Dependência, Prazo, Aprovação e Infraestrutura.
  - Em 0,45 s entra "Mais horas / não resolvem tudo.".
  - A partir de 2,0 s, os cartões se alinham em grade, um a cada colcheia, acompanhados por um arpejo. O status passa a "priorizado".
- 5–10 s: com antecipação, os cartões viram nós em órbita de um núcleo "RESULTADO". As conexões são desenhadas em 5,9–6,4 s.
  - O drop acontece em 6,0 s.
  - Entram "AI-Native Delivery Pods" e depois "Uma equipe moldada pelo resultado.".
  - A legenda mostra Especialistas e Agentes supervisionados.
- 10–17 s: o núcleo se abre em 5 cartões, e os membros da equipe voam da órbita para dentro deles.
  - Título: "Especialistas + agentes supervisionados".
  - As funções entram uma a cada 2 tempos (10,5 / 11,5 / 12,5 / 13,5 / 14,5 s), cada uma com uma ação visual:
    - Prototyper, explorar ideias: esboços, dos quais um é escolhido.
    - Builder, construir: blocos que empilham.
    - Sweeper, simplificar: um zigue-zague que vira linha e perde nós supérfluos.
    - Grower, evoluir: uma trajetória iterativa ascendente.
    - Maintainer, manter: escudo com pulso estável.
  - Entre as funções, nos pontos de decisão, há 4 "CHECKPOINT HUMANO" (11,15 / 12,15 / 13,15 / 14,15 s). O texto de apoio é "Revisão humana nos pontos de decisão.".
- 16,3–17,6 s: os cartões colapsam em barras, que se fundem em um trilho único.
- 17–24,5 s: fluxo "Contexto → Entrega → Qualidade", com as setas vetoriais desenhadas.
  - Os artefatos Protótipo, Incremento de software, Teste e Revisão percorrem o trilho. Cada um é verificado com um check em Qualidade e desce para "EVIDÊNCIAS DE PROGRESSO".
  - Título: "Progresso visível. / Responsabilidade clara.".
- 23,7–24,5 s: tudo converge em 6 pontos que formam o logotipo, na resolução em 24,5 s.
  - Em 25,0 s entra "AI-Native Delivery Pods", em 25,5 s o botão "Converse com um engenheiro. ↗" e em 26,0 s "t2stech.com".
  - A composição fica estática de cerca de 26,6 s até 30 s, ou seja, mais de 3 s de leitura.

## Áudio e sincronização
A música é original e programática (ver `music-license.md`), a 120 BPM: 1 tempo = 0,5 s = 15 frames.

Pontos de sincronia:
- Cada cartão que se alinha coincide com uma nota do arpejo ascendente.
- Drop, núcleo e título caem juntos com o kick, o prato e o sub em 6,0 s.
- Cada função tem um sino, e cada checkpoint tem um chime de confirmação no instante em que o check é desenhado.
- Cada nó do fluxo tem um sino.
- Cada artefato tem ticks nos nós, um chime de verificação e um "thump" ao pousar.
- Há risers e whooshes nas transições.
- Harmonia: tensão (Eb sobre D) → Dsus2 → Dm9 → … → A7(b9) → resolução em Dmaj9 no logotipo, em 24,5 s. A música sai em fade entre 28,6 e 30 s.

Não há locução, e a mensagem inteira está em texto na tela. Os tempos dos eventos estão em `output/audio_events.json`.

## Textos em tela (PT-BR, nomes do serviço e das funções preservados)
"Mais horas não resolvem tudo." · "T2S TECH · SERVIÇO" · "AI-Native Delivery Pods" · "Uma equipe moldada pelo resultado." · "Especialistas" · "Agentes supervisionados" · "RESULTADO" · "Especialistas + agentes supervisionados" · Prototyper/explorar ideias · Builder/construir · Sweeper/simplificar · Grower/evoluir · Maintainer/manter · "CHECKPOINT HUMANO" · "Revisão humana nos pontos de decisão." · "COMO TRABALHAMOS" · Contexto/entender o que existe · Entrega/incrementos com dono claro · Qualidade/testes, revisão e evidências · Protótipo · Incremento de software · Teste · Revisão · "EVIDÊNCIAS DE PROGRESSO" · "Progresso visível." · "Responsabilidade clara." · "Converse com um engenheiro." · "t2stech.com".

O vídeo não traz clientes, depoimentos, certificações, números de produtividade nem promessa de autonomia total. "01–05" são apenas índices de função, como no site. Os diagramas são conceituais e não representam telas de produto.

## QA realmente feito
- `src/finalize.py` roda ffprobe, faz uma decodificação completa sem erros e mede EBU R128 e o pico. Também gera as contact sheets a partir de `final.mp4` e mede a diferença de pixels do cartão final entre 26,8 s e 29,8 s. Os resultados estão em `manifest.json`.
- A revisão visual foi feita com uma ferramenta de análise de imagem sobre as contact sheets e recortes do primeiro render completo (mesma linha do tempo, 4 subframes) e das prévias. Ela encontrou os problemas abaixo, que foram corrigidos:
  - colisão de cartões durante o alinhamento em cerca de 3,4 s;
  - artefatos cobrindo a legenda de Qualidade;
  - a órbita sobrepondo os cartões na abertura, em cerca de 10,3 s;
  - um ponto residual antes do logotipo.
- Nos frames finais, a mesma ferramenta confirmou a grafia de "AI-Native Delivery Pods", "Converse com um engenheiro.", "t2stech.com", "T2S TECH · SERVIÇO" e das 5 funções, além de mostrar o logotipo completo e nenhum texto cortado pelas bordas.
- Áudio: medi RMS por segundo, zero amostras clipadas e loudness/true peak via ffmpeg.
- Revisão do render definitivo: as duas contact sheets de `output/qa/` (18 frames extraídos do `final.mp4`) foram revisadas com a ferramenta de análise de imagem. Não há texto cortado pelas bordas, frame quebrado ou erro de grafia, e as 5 funções e o cartão final estão completos. Os pontos apontados são estados transitórios das animações: blur de entrada em 0,5 s, cartões em trânsito em 5,3 s, chips em movimento com blur em 22,0 s e logotipo em revelação em 24,8 s.

## Limitações reais
- Não houve revisão humana em tempo real, nem escuta humana. O áudio foi validado por métricas e pela construção dos tempos, e o vídeo por frames amostrados.
- O motion blur é por subframes, não por vetor de velocidade. Em movimentos muito rápidos pode aparecer um leve escalonamento.
- Alguns rótulos secundários são pequenos: status dos cartões com 17 px, "CHECKPOINT HUMANO" com 16 px e eyebrows com 20 px. São legíveis em 1080p, mas ficam pequenos em telas móveis. Os textos principais têm de 34 a 124 px.
- Maintainer fica cerca de 1,8 s em cena antes do colapso. As demais funções ficam mais tempo.
- A copy em PT-BR é uma adaptação da página, que está em inglês. Os subtítulos dos artefatos são conceituais.
- A URL ao vivo responde com redirecionamento HTTP 301 (curl sem seguir redirecionamentos) e não foi navegada nesta rodada. A fonte de verdade foram os arquivos congelados em `./input` (HTML, texto, CSS, logotipos e fontes).
- Os rótulos de status dos cartões (por exemplo, "priorizado") usam a forma masculina genérica, referindo-se ao item, inclusive sob nomes femininos como "Integração". É uma escolha de rótulo, não concordância com o nome do cartão.
