# Licença e procedência da música e dos efeitos sonoros

## Declaração

Trilha instrumental e todos os efeitos sonoros deste vídeo são COMPOSIÇÃO
ORIGINAL PROGRAMÁTICA, sintetizados por código neste workspace. Nenhum sample,
loop, gravação, stem ou biblioteca sonora de terceiros foi usado, baixado ou
embutido. Não há, portanto, licença de terceiro a declarar — e nenhuma é
alegada.

## Como foi produzida

- Fonte única: `work/src_audio.py` (numpy, síntese aditiva/subtrativa/FM
  simples, 48 kHz estéreo, 30,0 s, determinístico com seed fixa).
- Todos os timbres (kick, clap, hats, shaker, baixo, pads, plucks, arps,
  toms, chimes, ticks, blips, whooshes, riser, impacto) são osciladores,
  ruído filtrado e envelopes gerados no próprio script.
- Intermediário: `work/audio_mix.wav` (PCM 16-bit, pico −1 dBFS).
- Final: faixa AAC 192 kbps multiplexada em `output/final.mp4` via ffmpeg,
  sem outro processamento.

## Direitos

Sendo obra original gerada para esta entrega, a trilha acompanha o vídeo como
parte da peça. Uso comercial do vídeo final inclui o áudio embutido, sem
royalties de terceiros, sem atribuição obrigatória e sem restrições de
Content ID de catálogo externo (a obra não foi registrada em nenhum catálogo).

## Verificação

- `ffprobe output/final.mp4` confirma 1 faixa de áudio AAC estéreo 48 kHz,
  30,00 s, sem metadados de editora/selo.
- O script `work/src_audio.py` é autocontido: não faz download, não lê
  arquivos de áudio, importa apenas `wave` + `numpy`.
