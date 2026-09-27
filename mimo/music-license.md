# Procedência da música — final.mp4

## Declaração

A trilha instrumental do vídeo **"AI-Native Delivery Pods"** (30 s) é uma
**composição original criada programaticamente** para este projeto.
Não há licença de terceiro alegada e não há samples, loops, gravações ou
trechos de obras existentes.

- Origem: sintetização 100% programática (numpy), gerada por `build/music.py`.
- Arquivo gerado: `build/music.wav` (30,0 s, 48 kHz, estéreo, 16-bit PCM).
- Autoria: composição gerada por software no contexto deste experimento
  (Hermes Agent / Nous Research, execução de 2026-09-27). Sem uso de modelos
  gerativos de áudio de terceiros.

## Características da composição

- Título sugerido: "Delivery Pods" (bed instrumental).
- 120 BPM (2 s por compasso), tonalidade Lá menor, 4/4.
- Camadas: sub/baixo sintetizado, arpejos (seno + ruído filtrado), pads,
  percussão eletrônica (kick, caixa/clap, hi-hats), campana de "checkpoint"
  (sine 1568 Hz, sincronizada com os marcos de decisão do roteiro),
  whooshes/cortes de transição (ruído filtrado) e riser/impacto final.
- Filtros implementados por convolução FFT sobre kernels FIR próprios
  (janelas de Hamming); envelopes exponenciais; compressor e limitador de
  pico programáticos.

## Reprodução / regeneração

```bash
cd /home/hermes/entregas/t2s-pods-model-comparison/runs/mimo/work
python3 build/music.py      # regrava build/music.wav deterministicamente
```

O mux de áudio no vídeo final é feito por ffmpeg (ver `output/README.md`).

## Licença de uso

Como obra original deste experimento, os direitos são do autor/comitente da
execução e o uso comercial é permitido sem exigir licença de terceiros.
Nenhuma entidade externa (artista, gravadora, biblioteca de música) tem
direitos sobre esta trilha.
