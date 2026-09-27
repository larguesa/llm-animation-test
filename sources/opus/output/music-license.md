# Música e efeitos sonoros: procedência

Declaração: a trilha e todos os efeitos sonoros de `output/final.mp4` são uma composição instrumental original, feita por programação neste workspace. Não uso música, loops, samples, presets nem gravações de terceiros. Por isso não declaro nenhuma licença de terceiros.

## Como foi feita
- `src/audio_synth.py` é um sintetizador escrito em numpy. Ele gera o som com osciladores (dente de serra com PolyBLEP, senoides, FM), ruído branco com semente fixa, filtros no domínio da frequência e reverb por convolução com resposta ao impulso sintética. Também tem um delay ping-pong.
- `src/compose.py` escreve a partitura e o mix:
  - Andamento de 120 BPM, com tonalidade de ré menor que resolve em ré maior no logotipo.
  - Instrumentos: pads supersaw com filtro variável no tempo, baixo, bateria sintética (kick, clap, hi-hat, prato), plucks, sinos FM e efeitos sonoros (ticks, whooshes, risers, sub boom).
  - O script também gera o log de eventos `output/audio_events.json`.
- O resultado é determinístico, com sementes fixas. `python3 src/compose.py` recria `build/music.wav`, `build/sfx.wav` e `build/mix.wav`.
- Não há voz, locução, TTS nem amostras vocais.

## Autoria e uso
- O código e a composição foram escritos nesta sessão pelo assistente de IA (Claude, via Hermes Agent), como código-fonte. Não usei nenhum modelo generativo de música ou de áudio.
- Não há catálogo nem licença de terceiros envolvidos. Qualquer decisão sobre titularidade ou uso comercial cabe à T2S e ao supervisor do projeto. Se for necessária uma validação formal, recomenda-se uma revisão jurídica.

## Outros ativos (não musicais)
- Fontes: Montserrat e Rubik, sob SIL Open Font License 1.1. As licenças estão em `input/fonts/*OFL.txt`.
- Logotipo: arquivo oficial da T2S, `input/assets/assets__t2s-logo-light.svg`, usado sem alterar a geometria nem as cores.
