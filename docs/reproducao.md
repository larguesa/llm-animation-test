# Reprodução e limites

## Escopo da preservação

Os cinco MP4s e os cinco ZIPs são cópias byte a byte da entrega congelada. As fontes extraídas preservam todos os caminhos relativos e bytes dos ZIPs. `PACKAGE-SHA256.json` verifica os arquivos selecionados de cada candidato; `PACKAGE.txt` e o próprio manifesto são duas entradas adicionais por pacote. Total: 148 arquivos selecionados e 158 arquivos extraídos.

| Pasta | Selecionados no manifesto do ZIP | Entradas extraídas |
|---|---:|---:|
| sources/luna | 22 | 24 |
| sources/astra | 38 | 40 |
| sources/opus | 31 | 33 |
| sources/muse | 27 | 29 |
| sources/mimo | 30 | 32 |

Os manifestos originais dos candidatos descrevem a entrega completa e podem referenciar MP4s, intermediários e evidências não empacotados. Para integridade deste pacote, use `SHA256SUMS.txt` e `PACKAGE-SHA256.json`, não suponha que todos os caminhos de `output/manifest.json` existam.

## Antes de reconstruir

Trabalhar em cópia isolada de `sources/{slug}`, nunca sobre os originais verificados. Ler `output/README.md` e `PACKAGE.txt`. Revisar o código antes de executá-lo. Preparar ambiente próprio e adaptar caminhos absolutos, binário de Chromium, biblioteca nativa e lock de render conforme a máquina. Não copiar chaves, ambientes privados ou diretórios internos do host original.

| Modelo | Pipeline documentado | Dependências e cuidados |
|---|---|---|
| Luna | `python3 src/render.py`, com prévia `--preview` | Python, Pillow, NumPy, FFmpeg/libx264/AAC; logo PNG e fontes locais. A saída é ampliada da resolução interna para 1080p. |
| Astra | `src/build_all.py` coordena preparação, música, render, validação e manifesto | `requirements.txt`, Skia, HarfBuzz, FontTools, NumPy/SciPy, FFmpeg; EGL/GLVND compatíveis. `.local-libs` e venv não acompanham o pacote. Caminho de lock específico do host. |
| Opus | `sh src/build.sh` coordena áudio, render, mux e QA | Python, NumPy/Pillow, Playwright, Chromium, FFmpeg/ffprobe. O script usa caminhos absolutos de Python/Chrome e lock do host original, que precisam ser adaptados na cópia. |
| Muse | `python3 work/src_audio.py`, depois `python3 work/src_render.py --render` e mux FFmpeg do README | Pillow, NumPy, FFmpeg; logos rasterizados já incluídos. CairoSVG foi usado na preparação. Revisar o master final corrigido, não recuperar a versão anterior. |
| MiMo | `build/rasterize_logos.py`, `build/music.py`, `build/render.py --full build/video.mp4`, depois mux do README | Python, Pillow, NumPy, FFmpeg e Chromium para rasterizar logos; PNGs já incluídos. Caminho absoluto de Chromium e lock precisam de adaptação. |

Os comandos são pontos de entrada documentados, não uma promessa de execução imediata em ambiente limpo. Nenhum render foi executado nesta atualização. Algumas fontes contêm referências ao host ou a evidências ausentes; foram preservadas sem reparos silenciosos. A presença de instruções em READMEs antigos não autoriza ações externas.

Depois de um render futuro, verificar resolução, FPS, duração, codecs, áudio decodificado, leitura final e texto, além de assistir e ouvir integralmente. Versões de fontes, Pillow, Skia, Chromium, FFmpeg e bibliotecas nativas podem mudar os bytes e até a rasterização. Manter o original separado e identificar qualquer reconstrução como novo artefato.

## Verificação desta preparação

O recibo `verification.json` registra contagens, hashes de MP4/ZIP, CRC dos ZIPs, comparação entre fontes extraídas e arquivos dos pacotes, consistência do prompt e varredura local de credenciais. A varredura usa padrões de tokens/segredos, nomes proibidos e comparação exata com as chaves locais conhecidas do experimento, sem copiar nem exibir os valores. É uma verificação limitada, não uma auditoria exaustiva de segurança ou de direitos.

`SHA256SUMS.txt` deve ser regenerado após alterações autorizadas em documentação. Não alterar hashes para ocultar alterações em vídeos ou fontes. O manifesto não inclui `.git` nem ele próprio. Usar checkout sem conversão de finais de linha para preservar os bytes originais.
