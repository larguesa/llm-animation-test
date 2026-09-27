T2S Tech — AI-Native Delivery Pods

ENTREGA

Vídeo final: final.mp4
Formato verificado por ffprobe: 1920 × 1080, 16:9, 30 fps, 900 quadros, 30,000 segundos.
Vídeo H.264, yuv420p, BT.709. Áudio AAC estéreo, 48 kHz, codificado a 320 kb/s. MP4 com faststart.
Sem locução. A mensagem e os checkpoints permanecem compreensíveis sem áudio.

REPRODUZIR

A partir da raiz deste workspace:

    ffplay -autoexit output/final.mp4

Também é possível abrir final.mp4 diretamente em VLC ou num navegador compatível com H.264/AAC. O vídeo não depende do site, de um servidor ou de recursos externos para tocar.

DECISÕES DE DIREÇÃO

A peça usa um plano estável e elementos vetoriais individualmente animados, não uma gravação do site. Os cartões iniciais alinham-se, tornam-se nós de um pod centrado no resultado e se desdobram nas capacidades. O campo azul se transforma no plano claro do fluxo. Os artefatos e sinais de validação convergem para a assinatura final.

0–5 s: demandas e dependências dispersas; “Mais horas não resolvem tudo.”; antecipação e alinhamento escalonado.
5–10 s: núcleo conectado; serviço, especialistas e agentes representados por símbolos distintos; informação sobre capacidade mensal ou etapa focada.
10–17 s: Prototyper, Builder, Sweeper, Grower e Maintainer, com ações sequenciais de explorar, construir, simplificar, evoluir e manter. Pontos humanos de validar, revisar e liberar aparecem durante o trabalho.
17–24 s: Contexto → Entrega → Qualidade; protótipo, incremento de software, teste e revisão, com evidências conceituais de progresso e responsabilidade.
24–30 s: convergência, logotipo oficial, serviço, CTA e endereço. De 27 a 30 s a composição visual fica parada para leitura.

Movimento: máscaras tipográficas, interpolação quintic, desaceleração cúbica, overshoot contido, transições por expansão e continuidade de formas. Motion blur temporal moderado apenas durante os deslocamentos maiores; os momentos de leitura permanecem nítidos.

IDENTIDADE E FONTES

A URL https://t2stech.com/services/ai-native-delivery-pods foi consultada com sucesso (HTTP 200), além dos inputs oficiais congelados em input/.

Logotipo: SVG oficial claro/escuro, renderizado diretamente, sem alteração dos paths, cores ou proporção. O viewport SVG foi explicitamente ajustado ao viewBox original para corrigir sua ausência detectada na primeira revisão.
Fontes: Montserrat nos títulos e Rubik nos textos de apoio; arquivos oficiais fornecidos em input/fonts/. Instâncias de peso determinísticas são geradas em build/fonts/. As licenças SIL OFL acompanham os inputs.
Paleta: #22262b, #f6f9fb, #ffffff, #00b4e8, #3264ff e cores auxiliares extraídas do CSS oficial. O manifesto contém o mapa de cores e hashes dos assets.

A captura da página em review/official-page.png é apenas documentação da pesquisa; não integra as cenas. Cartões e diagramas são representações conceituais de um serviço, não telas de um produto proprietário. Não há clientes, depoimentos, certificações, métricas de produtividade ou promessas de autonomia inventadas.

ÁUDIO E PROCEDÊNCIA

Instrumental eletrônico original composto programaticamente a 120 BPM, com pads, baixo, plucks, percussão e efeitos discretos. Sem samples, loops ou gravações externas. A declaração completa está em music-license.md; não se alega licença de uma biblioteca musical de terceiros.

Fontes: src/music.py e build/audio/score.json. Stems e master PCM estão em build/audio/.
As entradas dos papéis e as mudanças da trilha seguem a grade de beats; conexões, revisão humana e transições possuem eventos sonoros dedicados. Não há locução.

VERIFICAÇÃO

O MP4 também foi reproduzido até o fim em Chrome headless independente. O teste em velocidade 2× registrou 900 frames totais, zero frames corrompidos e 31 frames descartados pela reprodução em CPU compartilhada; não houve erro do player. Esse teste foi mudo e não constitui audição. Registro: review/browser-playback.json.

O registro automatizado da entrega fica em review/validation.json e os metadados integrais em review/ffprobe.json. O verificador:

    confirma resolução, taxa, quadros, duração, codecs e canais;
    decodifica integralmente vídeo e áudio para detectar erros;
    extrai frames do MP4 entregue para revisão, não apenas do compositor;
    mede os 90 quadros finais reservados à leitura;
    verifica limites dos glifos nos frames de leitura;
    mede loudness, true peak, amplitude e amostras saturadas no AAC decodificado.

Frames de revisão: review/final-contact-sheet.png e review/decoded-*.png.
Sinal de áudio: review/audio-waveform.png e review/audio-loudness.txt.
Na revisão visual, foram corrigidos o viewport do logotipo e as hastes que passavam atrás das legendas dos checkpoints. Textos, nomes das cinco funções, acentuação, CTA e endereço foram conferidos nas imagens de resolução integral.

LIMITAÇÕES REAIS

Este ambiente CLI não oferece audição subjetiva do som ao agente. O áudio foi revisado por decodificação, waveform, envelopes, duração, loudness, true peak e tempos dos eventos; não se afirma que houve escuta em monitores/fones. Recomenda-se uma escuta humana antes de veiculação comercial.

A peça é uma composição vetorial 2D com fontes reproduzíveis em Python/Skia, não um projeto editável de After Effects. Não há footage ou modelagem 3D. Nenhuma publicação ou envio externo foi feito.

A declaração de composição original não é registro autoral nem parecer jurídico sobre exclusividade de material assistido por IA. Os direitos da marca T2S permanecem com seu titular.

REPRODUZIR O RENDER

Dependências Python fixadas em requirements.txt. As fontes e assets são os inputs locais; o render não precisa de rede. Neste workspace o venv e a biblioteca nativa local já estão preparados.

    .venv/bin/python src/build_all.py

Esse comando regenera instâncias das fontes, trilha, master de áudio, previews, vídeo, mux MP4, validação e manifesto. Os renders são serializados com flock no lock autorizado:

    /home/hermes/entregas/t2s-pods-model-comparison/render.lock

O compositor e o encoder usam uma thread. A biblioteca libEGL foi extraída localmente, sem instalar pacotes no sistema ou alterar serviços; src/bootstrap.py carrega somente a cópia em .local-libs/.

Para reconstruir as dependências em um workspace novo equivalente:

    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    apt-get download libegl1 libglvnd0
    dpkg-deb -x libegl1_1.7.0-1build1_amd64.deb .local-libs
    dpkg-deb -x libglvnd0_1.7.0-1build1_amd64.deb .local-libs
    .venv/bin/python src/build_all.py

Os nomes de pacotes acima correspondem à versão obtida nesta execução em Ubuntu noble; numa distribuição diferente, a dependência EGL/GLVND deve ser fornecida pela versão compatível do ambiente. Os .deb baixados foram preservados na raiz do workspace. O caminho do lock é específico deste experimento.

ARQUIVOS

final.mp4: entrega audiovisual.
README.md: instruções, decisões e limitações.
music-license.md: declaração de procedência do áudio.
manifest.json: fontes, assets, artefatos, versões e SHA-256.
../src/: compositor, síntese musical, render, verificação e scripts de reprodução.
../build/audio/: trilha, efeitos, premaster e master PCM.
review/: evidências de revisão.
