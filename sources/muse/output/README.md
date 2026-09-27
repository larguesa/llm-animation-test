# T2S AI-Native Delivery Pods — vídeo motion graphics 30 s

Peça principal: apresenta o serviço AI-Native Delivery Pods da T2S Tech
(https://t2stech.com/services/ai-native-delivery-pods) como fluxo de entrega
claro, com especialistas + agentes supervisionados, checkpoints humanos e
evidências de progresso. Sem locução; compreensível com áudio desligado.

## Reprodução

- Arquivo final: `./output/final.mp4`
  (H.264 yuv420p 1920×1080 30 fps + AAC estéreo 48 kHz, 30,00 s)
- Reproduzir: `ffplay output/final.mp4`
  ou `mpv output/final.mp4`
  ou abrir o arquivo em qualquer player/navegador.
- Verificar specs: `ffprobe -hide_banner output/final.mp4`
- Regenerar do zero (reproduzível, determinístico):
  1. `python3 work/src_audio.py` → gera `work/audio_mix.wav`
  2. `flock /home/hermes/entregas/t2s-pods-model-comparison/render.lock python3 work/src_render.py --render` → gera `work/video.mp4`
  3. `ffmpeg -y -i work/video.mp4 -i work/audio_mix.wav -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart output/final.mp4`
- Pré-visualizar frames sem renderizar tudo:
  `python3 work/src_render.py --preview 2.5 8.0 13.0 16.1 20.5 26.0`
  → PNGs em `work/preview/`.

## Roteiro executado (30 s, 16:9, 30 fps)

- 0–5 s — Tensão controlada: 8 cartões de demandas/dependências dispersos
  ("Nova funcionalidade / escopo aberto", "Bug em produção / sem dono
  definido", "Integração externa / dependência externa", "Lentidão no app /
  sem contexto", "Débito técnico / retrabalho", "Novo relatório / prioridade
  incerta", "Migração de dados / bloqueado", "Pedido do cliente / prazo
  apertado") com vínculos tracejados âmbar/vermelho. Headline:
  "Mais horas / não resolvem tudo." Os cartões se alinham em grade ~3,2–4,7 s.
- 5–10 s — Os cartões convergem para o núcleo "POD"; hubs com 3 nós
  especialistas (pessoa) + 3 nós agentes (hexágono com centelha, sem robôs
  humanoides). Título "AI-Native Delivery Pods", apoio "Uma equipe moldada
  pelo resultado."
- 10–17 s — Núcleo expande na espinha para 5 funções em sequência nos beats
  10,5 / 11,5 / 12,5 / 13,5 / 14,5 s: Prototyper (explorar ideias), Builder
  (construir), Sweeper (simplificar), Grower (evoluir), Maintainer (manter),
  cada cartão com barra especialista/agente. Texto "Especialistas + agentes
  supervisionados". Três badges verdes de checkpoint (15,35 / 15,75 / 16,15 s)
  entre Builder–Sweeper–Grower–Maintainer + legenda "checkpoints humanos nas
  decisões".
- 17–24 s — Fluxo "Contexto → Entrega → Qualidade" (estações: "entender o que
  existe", "incrementos visíveis", "testes e revisão"); quatro artefatos
  conceituais percorrem a trilha: protótipo, incremento, teste, revisão; ticks
  de passagem e bursts de chegada; evidências sem métricas fictícias: "dono
  definido", "incremento demonstrável", "testes executados", "revisão
  registrada". Texto "Progresso visível. Responsabilidade clara."
- 24–30 s — Impacto + convergência para end-card limpo: logotipo oficial T2S
  (SVG congelado, rasterizado via cairosvg), "PRÓXIMO PASSO", "AI-Native
  Delivery Pods", botão "Converse com um engenheiro ↗", "t2stech.com".
  Composição 100% estática e legível de ~27,5 s a 30 s (leitura confortável).

## Decisões de direção e técnica

- Render 100% programático (Pillow + numpy → ffmpeg/libx264). Nenhum frame
  usa screenshot do site; identidade reconstruída dos tokens reais do CSS
  congelado: --ink #22262b, --paper, --cyan #00b4e8, --blue #3264ff,
  --blue-deep, --green, --amber, --red + Montserrat (títulos/eyebrows) e Rubik
  (corpo), arquivos TTF congelados em ./input/fonts.
- Logo oficial: `input/assets/assets__t2s-logo-light.svg` sobre fundo escuro,
  convertido para PNG com cairosvg (arte vetorial exata, sem lettering de IA).
- Continuidade de formas entre cenas: cartões → núcleo POD (mesmos cartões
  voam para o centro) → nós viram cartões de função → espinha vira trilha de
  fluxo → tudo converge no end-card. Tipografia cinética com máscaras de
  revelação (wipe), overshoot sutil (easeOutBack), motion blur moderado
  (ghosts nos tokens do fluxo), pausas de leitura em cada ato.
- Áudio: composição instrumental original 100% sintetizada em
  `work/src_audio.py` (numpy, 120 BPM): pads, groove kick/clap/hats, baixo,
  motivos, arps, toms nos 5 reveals, chimes nos checkpoints, ticks nos gates,
  whooshes, riser 22,6–24 s, impacto em 24,0 s, resolução half-time. SFX
  discretos de conexão/checkpoint/transição. Sem locução, sem samples de
  terceiros. Ver `music-license.md`.
- Sincronização: beats em 0,5 s; reveals em 10,5–14,5 s; checkpoints em
  15,35–16,15 s; fluxo 17–24 s; impacto/resolução em 24 s; CTA em 25,15 s.

## Correções v2 (rodada única de correção objetiva)

Dois defeitos verificáveis apontados pelo supervisor, sem troca de direção
criativa. Originais v1 preservados em `work/final_v1.mp4`,
`work/src_render_v1.py`, `work/src_audio_v1.py`, `work/audio_mix_v1.wav`.

1. Abertura (t=4,0 s): a primeira fileira de cartões cobria parte da segunda
   linha do título ("não resolvem tudo."). Correção em `scene1` de
   `work/src_render.py`: a headline passou a ser desenhada DEPOIS dos cartões
   e vínculos (sempre no topo), com halo escuro próprio por linha (scrims
   primeiro, depois as duas linhas de texto, para a linha 1 não escurecer sob
   o halo da linha 2). Posições, roteiro e animação dos cartões inalterados.
2. Áudio: o AAC entregue media pico float 1,216654 (152 amostras ≥1,0) —
   risco de saturação real. Correção em `work/src_audio.py`: teto do master
   reduzido de −1 dBFS para −5 dBFS (fator 0,562/pico), mesma mixagem e SFX.
   Medido no MP4 codificado decodificado (pcm_f32le): pico 0,773979,
   0 amostras ≥1,0 em 2.881.536 — PASS. (Intermediário a −3 dBFS ainda deu
   pico 1,038724, por isso o teto final é −5 dBFS.)

## Limitações reais

- Animação 2D rasterizada quadro a quadro em CPU (Pillow): sem motion blur
  3D real, sem profundidade de campo ótica, sem partículas GPU. Efeitos de
  brilho/blur são aproximações 2D.
- Ícones das funções e diagramas são representações conceituais geométricas
  (não telas de produto — conforme o brief, o serviço não tem UI própria).
- Música original programática: timbres de síntese aditiva/subtrativa simples
  (sem bibliotecas orquestrais); master moderado (pico −5 dBFS no WAV para
  true-peak seguro pós-AAC: 0,774 medido no MP4 decodificado).
- Render completo leva ~65 s em 2 CPUs compartilhadas; feito sob flock para
  não competir com outros candidatos.

## Validação executada (ferramentas, não estimativa)

- `ffprobe`: 900 frames, 1920×1080, avg 30 fps, duração 30,00 s vídeo e áudio.
- Áudio do MP4 final extraído e medido (pcm_f32le): pico 0,773979, 0 amostras
  ≥1,0 (true-peak seguro); sem trechos de silêncio ≥1 s a −50 dB; cauda
  29,5–30 s com energia e sem corte seco. Validação feita no MP4 codificado,
  não só no WAV fonte.
- Frames do MP4 final inspecionados visualmente (2,5 / 3,5 / 4,0 / 4,5 / 5,0 /
  8,0 / 10,4 / 13,0 / 16,1 / 16,6 / 17,6 / 20,5 / 24,3 / 26,0 / 28,5 / 29,0 s):
  frase "Mais horas / não resolvem tudo." integral em todo o intervalo de
  leitura da abertura, sem nenhum elemento sobre o texto; ortografia PT-BR
  conferida, 5 funções legíveis, 3 checkpoints verificados em 16,6 s, CTA+URL
  legíveis nos 3 s finais, sem texto cortado pela borda, sem sobreposição
  ilegível em transições, sem dano de compressão no texto.
- Fora da abertura, o vídeo é pixel-idêntico à v1 (diff t=20,5 s: maxdiff 0,
  meandiff 0,0000): nenhuma outra cena foi tocada.
- Textos e logo são gráficos exatos (fontes oficiais + SVG oficial); nenhum
  cliente/depoimento/certificação/número de produtividade foi inventado.
