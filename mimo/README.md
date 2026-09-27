# AI-Native Delivery Pods — vídeo motion graphics 30 s (T2S Tech)

Peça promocional em motion graphics, 1920x1080 @ 30 fps, 30,0 s, MP4 (H.264)
com trilha instrumental original em AAC.

Artefato final: `output/final.mp4`

## Reprodução a partir das fontes

```bash
cd /home/hermes/entregas/t2s-pods-model-comparison/runs/mimo/work

# 1) Rasterizar o logotipo oficial (SVG -> PNG com alpha, via Chrome headless)
/home/hermes/.hermes/tool-venvs/crawl4ai/bin/python build/rasterize_logos.py

# 2) Gerar a trilha instrumental original (30 s, 48 kHz estéreo)
python3 build/music.py                       # -> build/music.wav

# 3) Renderizar os 900 frames e codificar o vídeo (1 thread, sob flock)
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  flock /home/hermes/entregas/t2s-pods-model-comparison/render.lock \
  python3 build/render.py --full build/video.mp4

# 4) Mux de áudio -> entrega final
ffmpeg -y -i build/video.mp4 -i build/music.wav \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart output/final.mp4
```

Render isolado de frames para revisão:

```bash
python3 build/render.py --frame 7.2,13.5,20.55,28.5 --out build/test
```

## Estrutura do workspace

- `build/render.py` — renderizador de motion graphics (Pillow + numpy):
  scene-graph com sprites escaláveis/rotacionáveis, easing próprio
  (out3/out5/in2/inout/back), máscaras de revelação por texto (wipe/rise),
  motion blur por superamostragem temporal (2 amostras por frame em
  movimento, 1 no trecho estático final), transições por continuidade de
  forma (cartões -> constelação -> hub -> funções -> fluxo -> logo).
- `build/music.py` — síntese 100% programática da trilha (numpy):
  120 BPM, Lá menor, sub/baixo, arpejos, pads, percussão eletrônica,
  campainha de "checkpoint" sincronizada com os marcos humanos do roteiro,
  whooshes de transição e riser/impacto final. Sem samples de terceiros.
- `build/rasterize_logos.py` — rasterização dos SVGs oficiais via Chrome
  headless (render vetorial exato; nenhum logotipo/texto gerado por IA).
- `build/logo_on_light.png`, `build/logo_on_dark.png` — logos rasterizados
  (variante escura do site para fundo claro; variante clara para o palco
  final escuro).

## Direção (roteiro executado)

| Tempo | Cena |
|-------|------|
| 0–5 s | Cartões de demandas dispersos e linhas de dependência; "Mais horas não resolvem tudo."; os cartões começam a se alinhar |
| 5–10 s | Constelação converte-se em núcleo conectado (hub "POD" com especialistas e agentes como elementos distintos); título "AI-Native Delivery Pods" + apoio "Uma equipe moldada pelo resultado." |
| 10–17 s | Expansão em cinco funções (Prototyper, Builder, Sweeper, Grower, Maintainer) com ações "explorar ideias / construir / simplificar / evoluir / manter"; "Especialistas + agentes supervisionados"; checkpoints humanos ao longo da linha (pontos de decisão) |
| 17–24 s | Fluxo "Contexto → Entrega → Qualidade"; artefatos conceituais percorrem o fluxo (Protótipo, Incremento de software, Teste, Revisão); evidências de progresso sem métricas; "Progresso visível. Responsabilidade clara." |
| 24–30 s | Convergência para palco escuro com logotipo oficial, título, CTA "Converse com um engenheiro." e "t2stech.com"; últimos ~3 s estáticos para leitura |

Elementos gráficos decompostos e animados individualmente (cartões, chips,
linhas, ícones, pílulas, réguas) — nenhum screenshot do site é usado como
cena. Os diagramas são representações conceituais do processo, não telas de
produto.

## Identidade visual

- Logotipo: SVGs oficiais `input/assets/assets__t2s-logo-dark.svg` e
  `assets__t2s-logo-light.svg` (rasterização vetorial exata).
- Paleta: extraída do CSS oficial
  (`input/assets/_next__static__chunks__23njtp8mlj1pv.css`) e do HTML da
  página — ciano `#00B4E8`, azul `#3264FF`, tinta escura `#011727`/`#0C2334`,
  papel `#F1F1F1`, superfícies e hairlines do próprio sistema do site.
- Tipografia: Montserrat (títulos/números, tracking negativo como no site)
  e Rubik (texto corrido), variáveis oficiais em `input/fonts/` (licenças
  OFL incluídas). Todo texto é desenhado como elemento gráfico exato.

## Áudio

Composição original programática — ver `output/music-license.md`. Não há
trilha de terceiro e não se alega licença de biblioteca externa.

## Decisões

1. **Renderizador próprio em vez de ferramenta de motion**: controle exato
   de easing, máscaras de revelação e continuidade de forma entre cenas
   (cada transição transforma a composição anterior), com determinismo para
   reprodução.
2. **Motion blur moderado por superamostragem temporal** (janela ~6 ms),
   desligado no trecho final para máxima nitidez de leitura.
3. **Especialistas vs. agentes**: pictogramas distintos (figura humana em
   círculo vs. símbolo de agente em diamante) — sem robôs humanoides.
4. **Checkpoints humanos** aparecem em pontos de decisão (linha de
   checkpoints na cena das funções e selo de validação nos artefatos),
   não apenas no final.
5. **Sem métricas fictícias**: as evidências mostradas são artefatos
   reais do processo (Protótipo demonstrável, Teste automatizado, Revisão
   registrada, Evidência de progresso), sem números inventados, clientes,
  depoimentos ou promessas de autonomia.
6. **Sincronização musical**: 120 BPM = 2 s por compasso; entrada de
   cena/mudanças de compasso alinhadas a 0/5/10/17/24 s; campainhas de
   checkpoint no compasso das decisões; whooshes nas transições.

## Limitações reais

- Síntese de áudio é programática (osciladores + filtros FIR próprios);
  o resultado é instrumental eletrônico "limpo", sem interpretação humana
  ou instrumentos acústicos reais.
- Toda a animação é 2D em plano estável, com parallax apenas nos slides de
  fundo da cena de funções — profundidade não é simulada com câmera 3D.
- O trecho final usa samples=1 (sem motion blur) para garantir leitura;
  as 2 primeiras usam 2 amostras por frame.
- Nenhum dado externo (fotos, vídeos, ilustrações de terceiros) foi
  utilizado além dos assets oficiais congelados em `input/`.

## Validação feita

- Revisão visual frame a frame das cenas e transições (ferramenta de
  visão) para legibilidade, cortes, sobreposições e grafia.
- Verificação programática de dimensões/duração com ffprobe no MP4 final.
- Verificação de presença de áudio (AAC) e sincronia de duração.
- Checagem de textos obrigatórios e ausência de métricas inventadas.
