# T2S Tech — AI-Native Delivery Pods

Motion graphics original de 30 segundos para apresentar o serviço AI-Native Delivery Pods. O arquivo final é `output/final.mp4`.

## Reproduzir o vídeo

A partir da raiz deste workspace:

```sh
ffplay -autoexit output/final.mp4
```

## Regerar o MP4

Requisitos usados nesta execução: Python 3 com Pillow e NumPy, FFmpeg com encoder libx264 e AAC, e os assets/fontes locais em `input/` e `src/`.

```sh
python3 -m py_compile src/render.py
flock /home/hermes/entregas/t2s-pods-model-comparison/render.lock python3 src/render.py
```

O `flock` serializa a renderização com as demais execuções do experimento. O comando `python3 src/render.py --preview` gera cinco quadros de revisão em `output/review-frames/`; ele não cria o vídeo.

## Decisões de produção

- Composição procedural em Python/Pillow, codificação H.264/AAC via FFmpeg, 1920×1080, 30 fps, 30 segundos.
- Logotipo oficial fornecido pela T2S, paleta consultada no CSS oficial e tipografias Montserrat e Rubik fornecidas com seus textos de licença OFL em `input/fonts/`.
- A narrativa transforma demandas dispersas em um núcleo orientado ao resultado, apresenta pessoas e agentes supervisionados, as cinco funções e checkpoints humanos, e um fluxo conceitual de Contexto → Entrega → Qualidade.
- Cartões e artefatos são diagramas ilustrativos do serviço, não telas de um produto T2S; gráficos não representam métricas nem resultados reais.
- Sem locução. A trilha instrumental é síntese programática original desta execução; detalhes de procedência estão em `output/music-license.md`.
- A cartela de encerramento mantém título, CTA e endereço visíveis durante os três segundos finais.

## Limitações

A peça usa motion graphics vetoriais/rasterizados e formas esquemáticas; não inclui filmagem, captação de áudio nem interfaces reais de software. A música é uma composição eletrônica sintetizada por código, não uma faixa comercial de catálogo nem uma licença de música de terceiros. O arquivo `output/manifest.json` registra hashes dos artefatos efetivamente entregues.
