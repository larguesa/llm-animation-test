# Relatório completo: T2S AI-Native Delivery Pods

Cinco modelos. Um mesmo briefing. Experimento realizado em 27/09/2026; documentação Markdown acrescentada em 30/09/2026. O retrato de percepção foi coletado em 30/09/2026 e incorporado ao relatório em 01/10/2026. A geração original do resumo está registrada em `2026-09-27T19:29:52Z`.

**Repositório público, conforme verificação da página e da API do GitHub em 01/10/2026.** A correspondência entre versões e modelos e os resultados de percepção estão documentados; Ricardo registra a revelação dos modelos no episódio do Desbugados vinculado na seção 8. Esta atualização não alterou a visibilidade encontrada.

[Baixar o relatório HTML (.zip)](https://github.com/larguesa/llm-animation-test/raw/refs/heads/main/report-html.zip) · [Resumo estruturado](summary.json) · [Prompt original](prompt.txt) · [Hashes](SHA256SUMS.txt)

O download contém o `report.html` atualizado, incluindo a coleta de percepção e o episódio do Desbugados. O ZIP permite baixar o arquivo em vez de abrir seu código no navegador. O HTML usa caminhos relativos para vídeos e imagens: para reproduzi-los offline, extraia o HTML na raiz de uma cópia completa deste repositório. O ZIP do relatório não inclui os MP4s nem as fontes dos candidatos.

## 1. Resumo executivo

Os cinco candidatos produziram MP4s finais com áudio e passaram nas verificações técnicas registradas. Cada candidato executou o trabalho em um processo Hermes com modelo e chave OpenRouter próprios. As fontes criativas são dos candidatos; não houve edição criativa do supervisor. Os arquivos finais preservados, e não as primeiras tentativas, são o objeto desta comparação.

O estudo documenta uma execução integral por modelo, incluindo retomadas e correções. **Não é um ranking geral nem uma comparação isolada de velocidade.** A percepção humana acrescentada na seção 8 é descritiva, com amostra pequena e cegamento não comprovado. A inspeção estética foi amostral, e o áudio não foi ouvido integralmente por um avaliador humano.

| Versão | Modelo | Tempo total | Custo da chave (USD) | Chamadas principais | Eventos de erro | YouTube | Vídeo original | Fontes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | openai/gpt-6-luna | 01:27:47 | 0.467659825 | 138 | 6 | [Versão 1](https://www.youtube.com/watch?v=DG9gIfH_3Hc) | [MP4](luna/luna-t2s-pods.mp4) | [ZIP](luna/luna-fontes.zip) |
| 2 | openai/gpt-6-astra | 01:36:14 | 10.6071655 | 41 | 26 | [Versão 2](https://www.youtube.com/watch?v=IWdM82_2kN0) | [MP4](astra/astra-t2s-pods.mp4) | [ZIP](astra/astra-fontes.zip) |
| 3 | anthropic/claude-opus-5.5 | 03:00:07 | 25.918514 | 45 | 8 | [Versão 3](https://www.youtube.com/watch?v=lE9gV8PbZ2w) | [MP4](opus/opus-t2s-pods.mp4) | [ZIP](opus/opus-fontes.zip) |
| 4 | meta/muse-spark-1.3 | 00:47:17 | 3.1216316 | 91 | 6 | [Versão 4](https://www.youtube.com/watch?v=5K7dABXSM94) | [MP4](muse/muse-t2s-pods.mp4) | [ZIP](muse/muse-fontes.zip) |
| 5 | xiaomi/mimo-v2.6-pro | 02:02:00 | 0.330521967 | 85 | 4 | [Versão 5](https://www.youtube.com/watch?v=5FdPaSsJwsg) | [MP4](mimo/mimo-t2s-pods.mp4) | [ZIP](mimo/mimo-fontes.zip) |

Total das cinco chaves de candidatos: **USD 40.445492892**. A numeração é ordem de apresentação, não classificação de qualidade. O total não inclui diagnósticos, supervisão, infraestrutura ou assinaturas.

## 2. Objetivo e protocolo

Produzir uma peça horizontal de motion graphics para apresentar o serviço AI-Native Delivery Pods da T2S Tech, com a identidade oficial, especialistas e agentes supervisionados, checkpoints humanos e evidências de entrega. A especificação pede 30 segundos, 1920×1080, 30 fps, MP4 com áudio, sem locução e sem inventar métricas, clientes ou interfaces proprietárias.

Referência do briefing: https://t2stech.com/services/ai-native-delivery-pods. O texto integral está na seção 11 e em `prompt.txt`.

| Item | Condição documentada |
| --- | --- |
| Provedor dos candidatos | OpenRouter |
| Prompt e entradas | Mesmo prompt e inputs oficiais congelados |
| Isolamento | Processos e workspaces separados, não sandboxes de segurança. Mesmo prompt e inputs oficiais congelados. |
| Raciocínio | Maior esforço anunciado solicitado: max; Opus usa adaptação verbosity=max. MiMo: reasoning enabled, sem prova de controle graduado. |
| Teto de saída | max_tokens=32000 |
| Contexto | context_length=200000 |
| Oportunidade inicial | 120 iterações |
| Correção objetiva | Uma rodada de até 40 iterações |
| Troca de modelos | Nenhum modelo substituído nas retomadas |
| Edição criativa do supervisor | Não realizada |

O teto de saída permaneceu fixo. Retomadas de infraestrutura preservaram as sessões. Maior esforço anunciado solicitado não equivale a raciocínio ilimitado; no MiMo não há prova de controle graduado de esforço máximo.

### Tempo decorrido e base das estratégias

Tempo total de ponta a ponta: ended_at menos started_at, em UTC. Inclui filas, retries, pausas, renderização e correções dentro desse intervalo; não é latência pura de inferência nem tempo exclusivo de render. Não inclui preparação anterior ao início do candidato nem publicação posterior ao término.

Síntese dos READMEs e fontes empacotadas dos candidatos, não acesso ao raciocínio interno dos modelos. Intervenções conforme registros do experimento.

| Versão | Início (UTC) | Término (UTC) | Segundos | hh:mm:ss |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-27T16:26:38Z | 2026-09-27T17:54:25Z | 5267 | 01:27:47 |
| 2 | 2026-09-27T16:26:38Z | 2026-09-27T18:02:52Z | 5774 | 01:36:14 |
| 3 | 2026-09-27T16:26:39Z | 2026-09-27T19:26:46Z | 10807 | 03:00:07 |
| 4 | 2026-09-27T16:26:39Z | 2026-09-27T17:13:56Z | 2837 | 00:47:17 |
| 5 | 2026-09-27T16:26:40Z | 2026-09-27T18:28:40Z | 7320 | 02:02:00 |

## 3. Intervenções e tratamento das falhas

- Supervisor reutilizou assets, chaves e testes anteriores; candidatos mantidos nos cinco IDs solicitados, somente via OpenRouter.
- Astra: retomadas da mesma sessão após 402 de reserva/crédito e 429 de verificação de créditos. Nenhum modelo substituído.
- Muse: primeira entrega preservada; o candidato corrigiu título parcialmente coberto na abertura e risco de saturação do AAC.
- Luna: chegou ao limite inicial de 120 iterações com MP4; rodada objetiva concluiu documentação e último render.
- Opus: execução inicial encerrou sem MP4 após respostas truncadas; recebeu a mesma oportunidade de correção de até 40 iterações.
- MiMo: ajustes e re-render dentro da própria execução inicial, sem código criativo do supervisor.

Os registros brutos, históricos, primeiras versões e recibos permanecem fora do repositório de artefatos. Logs e credenciais não são publicados. Ajustes de execução fazem parte do tratamento observado, por isso tempos e custos não devem ser interpretados como medidas puras de inferência.

## 4. Custos e telemetria

O custo de cada chave dedicada inclui a inferência principal, ferramentas auxiliares de percepção/compressão e eventuais chamadas truncadas ou com erro que tenham sido cobradas. A separação por fase utiliza snapshots de uso das chaves e pode ter defasagem. Os tokens abaixo cobrem apenas as chamadas principais registradas, não todos os serviços auxiliares.

**Raciocínio já integra a saída: não somar `reasoning_tokens` a `output_tokens`.** A entrada total é `prompt_tokens`, contabilizada cumulativamente entre chamadas, incluindo histórico repetido e cache. `cache_read_tokens` e `cache_write_tokens` são contadores separados, não acréscimos à entrada total. Zeros são valores reportados, não prova independente de ausência de cache. O hook não expôs generation IDs nem `usage.cost`; não há reconciliação exata de custo por geração.

| Modelo | Entrada total | Saída | Raciocínio (subconjunto) | Cache lido | Cache escrito |
| --- | --- | --- | --- | --- | --- |
| openai/gpt-6-luna | 11341403 | 191935 | 92185 | 10996025 | 344964 |
| openai/gpt-6-astra | 3316155 | 59282 | 28591 | 3198408 | 117624 |
| anthropic/claude-opus-5.5 | 3311527 | 331328 | 267400 | 2320166 | 991263 |
| meta/muse-spark-1.3 | 6376922 | 104539 | 48523 | 5391704 | 0 |
| xiaomi/mimo-v2.6-pro | 5834394 | 106054 | 58329 | 5470528 | 0 |

### Custos externos ao total dos candidatos

- Diagnósticos: USD 0.0479598.

- Supervisão anterior via OpenRouter, modelo `openai/gpt-6-astra`: aproximadamente USD 14.3799015, valor estimado, sem reconciliação por chave isolada.

- Supervisão posterior via `openai-codex`/OAuth: custo API indisponível. O estado `included` do resumo não comprova custo econômico zero.

- CPU, armazenamento e assinaturas não foram precificados. Serviços auxiliares dos candidatos estão nos totais das chaves, sem discriminação independente.

Não se publica um total global auditado somando valores reconciliados, estimativas e custos indisponíveis. `summary.json` preserva os contadores nativos, as estimativas históricas e o detalhamento por fase.

## 5. Validação técnica e evidências

As verificações originais incluíram ffprobe, decodificação integral, análise do áudio decodificado, amostras visuais e leitura do encerramento. Elas não equivalem a parecer estético de motion designer, aprovação jurídica da música ou escuta humana.

| Modelo | Resolução de saída | FPS | Duração do vídeo | Frames | Áudio | Decodificação |
| --- | --- | --- | --- | --- | --- | --- |
| openai/gpt-6-luna | 1920×1080 | 30 | 30 s | 900 | AAC presente | Aprovada |
| openai/gpt-6-astra | 1920×1080 | 30 | 30 s | 900 | AAC presente | Aprovada |
| anthropic/claude-opus-5.5 | 1920×1080 | 30 | 30 s | 900 | AAC presente | Aprovada |
| meta/muse-spark-1.3 | 1920×1080 | 30 | 30 s | 900 | AAC presente | Aprovada |
| xiaomi/mimo-v2.6-pro | 1920×1080 | 30 | 30 s | 900 | AAC presente | Aprovada |

A resolução de saída não garante resolução nativa de composição: o Luna rasterizou internamente em 1280×720 e ampliou por Lanczos, como detalhado na seção individual.

### Áudio final decodificado

| Modelo | Pico amostral | RMS | RMS (dBFS) | Amostras com módulo ≥ 1 | Duração decodificada (s) |
| --- | --- | --- | --- | --- | --- |
| openai/gpt-6-luna | 0.26664626598358154 | 0.04320738818454804 | -27.288839705629616 | 0 | 30.016 |
| openai/gpt-6-astra | 0.727967381477356 | 0.13413980165547768 | -17.44884680320468 | 0 | 30.016 |
| anthropic/claude-opus-5.5 | 0.7510722279548645 | 0.17647883430000585 | -15.066147471009131 | 0 | 30.016 |
| meta/muse-spark-1.3 | 0.7739788889884949 | 0.132174226055543 | -17.57706447842162 | 0 | 30.016 |
| xiaomi/mimo-v2.6-pro | 0.7360112071037292 | 0.17859391427110244 | -14.962666882466714 | 0 | 30.016 |

Não foram encontradas amostras saturadas nos arquivos finais. Essa análise numérica não demonstra qualidade de timbre, volume percebido, ausência de todos os defeitos ou sincronização perceptiva. A duração decodificada de AAC registrada é 30,016 s; a duração de vídeo validada é 30 s. Nenhum vídeo foi normalizado pelo supervisor.

### Leitura dos três segundos finais

| Modelo | Frames finais decodificados | Mudança média absoluta em relação a 27 s |
| --- | --- | --- |
| openai/gpt-6-luna | 90 | 0.0008102494855967078 |
| openai/gpt-6-astra | 90 | 0.000996656378600823 |
| anthropic/claude-opus-5.5 | 90 | 0.22696727109053497 |
| meta/muse-spark-1.3 | 90 | 0.4148227237654321 |
| xiaomi/mimo-v2.6-pro | 90 | 0.00709645061728395 |

Diferença de pixels é descritiva, não um veredito de legibilidade. As observações visuais específicas de encerramento e envelope de áudio constam na seção de cada candidato. As folhas de contato são links para as amostras, não prova de qualidade de todos os frames.

## 6. Análise individual dos cinco modelos

### 1. openai/gpt-6-luna

**Status registrado:** MP4 e documentação concluídos; validação técnica aprovada. Status estruturado: `completed_independently_validated`.

**Tempo total:** 01:27:47 (5267 segundos). **Custo da chave:** USD 0.467659825. **Chamadas principais:** 138. **Eventos de erro:** 6. Esses eventos não representam necessariamente requisições distintas cobradas.

#### Estratégia e procedimento

Composição procedural 2D em Python/Pillow e NumPy, com cartões que se organizam em núcleo, funções e fluxo. Usa Montserrat/Rubik, logos oficiais rasterizados, easing e trilha sintetizada por código. O compositor trabalha em resolução interna reduzida e amplia para 1920×1080 com Lanczos.

1. Ler os inputs oficiais congelados e preparar fontes e logos locais.
2. Compor cenas e áudio em src/render.py, gerar prévias e codificar H.264/AAC com FFmpeg.
3. Após o limite inicial de 120 iterações, concluir documentação e render na rodada objetiva de correção; validar o MP4 final.

Base documental nas fontes preservadas: [`output/README.md`](sources/luna/output/README.md), [`src/render.py`](sources/luna/src/render.py).

#### Fases e consumo principal

| Fase | Custo (USD) | Chamadas | Erros | Entrada | Saída | Raciocínio | Cache lido | Cache escrito |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| production | 0.42619279 | 120 | 5 | 9681066 | 179760 | 85554 | 9364779 | 315927 |
| correction-1 | 0.041467035 | 18 | 1 | 1660337 | 12175 | 6631 | 1631246 | 29037 |

#### Observações favoráveis

- Textos principais da abertura, cinco funções, fluxo e CTA presentes na amostra.
- Identidade escura consistente, logo oficial destacado no encerramento.
- Checkpoints de revisão humana distribuídos no fluxo, sem números de produtividade fictícios.
- Todos os testes técnicos passaram; áudio presente, sem amostras saturadas.

#### Ressalvas

- Fonte src/render.py: composição rasterizada em 1280x720 (S=2/3) e ampliada por Lanczos para 1920x1080. O arquivo satisfaz resolução de saída, mas não é render nativo 1080p.
- Textos auxiliares e rótulos de checkpoints são pequenos e discretos; comparação visual sugere menor legibilidade em telas reduzidas.
- Contraste dos elementos de conexão e do núcleo é sutil; apreciação estética não equivale a defeito técnico.
- Áudio tem RMS aproximado de -27,29 dBFS, inferior aos outros vídeos já medidos; não normalizado pelo supervisor nem classificado como inaudível.

#### Limitações e verificações de encerramento

- Inspeção visual por frames, sem julgamento integral de fluidez e sem escuta humana.
- A execução inicial atingiu 120 iterações antes da documentação; o próprio candidato concluiu em rodada objetiva de correção.

Encerramento: Frames aos 27 e 29,5 segundos inspecionados: logo, título, CTA e domínio visíveis, sem cortes; variação residual do fundo no Muse não prejudica texto.

Áudio: Envelope RMS do MP4 decodificado inspecionado; não se observam lacunas extensas, término com redução gradual. Isto não é escuta nem julgamento de timbre.

#### Artefatos e integridade

[Vídeo original](luna/luna-t2s-pods.mp4) · [Poster](luna/poster.jpg) · [Folha de contato](luna/contact.jpg) · [Fontes e inputs em ZIP](luna/luna-fontes.zip) · [Declaração da música](luna/music-license.md) · [Fontes extraídas](sources/luna/)

MP4: 2303622 bytes. SHA-256: `1f6684590de40596a700479f00ff81a9e130a1757526147e2af32a5a3e3b83ef`. Pacote com 22 arquivos selecionados no manifesto, mais `PACKAGE.txt` e `PACKAGE-SHA256.json`.

### 2. openai/gpt-6-astra

**Status registrado:** MP4 validado tecnicamente; inspeção visual por amostragem. Status estruturado: `completed_independently_validated`.

**Tempo total:** 01:36:14 (5774 segundos). **Custo da chave:** USD 10.6071655. **Chamadas principais:** 41. **Eventos de erro:** 26. Esses eventos não representam necessariamente requisições distintas cobradas.

#### Estratégia e procedimento

Pipeline modular Python/Skia com shaping HarfBuzz, fontes de pesos instanciados e síntese musical NumPy/SciPy. Transforma cartões em núcleo, capacidades e fluxo, com máscaras tipográficas, interpolação e blur temporal seletivo; encerra com composição estática.

1. Inspecionar a marca, preparar pesos tipográficos e paleta em src/prepare.py.
2. Gerar trilha em src/music.py e compor/renderizar com src/film.py, src/graphics.py e src/render.py; src/build_all.py coordena a entrega.
3. Retomar a mesma sessão após erros 402/429 em seis fases de recuperação; corrigir viewport do logo e linhas dos checkpoints, validar áudio/vídeo e gerar manifesto.

Base documental nas fontes preservadas: [`output/README.md`](sources/astra/output/README.md), [`src/build_all.py`](sources/astra/src/build_all.py), [`src/prepare.py`](sources/astra/src/prepare.py), [`src/graphics.py`](sources/astra/src/graphics.py), [`src/film.py`](sources/astra/src/film.py), [`src/music.py`](sources/astra/src/music.py), [`src/render.py`](sources/astra/src/render.py).

#### Fases e consumo principal

| Fase | Custo (USD) | Chamadas | Erros | Entrada | Saída | Raciocínio | Cache lido | Cache escrito |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| production | 4.589265 | 17 | 5 | 801989 | 42954 | 23259 | 715595 | 86343 |
| recovery-1 | 1.5898 | 3 | 4 | 274018 | 2071 | 787 | 266445 | 7564 |
| recovery-2 | 0.0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| recovery-3 | 1.0735345 | 4 | 3 | 387934 | 2235 | 0 | 383742 | 4180 |
| recovery-4 | 0.6252205 | 4 | 5 | 407290 | 3341 | 989 | 402863 | 4415 |
| recovery-5 | 2.4119255 | 11 | 5 | 1210368 | 7678 | 3165 | 1198053 | 12282 |
| recovery-6 | 0.31742 | 2 | 1 | 234556 | 1003 | 391 | 231710 | 2840 |

#### Observações favoráveis

- Abertura legível e cartões dispersos que aparecem alinhados no segundo frame.
- Cinco funções com nomes e ações visíveis, decisões com revisão humana explicitadas.
- Variação entre fundos escuro, azul e claro; boa hierarquia dos títulos na amostra.
- Fluxo Contexto, Entrega, Qualidade e quatro evidências de artefatos sem números fictícios.
- Logo oficial, título, CTA e domínio visíveis no encerramento.
- Todos os testes técnicos passaram; AAC sem amostras acima de 1.

#### Ressalvas

- Alguns textos auxiliares são pequenos; legibilidade em tela móvel não foi garantida.

#### Limitações e verificações de encerramento

- Inspeção de 12 frames, não julgamento da fluidez integral.
- Sem escuta humana, qualidade musical e sincronização perceptiva não foram confirmadas.

Encerramento: Frames aos 27 e 29,5 segundos inspecionados: logo, título, CTA e domínio visíveis, sem cortes; variação residual do fundo no Muse não prejudica texto.

Áudio: Envelope RMS do MP4 decodificado inspecionado; não se observam lacunas extensas, término com redução gradual. Isto não é escuta nem julgamento de timbre.

#### Artefatos e integridade

[Vídeo original](astra/astra-t2s-pods.mp4) · [Poster](astra/poster.jpg) · [Folha de contato](astra/contact.jpg) · [Fontes e inputs em ZIP](astra/astra-fontes.zip) · [Declaração da música](astra/music-license.md) · [Fontes extraídas](sources/astra/)

MP4: 3626066 bytes. SHA-256: `991ce9d434a3d67f94b71e47a6385ff3ae43f493aa543a4bdb347b788958345a`. Pacote com 38 arquivos selecionados no manifesto, mais `PACKAGE.txt` e `PACKAGE-SHA256.json`.

### 3. anthropic/claude-opus-5.5

**Status registrado:** MP4 validado tecnicamente; inspeção visual por amostragem. Status estruturado: `completed_independently_validated`.

**Tempo total:** 03:00:07 (10807 segundos). **Custo da chave:** USD 25.918514. **Chamadas principais:** 45. **Eventos de erro:** 8. Esses eventos não representam necessariamente requisições distintas cobradas.

#### Estratégia e procedimento

Canvas 2D em Chromium headless, controlado por Playwright/Python. Fontes oficiais e paths SVG em Path2D, transições por continuidade de formas, máscaras e seis subframes de motion blur. Música sintetizada em Python, com eventos de sincronia registrados.

1. Usar HTML/CSS e assets congelados como referência de marca e construir cenas JavaScript.
2. Gerar música, rasterizar 900 frames no Chromium e codificar/muxar com FFmpeg via src/build.sh; gerar QA e manifesto.
3. Após respostas truncadas e término inicial sem MP4, usar rodada objetiva de até 40 iterações; corrigir colisões/sobreposições e revisar amostras do render definitivo.

Base documental nas fontes preservadas: [`output/README.md`](sources/opus/output/README.md), [`src/build.sh`](sources/opus/src/build.sh), [`src/render.py`](sources/opus/src/render.py), [`src/main.js`](sources/opus/src/main.js), [`src/logo.js`](sources/opus/src/logo.js), [`src/compose.py`](sources/opus/src/compose.py), [`src/finalize.py`](sources/opus/src/finalize.py).

#### Fases e consumo principal

| Fase | Custo (USD) | Chamadas | Erros | Entrada | Saída | Raciocínio | Cache lido | Cache escrito |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| production | 3.9084818 | 8 | 2 | 189412 | 20528 | 18148 | 146387 | 43007 |
| correction-1 | 22.0100322 | 37 | 6 | 3122115 | 310800 | 249252 | 2173779 | 948256 |

#### Observações favoráveis

- Composição escura com hierarquia clara e contraste do ciano nos textos principais.
- Cinco funções reveladas sequencialmente e checkpoints humanos distribuídos abaixo dos cartões.
- Fluxo Contexto, Entrega, Qualidade e evidências de progresso visíveis na amostra.
- Logo oficial completo, título, CTA e domínio legíveis aos 27 segundos.
- Todos os testes técnicos passaram; áudio sem amostras saturadas, envelope com entrada e saída graduais.

#### Ressalvas

- Rótulos menores de checkpoints e evidências exigem tela maior para leitura confortável.
- Frames de 1s, 6s e 15s capturam máscaras durante revelações; não foram classificados como cortes acidentais com base em uma única imagem.

#### Limitações e verificações de encerramento

- Sem julgamento integral de fluidez, sincronização perceptiva ou escuta humana.
- Produção sofreu truncamentos com teto de saída 32000; houve rodada objetiva de correção após execução inicial sem MP4.
- Consulta ao site ao vivo retornou 301 sem seguir redirecionamento; o candidato usou a página e os assets oficiais congelados. Encerramento no limite da rodada de 40 iterações, com os quatro entregáveis presentes.

Encerramento: Versão final revalidada: logo, título, CTA e domínio legíveis aos 27 segundos; 90 frames finais decodificados.

Áudio: Envelope RMS inspecionado na entrega anterior; mesma análise numérica de pico/RMS na versão final, sem silêncio >=0,4s sob limiar -50dB. Sem escuta humana.

#### Artefatos e integridade

[Vídeo original](opus/opus-t2s-pods.mp4) · [Poster](opus/poster.jpg) · [Folha de contato](opus/contact.jpg) · [Fontes e inputs em ZIP](opus/opus-fontes.zip) · [Declaração da música](opus/music-license.md) · [Fontes extraídas](sources/opus/)

MP4: 10413134 bytes. SHA-256: `7b08bd64a9e7cdd114ae8a5d9428b689da136e8d8c49d0b547bb4002078d342d`. Pacote com 31 arquivos selecionados no manifesto, mais `PACKAGE.txt` e `PACKAGE-SHA256.json`.

### 4. meta/muse-spark-1.3

**Status registrado:** MP4 corrigido validado tecnicamente; inspeção visual por amostragem. Status estruturado: `completed_independently_validated`.

**Tempo total:** 00:47:17 (2837 segundos). **Custo da chave:** USD 3.1216316. **Chamadas principais:** 91. **Eventos de erro:** 6. Esses eventos não representam necessariamente requisições distintas cobradas.

#### Estratégia e procedimento

Renderização procedural em Pillow/NumPy com identidade derivada dos tokens CSS oficiais e logos rasterizados. Cartões viram núcleo POD, funções e trilha de entrega; usa máscaras, overshoot e rastros 2D. Áudio eletrônico original sintetizado a 120 BPM.

1. Compor áudio em work/src_audio.py e cenas em work/src_render.py, usando fontes e assets locais.
2. Renderizar vídeo sob lock e muxar H.264/AAC com FFmpeg.
3. Na rodada objetiva, desenhar a headline acima dos cartões com proteção de contraste e reduzir o teto do master para evitar saturação após AAC; verificar novamente o arquivo codificado.

Base documental nas fontes preservadas: [`output/README.md`](sources/muse/output/README.md), [`work/src_render.py`](sources/muse/work/src_render.py), [`work/src_audio.py`](sources/muse/work/src_audio.py).

#### Fases e consumo principal

| Fase | Custo (USD) | Chamadas | Erros | Entrada | Saída | Raciocínio | Cache lido | Cache escrito |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| production | 1.96971095 | 56 | 5 | 4074134 | 86115 | 40120 | 3485398 | 0 |
| correction-1 | 1.15192065 | 35 | 1 | 2302788 | 18424 | 8403 | 1906306 | 0 |

#### Observações favoráveis

- Título da abertura integralmente legível após correção pelo candidato.
- Cinco funções identificadas, fluxo Contexto, Entrega, Qualidade e evidências de progresso visíveis.
- Logo oficial e CTA visíveis no encerramento, com composição equivalente em 26 e 28,5 segundos.
- Todos os testes técnicos passaram; pico AAC decodificado 0,773979, sem amostras acima de 1.

#### Ressalvas

- Na abertura, textos dos cartões permanecem atrás do título; o título prioritário está legível, mas há competição visual residual.
- Checkpoints humanos e textos pequenos exigem inspeção em resolução integral; a folha de contato não prova sua leitura ao longo de todo o vídeo.

#### Limitações e verificações de encerramento

- Inspeção visual de 12 frames, não julgamento de fluidez integral.
- Áudio analisado numericamente, sem escuta humana; não afirmada qualidade musical ou sincronização perceptiva.

Encerramento: Frames aos 27 e 29,5 segundos inspecionados: logo, título, CTA e domínio visíveis, sem cortes; variação residual do fundo no Muse não prejudica texto.

Áudio: Envelope RMS do MP4 decodificado inspecionado; não se observam lacunas extensas, término com redução gradual. Isto não é escuta nem julgamento de timbre.

#### Artefatos e integridade

[Vídeo original](muse/muse-t2s-pods.mp4) · [Poster](muse/poster.jpg) · [Folha de contato](muse/contact.jpg) · [Fontes e inputs em ZIP](muse/muse-fontes.zip) · [Declaração da música](muse/music-license.md) · [Fontes extraídas](sources/muse/)

MP4: 9429538 bytes. SHA-256: `9d5221f4b2efc9c9d871abd899b66835d00796283822e3a6fb783b6b6154991c`. Pacote com 27 arquivos selecionados no manifesto, mais `PACKAGE.txt` e `PACKAGE-SHA256.json`.

### 5. xiaomi/mimo-v2.6-pro

**Status registrado:** MP4 e documentação concluídos; validação técnica aprovada. Status estruturado: `completed_independently_validated`.

**Tempo total:** 02:02:00 (7320 segundos). **Custo da chave:** USD 0.330521967. **Chamadas principais:** 85. **Eventos de erro:** 4. Esses eventos não representam necessariamente requisições distintas cobradas.

#### Estratégia e procedimento

Renderizador próprio Pillow/NumPy com grafo de cenas, supersampling espacial e temporal, easing e máscaras. Cartões passam por constelação, hub, funções e fluxo até o logo; áudio programático a 120 BPM com efeitos de checkpoints e transições.

1. Rasterizar SVGs oficiais via Chrome headless em build/rasterize_logos.py e gerar trilha em build/music.py.
2. Renderizar 900 frames em build/render.py e muxar áudio/vídeo com FFmpeg; preparar manifesto.
3. Realizar ajustes e novo render dentro da execução inicial, sem rodada externa de correção; conferir amostras e especificações do MP4.

Base documental nas fontes preservadas: [`output/README.md`](sources/mimo/output/README.md), [`build/rasterize_logos.py`](sources/mimo/build/rasterize_logos.py), [`build/music.py`](sources/mimo/build/music.py), [`build/render.py`](sources/mimo/build/render.py), [`build/manifest.py`](sources/mimo/build/manifest.py).

#### Fases e consumo principal

| Fase | Custo (USD) | Chamadas | Erros | Entrada | Saída | Raciocínio | Cache lido | Cache escrito |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| production | 0.330521967 | 85 | 4 | 5834394 | 106054 | 58329 | 5470528 | 0 |

#### Observações favoráveis

- Hierarquia clara dos títulos na amostra, alternância entre fundos claro, azul e escuro.
- Legenda de especialistas e agentes supervisionados legível após autocorreção do candidato.
- Cinco funções com ações e checkpoints humanos ao longo das decisões.
- Fluxo e evidências conceituais sem indicadores numéricos inventados.
- Logo oficial, serviço, CTA e domínio legíveis já aos 27 segundos.
- Todos os testes técnicos passaram; áudio sem amostras saturadas e envelope com saída gradual.

#### Ressalvas

- Textos secundários nas funções e nos artefatos são pequenos quando o vídeo é reduzido.
- A amostra de 17,5s captura uma faixa azul de transição, não uma cena estática; fluidez integral não foi julgada.

#### Limitações e verificações de encerramento

- Raciocínio habilitado, sem comprovação de controle graduado de esforço máximo no MiMo.
- Avaliação por amostras visuais e áudio numérico/visual, sem escuta humana.

Áudio: Envelope RMS do MP4 decodificado inspecionado; não se observam lacunas extensas, término com redução gradual. Isto não é escuta nem julgamento de timbre.

#### Artefatos e integridade

[Vídeo original](mimo/mimo-t2s-pods.mp4) · [Poster](mimo/poster.jpg) · [Folha de contato](mimo/contact.jpg) · [Fontes e inputs em ZIP](mimo/mimo-fontes.zip) · [Declaração da música](mimo/music-license.md) · [Fontes extraídas](sources/mimo/)

MP4: 3636021 bytes. SHA-256: `6a62c1385b8cf1bc78cd4ca8e2a0f68c3a9ededd4e4d7209b50616bf4e6746da`. Pacote com 30 arquivos selecionados no manifesto, mais `PACKAGE.txt` e `PACKAGE-SHA256.json`.

## 7. Síntese comparativa e limites de interpretação

Nesta execução, `xiaomi/mimo-v2.6-pro` teve o menor custo de chave, e `meta/muse-spark-1.3` o menor tempo total registrado. Isso não estabelece superioridade estética, qualidade média, produtividade geral nem vantagem causal de arquitetura. Custos dependem de chamadas, cache, serviços auxiliares e correções; tempos incluem esperas e renderização.

- Uma execução por modelo, com retomadas de transporte documentadas; não é ranking geral.
- Avaliação visual amostral e subjetiva, sem escuta humana nem julgamento integral de fluidez/sincronização.
- Teto de saída de 32000 pode truncar raciocínio e respostas; esforço máximo não significa raciocínio ilimitado.
- Composição programática declarada não equivale a parecer jurídico de direitos autorais.
- Fontes empacotadas e verificadas por hash/CRC; reprodução completa em máquina limpa não foi testada.

A presença dos textos principais e da marca em amostras não garante legibilidade móvel, fluidez de todas as transições ou sincronização musical integral. Estratégias são sínteses de documentação e código, não transcrições de raciocínio interno. Declarações mais amplas dos candidatos não substituem a validação independente.

**Percepção do público registrada em 30/09/2026:** 33 likes, 36 comentários de 8 contas e 16/36 acertos brutos de modelo (44,4%). Opus recebeu mais likes no retrato coletado. O detalhamento, as médias estimadas versus reais e as limitações do cegamento estão na seção 8; não há vencedor geral estabelecido.

## 8. Vídeos, percepção do público e revelação dos modelos

### Episódio do Desbugados

> **Assista à análise crítica e à revelação dos modelos no [Desbugados #076](https://www.youtube.com/watch?v=YXr0z2-87PQ).**
> 5 MODELOS VS 1 ANÚNCIO: QUAL FEZ O MELHOR MOTION GRAPHICS? l DESAFIO AO VIVO | DESBUGADOS #076

Ricardo registra que os vídeos foram criticados e os modelos revelados nesse episódio. A página do YouTube foi verificada para confirmar o link, o título e o canal Desbugados. Não se atribuem notas, falas ou timestamps específicos aos apresentadores sem transcrição validada. A discussão pública é distinta da validação técnica original por arquivos e amostras.

### 8.1. Tempo e gasto real por modelo, com os vídeos

| Versão | Modelo | Tempo total | Gasto da chave (USD) | Vídeo no YouTube | Original / fontes |
| --- | --- | --- | ---: | --- | --- |
| 1 | `openai/gpt-6-luna` | 01:27:47 | 0.467660 | [Versão 1](https://www.youtube.com/watch?v=DG9gIfH_3Hc) | [MP4](luna/luna-t2s-pods.mp4) / [ZIP](luna/luna-fontes.zip) |
| 2 | `openai/gpt-6-astra` | 01:36:14 | 10.607166 | [Versão 2](https://www.youtube.com/watch?v=IWdM82_2kN0) | [MP4](astra/astra-t2s-pods.mp4) / [ZIP](astra/astra-fontes.zip) |
| 3 | `anthropic/claude-opus-5.5` | 03:00:07 | 25.918514 | [Versão 3](https://www.youtube.com/watch?v=lE9gV8PbZ2w) | [MP4](opus/opus-t2s-pods.mp4) / [ZIP](opus/opus-fontes.zip) |
| 4 | `meta/muse-spark-1.3` | 00:47:17 | 3.121632 | [Versão 4](https://www.youtube.com/watch?v=5K7dABXSM94) | [MP4](muse/muse-t2s-pods.mp4) / [ZIP](muse/muse-fontes.zip) |
| 5 | `xiaomi/mimo-v2.6-pro` | 02:02:00 | 0.330522 | [Versão 5](https://www.youtube.com/watch?v=5FdPaSsJwsg) | [MP4](mimo/mimo-t2s-pods.mp4) / [ZIP](mimo/mimo-fontes.zip) |

**Total das cinco chaves: USD 40.445492892.** O tempo é de ponta a ponta, incluindo esperas, renderização, retomadas e correções. O gasto inclui chamadas principais e serviços auxiliares cobrados na chave de cada candidato. Diagnósticos, supervisão, CPU, armazenamento e assinaturas não entram nesse total. A numeração é ordem de apresentação, não posição em ranking.

Playlist literal fornecida por Ricardo: https://www.youtube.com/playlist?list=PLSxq4U-bytMY

Título verificado: **T2S AI-Native Pod Test**, de Ricardo Pupo Larguesa, com cinco versões. As métricas abaixo foram lidas nas páginas individuais dos vídeos, não inferidas da playlist. Não foi comparada a equivalência audiovisual das transcodificações do YouTube com os MP4s originais.

### 8.2. Coleta e métricas verificadas

**Retrato de 30/09/2026, entre 15h08 e 15h10 (America/Sao_Paulo).** Os horários exatos por vídeo estão no [registro estruturado pseudonimizado](docs/percepcao-2026-09-30.json). A coleta preserva o estado observado, não contagens atualizadas em tempo real.

Cada vídeo foi aberto em Chrome autenticado. Os likes foram lidos no controle do próprio vídeo. Os comentários foram ordenados por **Mais recentes** e carregados por rolagem, pois **Principais** inicialmente omitiu um comentário da versão 1. Foram lidos todos os comentários visíveis, e o total coletado de cada vídeo foi reconciliado programaticamente com seu contador. Não havia respostas adicionais indicadas nos comentários coletados.

| Vídeo | Likes | Comentários | Palpites de modelo | Acertos |
| --- | ---: | ---: | --- | ---: |
| [Versão 1](https://www.youtube.com/watch?v=DG9gIfH_3Hc) | 5 | 7 | Muse: 3; MiMo: 2; Luna: 2 | 2/7 |
| [Versão 2](https://www.youtube.com/watch?v=IWdM82_2kN0) | 8 | 8 | Astra: 5; Opus: 2; Muse: 1 | 5/8 |
| [Versão 3](https://www.youtube.com/watch?v=lE9gV8PbZ2w) | 12 | 8 | Opus: 6; Astra: 2 | 6/8 |
| [Versão 4](https://www.youtube.com/watch?v=5K7dABXSM94) | 4 | 6 | Luna: 4; MiMo: 2 | 0/6 |
| [Versão 5](https://www.youtube.com/watch?v=5FdPaSsJwsg) | 4 | 7 | MiMo: 3; Muse: 3; Astra: 1 | 3/7 |

**Totais: 33 likes, 36 comentários, 8 contas distintas e 16 acertos de modelo em 36 palpites (44,4%).** Os mesmos participantes comentaram em várias versões; não são 36 pessoas independentes. Não foram aplicados pesos de confiança aos palpites.

### 8.3. Expectativa de tempo e custo versus execução real

| Vídeo / modelo real | Tempo médio estimado | n tempo | Tempo real | Custo médio estimado (USD) | n custo | Custo real (USD) |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| [Versão 1](https://www.youtube.com/watch?v=DG9gIfH_3Hc) / `openai/gpt-6-luna` | 10,9 min | 7 | 01:27:47 | 0,27 | 7 | 0.467660 |
| [Versão 2](https://www.youtube.com/watch?v=IWdM82_2kN0) / `openai/gpt-6-astra` | 20,4 min | 8 | 01:36:14 | 2,26 | 8 | 10.607166 |
| [Versão 3](https://www.youtube.com/watch?v=lE9gV8PbZ2w) / `anthropic/claude-opus-5.5` | 20,9 min* | 7 | 03:00:07 | 2,67 | 8 | 25.918514 |
| [Versão 4](https://www.youtube.com/watch?v=5K7dABXSM94) / `meta/muse-spark-1.3` | 18,8 min | 6 | 00:47:17 | 0,47 | 6 | 3.121632 |
| [Versão 5](https://www.youtube.com/watch?v=5FdPaSsJwsg) / `xiaomi/mimo-v2.6-pro` | 15,7 min | 7 | 02:02:00 | 0,70 | 7 | 0.330522 |

*Na versão 3, um comentário dizia **até 30 min**. A média de tempo publicada usa os outros **7 palpites pontuais**, resultando em 20,9 min. Se o limite for tratado como 30 min, a média dos oito fica limitada a 22,0 min, mas não passa a ser uma média de oito estimativas exatas. O custo médio dessa versão considera todos os **8 comentários**.*

As médias são aritméticas e não ponderadas, calculadas a partir dos números escritos nos comentários. Valores em USD, com vírgula ou ponto decimal normalizados somente para cálculo. Os nomes abreviados foram agrupados nos cinco modelos quando explicitamente identificados; modelo é categoria, portanto se apresenta distribuição, não média numérica. Os custos reais estão arredondados a seis casas na tabela; a precisão original está no JSON e na contabilidade da seção 4.

### 8.4. Leitura dos resultados

- **Mais likes neste retrato:** versão 3, Claude Opus 5.5, com 12; seguida pela versão 2, GPT-6 Astra, com 8. Isso não constitui eleição com votos únicos nem ranking geral de qualidade.
- **Mais reconhecido:** Opus, 6 acertos em 8 palpites. Astra teve 5/8; MiMo 3/7; Luna 2/7; Muse 0/6.
- **Confusões:** versão 1 foi mais associada a Muse do que a Luna; versão 4 foi associada a Luna ou MiMo, sem palpite correto de Muse. Na versão 5, MiMo e Muse empataram com três palpites cada.
- **Tempo:** todas as médias estimadas ficaram abaixo dos tempos reais. Os tempos reais incluem esperas e trabalho de renderização/correção, enquanto os comentários não documentaram um protocolo comum para estimar duração.
- **Custo:** as médias ficaram abaixo do custo real nas versões 1 a 4. MiMo foi a exceção: estimativa média de USD 0,70, diante de USD 0,330521967 efetivamente registrado.
- **Comentário qualitativo explícito:** uma resposta da versão 3 declarou que foi o vídeo de que o participante mais gostou. Os demais textos coletados são principalmente palpites de modelo, tempo e custo; não foram convertidos em justificativas estéticas inexistentes.

### 8.5. Limitações da percepção e do cegamento

Esta é uma **amostra voluntária pequena e um retrato descritivo**, não um teste cego controlado. Não foram registrados início/fim de uma janela uniforme, confiança dos participantes ou autodeclaração de exposição aos resultados. Alguns comentários estavam editados. **Não foi validado se cada palpite foi feito ou editado antes da revelação no episódio**, nem se o participante já conhecia a correspondência; 44,4% é a proporção bruta de acertos observada, não uma medida controlada de identificação visual.

O relatório de entrega anterior já identificava os modelos por link. A revelação pública no Desbugados também torna inviável assumir cegamento de novas respostas. A privacidade do repositório não desfaz essa exposição. Likes não são votos exclusivos e podem refletir divulgação, alcance, prova social ou familiaridade, além de preferência pelo vídeo.

A ordem fixa, horários, thumbnail, reprodução automática, equipamento, volume, tamanho da tela e compressão do YouTube podem influenciar a percepção. Uma execução por modelo não sustenta conclusões causais ou generalizações sobre a qualidade média de cada modelo. A crítica dos apresentadores não foi transformada em pontuação quantitativa.

### 8.6. Dados e privacidade

O [JSON da coleta](docs/percepcao-2026-09-30.json) contém as 36 respostas textuais, classificações, denominadores, contagens, médias e a ligação de cada versão com seu modelo real. Os identificadores P01 a P08 são consistentes entre versões e substituem nomes e handles. O mapeamento de identidades e as capturas com nomes de usuários não estão no repositório.

Na verificação de 01/10/2026, o repositório já estava **público** na página e na API do GitHub (`private=false`). Essa visibilidade foi preservada, sem mudança de configuração nesta atualização. As notas antigas de privacidade descreviam a fase inicial do acervo, não o estado atual.

## 9. Preservação, reprodução e direitos

Os cinco MP4s e cinco ZIPs de fontes originais permanecem byte a byte preservados. O ZIP adicional `report-html.zip` contém apenas o relatório, não um sexto candidato. São 148 arquivos selecionados nos manifestos dos candidatos e 158 entradas extraídas contando os dois arquivos auxiliares de cada pacote.

As fontes oficiais, logos e materiais de marca têm direitos próprios. As declarações de composição musical programática não equivalem a parecer jurídico nem a registro de direitos autorais. Não existe licença genérica concedendo direitos sobre todo o repositório.

Consultar [reprodução e limites](docs/reproducao.md), os READMEs dos candidatos e os manifestos de pacote antes de executar qualquer fonte. Usar uma cópia isolada, adaptar caminhos e dependências, revisar o código e identificar uma reconstrução como novo artefato. Ambientes, bibliotecas nativas, logs e credenciais não acompanham as fontes. A reprodução completa em máquina limpa e a reprodução bit a bit não foram demonstradas.

O recibo [verification.json](verification.json) documenta a preparação original do acervo. Suas contagens e escopo são históricos, não incluem o novo Markdown nem o ZIP do relatório. O manifesto atualizado [SHA256SUMS.txt](SHA256SUMS.txt) cobre os arquivos atuais, exceto ele próprio e os metadados Git.

```sh
sha256sum -c SHA256SUMS.txt
```

Não publicar este diretório nem ativar GitHub Pages sem autorização específica. O relatório anterior e o episódio do Desbugados revelam identidades; a privacidade do GitHub não desfaz essa exposição.

## 10. Fontes documentais e escopo desta atualização

- [Relatório HTML atualizado](report.html), com a documentação original de produção e os novos resultados de percepção. A versão anterior permanece no histórico Git.
- [Resumo JSON](summary.json), protocolo, contabilidade, estratégias, procedimentos, validações e intervenções.
- [README](README.md), resumo, tempo/custo por modelo, links dos vídeos e destaque do episódio.
- [Coleta pseudonimizada](docs/percepcao-2026-09-30.json), comentários, palpites, contagens e cálculos da percepção.
- [Desbugados #076](https://www.youtube.com/watch?v=YXr0z2-87PQ), episódio de crítica dos vídeos e revelação dos modelos, conforme registro de Ricardo; título e canal verificados.
- [Prompt original](prompt.txt), bytes preservados e hash documentado.
- [Notas de reprodução](docs/reproducao.md) e [recibo original](verification.json).
- READMEs, códigos, declarações musicais e manifestos nas fontes de cada modelo.

Esta atualização incorpora o retrato de percepção coletado em 30/09/2026, relaciona tempos e gastos aos vídeos no YouTube e destaca o episódio do Desbugados. Markdown, HTML e ZIP do relatório foram atualizados. Não houve nova execução de modelos, reconstrução de vídeos ou alteração dos resultados originais de produção. O resumo original e os artefatos dos candidatos permanecem preservados; a coleta nova fica em JSON separado e pseudonimizado. A atualização não preenche custos indisponíveis, não amplia o alcance da validação técnica e não publica logs operacionais.

## 11. Prompt original integral

SHA-256 de `prompt.txt`: `7684288063461022ad603973b1069536705504b2802c84f9fc4abd7467be9d8c`. O bloco abaixo preserva o texto integral; o arquivo vinculado preserva seus bytes.

```text
Crie um vídeo de motion graphics de 30 segundos para apresentar o serviço AI-Native Delivery Pods da T2S Tech:

https://t2stech.com/services/ai-native-delivery-pods

Faça uma produção profissional, como a peça principal do portfólio de um excelente motion designer. Não entregue uma apresentação de slides, um protótipo ou uma simples gravação do site.

CONTEXTO

O serviço reúne especialistas experientes e agentes de IA supervisionados em uma equipe organizada em torno do resultado. Pode ser contratado como capacidade mensal ou uma etapa focada de entrega.

A composição muda conforme o trabalho. A responsabilidade permanece clara. Contexto, entregas demonstráveis, testes, revisão e evidências operacionais fazem parte do processo.

IDEIA CENTRAL

“Não contrate horas. Organize uma equipe em torno do resultado.”

Mostre visualmente demandas dispersas se transformando em um fluxo de entrega claro, com colaboração entre pessoas e agentes, checkpoints humanos e resultados verificáveis.

IDENTIDADE VISUAL

Visite a página e use o logotipo oficial, a paleta, a tipografia e os elementos gráficos reais da T2S. Preserve fielmente a identidade da marca.

Não use screenshots inteiros como cenas. Decomponha elementos do site em textos, cartões, linhas, ícones e formas que possam ser animados individualmente.

Como este é um serviço, não invente telas de um software proprietário. Diagramas e cartões devem funcionar como representações conceituais do processo, não como interfaces reais do produto.

ROTEIRO

0–5 segundos:
Comece com cartões de demandas e dependências dispersos, criando tensão visual controlada.
Texto: “Mais horas não resolvem tudo.”
Os elementos começam a se alinhar no ritmo da música.

5–10 segundos:
Os cartões se organizam em um núcleo conectado.
Revele: “AI-Native Delivery Pods”.
Texto de apoio: “Uma equipe moldada pelo resultado.”
Represente especialistas e agentes como elementos distintos e complementares, sem robôs humanoides.

10–17 segundos:
Expanda o núcleo em cinco funções:
Prototyper, Builder, Sweeper, Grower e Maintainer.
Associe cada função a uma ação visual: explorar ideias, construir, simplificar, evoluir e manter.
Anime as funções em sequência, mantendo os nomes legíveis.
Texto principal: “Especialistas + agentes supervisionados”.
Mostre checkpoints humanos nos pontos de decisão, não apenas no final.

17–24 segundos:
Transforme a composição em um fluxo:
“Contexto → Entrega → Qualidade”.
Faça artefatos conceituais percorrerem o fluxo: protótipo, incremento de software, teste e revisão.
Revele evidências de progresso, sem métricas fictícias.
Texto: “Progresso visível. Responsabilidade clara.”

24–30 segundos:
Os elementos convergem para uma composição limpa com o logotipo oficial.
Título: “AI-Native Delivery Pods”.
CTA: “Converse com um engenheiro.”
Endereço: “t2stech.com”.
Reserve os três segundos finais para leitura confortável.

MOTION DESIGN

Use tipografia cinética, máscaras de revelação, transições por continuidade de formas, movimentos escalonados, antecipação e desaceleração precisas.

Dê peso e personalidade ao movimento, com overshoot sutil e motion blur moderado. Cada transição deve transformar a composição anterior na próxima, não apenas trocar de cena.

Priorize animação dos elementos em um plano estável. Use profundidade e parallax discretos apenas quando ajudarem a explicar as relações.

Alterne momentos de energia com pausas para leitura. Uma ação visual dominante por cena. Evite movimento aleatório, efeitos excessivos e textos competindo pela atenção.

ÁUDIO

Use música instrumental eletrônica sofisticada, com licença adequada para uso comercial.
Sincronize entradas, transformações, cortes e resolução final com os beats e as mudanças da música.
Adicione efeitos sonoros discretos para conexões, checkpoints e transições.
Sem locução. A mensagem deve continuar compreensível com o áudio desligado.

QUALIDADE E ENTREGA

Formato horizontal 16:9, 1920×1080, 30 fps, duração de 30 segundos.
Textos em português brasileiro, preservando o nome do serviço e os nomes das cinco funções.

Renderize textos e logotipo como elementos gráficos exatos, nunca como lettering gerado por IA.

Não invente clientes, depoimentos, certificações, números de produtividade ou promessas de autonomia total.

Entregue o vídeo final em MP4 com áudio, não apenas storyboard ou código. Revise legibilidade, ortografia, identidade visual, sincronização e ausência de elementos cortados antes de finalizar.
```
