# LLM Animation Test: T2S AI-Native Delivery Pods

**Repositório privado. Deve permanecer privado até autorização futura explícita de Ricardo.** A correspondência entre números e modelos abaixo é informação privada do experimento. Não compartilhar este README, relatório, JSON, fontes ou nomes dos arquivos com participantes do teste cego antes do encerramento da coleta.

Comparação documental de cinco execuções que produziram vídeos de motion graphics a partir do mesmo briefing. Não é um ranking geral de modelos. Os vídeos originais estão preservados sem alterações.

## Material disponível

- [Relatório completo em Markdown](report.md), com prompt integral, estratégia e procedimento por modelo, custos, consumo, validações, intervenções e limitações.
- [Baixar o relatório HTML (.zip)](https://github.com/larguesa/llm-animation-test/raw/refs/heads/main/report-html.zip), contendo o `report.html` original, sem alterações.
- [Resumo estruturado](summary.json), com tempos e dados do experimento.
- [Prompt original](prompt.txt), preservado byte a byte. SHA-256: `7684288063461022ad603973b1069536705504b2802c84f9fc4abd7467be9d8c`.
- [Página local dos vídeos](index.html), cinco MP4s, posters, contact sheets, READMEs, declarações de música e ZIPs nas pastas de cada modelo.
- `sources/{slug}/`: conteúdo integral dos ZIPs, incluindo inputs oficiais, fontes, documentação e manifestos dos pacotes.
- [Notas de reprodução](docs/reproducao.md) e [verificação local](verification.json).
- [SHA256SUMS.txt](SHA256SUMS.txt): hashes de todos os arquivos do repositório, exceto o próprio manifesto e metadados `.git`.

O download do HTML requer login no GitHub e acesso ao repositório privado. O ZIP contém somente o relatório. Para usar seus vídeos e imagens offline, extraia `report.html` na raiz de uma cópia completa deste repositório, mantendo os caminhos relativos.

O conteúdo da pasta `public` da entrega foi copiado diretamente para a raiz deste repositório. Essa disposição mantém os links relativos de `report.html` e `index.html` sem duplicar os MP4s. Os logs, históricos, chaves, ambientes virtuais e estado operacional bruto não foram copiados. Os READMEs e manifestos dos candidatos podem citar esses arquivos históricos, mas isso não significa que estejam incluídos aqui.

## Ordem privada, tempo total e custo

| Número | Modelo | Tempo total | Segundos | Custo (USD) | Vídeo original | Fontes |
|---|---|---|---:|---:|---|---|
| 1 | openai/gpt-6-luna | 01:27:47 | 5267 | 0.467660 | [MP4](luna/luna-t2s-pods.mp4) | [ZIP](luna/luna-fontes.zip) |
| 2 | openai/gpt-6-astra | 01:36:14 | 5774 | 10.607166 | [MP4](astra/astra-t2s-pods.mp4) | [ZIP](astra/astra-fontes.zip) |
| 3 | anthropic/claude-opus-5.5 | 03:00:07 | 10807 | 25.918514 | [MP4](opus/opus-t2s-pods.mp4) | [ZIP](opus/opus-fontes.zip) |
| 4 | meta/muse-spark-1.3 | 00:47:17 | 2837 | 3.121632 | [MP4](muse/muse-t2s-pods.mp4) | [ZIP](muse/muse-fontes.zip) |
| 5 | xiaomi/mimo-v2.6-pro | 02:02:00 | 7320 | 0.330522 | [MP4](mimo/mimo-t2s-pods.mp4) | [ZIP](mimo/mimo-fontes.zip) |

Custo é o gasto registrado na chave OpenRouter dedicada de cada candidato, incluindo serviços auxiliares e eventuais chamadas truncadas ou com erro cobradas. Não inclui supervisão, diagnósticos, infraestrutura ou assinaturas. Valores em dólares americanos, arredondados a seis casas; precisão original no campo `key_usage_total_usd` de cada candidato no [resumo estruturado](summary.json). Não é preço por token nem estimativa de uma nova execução.

Tempo total é `ended_at - started_at`, em UTC, incluindo filas, retries, pausas, renderização e correções dentro do intervalo. Não é latência pura do modelo nem tempo exclusivo de render. Preparação anterior e publicação posterior não integram esse cálculo. A numeração é ordem de apresentação, não classificação.

## Playlist e teste cego futuro

Playlist literal fornecida pelo usuário: https://www.youtube.com/playlist?list=PLSxq4U-bytMY

Playlist verificada em Chrome: título **T2S AI-Native Pod Test**, autor **Ricardo Pupo Larguesa**, visibilidade **Público** e cinco vídeos, de Version 1 a Version 5, nessa ordem. Não foi realizada comparação audiovisual do YouTube com os MP4s originais. Não se afirma equivalência byte a byte, de áudio ou de imagem após a transcodificação do YouTube.

| Versão | Link do vídeo |
|---|---|
| Version 1 | https://www.youtube.com/watch?v=DG9gIfH_3Hc |
| Version 2 | https://www.youtube.com/watch?v=IWdM82_2kN0 |
| Version 3 | https://www.youtube.com/watch?v=lE9gV8PbZ2w |
| Version 4 | https://www.youtube.com/watch?v=5K7dABXSM94 |
| Version 5 | https://www.youtube.com/watch?v=5FdPaSsJwsg |

Repositório privado: https://github.com/larguesa/llm-animation-test.

**Coleta e resultados de percepção estão pendentes.** Não há vencedor de preferência humana, taxa de acerto dos palpites ou resultado de teste cego calculado neste repositório.

### Plano simples de coleta, sem sistema novo

1. Antes de divulgar, definir janela de coleta, público-alvo e perguntas. Exibir apenas Version 1 a Version 5, sem nomes de modelos, custos, tempos, fontes ou links deste relatório.
2. Pedir uma versão favorita, justificativa curta e, separadamente, palpite do modelo por versão com confiança opcional. Não revelar a correspondência durante a coleta.
3. Em uma planilha manual, registrar data/hora de coleta, versão, likes e quantidade de comentários visíveis no mesmo momento. Registrar opiniões e palpites consentidos com identificadores pseudônimos; não publicar nomes de comentaristas por padrão.
4. Distinguir likes agregados, comentários qualitativos e respostas individuais. Não tratar likes como votos únicos nem inferir ausência de preferência a partir da ausência de like. Documentar dados ocultos, indisponíveis e respostas duplicadas.
5. Encerrar a janela antes de revelar os modelos. Consolidar contagens, denominadores, temas das justificativas e acertos dos palpites, sem imputar valores ausentes. Publicar resultados e correspondência somente após autorização.

### Riscos de viés e de quebra do cegamento

O relatório público anterior já revela as identidades dos modelos e pode ser encontrado ou ter sido visto pelos participantes. Tornar este repositório privado não desfaz essa exposição. Quem teve acesso prévio deve ser identificado por autodeclaração e analisado separadamente, sem alegar cegamento perfeito.

A ordem fixa 1 a 5 traz efeitos de primazia e recência. Em uma avaliação controlada futura, variar a ordem entre participantes quando viável, mantendo o identificador de cada versão. Recomendação algorítmica, divulgação desigual, audiência prévia, horário, thumbnail, reprodução automática, equipamento, volume, tela e compressão do YouTube também podem influenciar respostas. Likes e comentários visíveis criam prova social e podem contaminar palpites. Uma amostra voluntária pequena não representa todos os públicos e uma execução por modelo não sustenta inferência causal geral.

## Limitações e direitos

A avaliação anterior foi técnica e visual amostral, sem escuta humana integral. Estratégias são sínteses de READMEs e código, não transcrições do raciocínio interno. Algumas declarações dos candidatos são mais amplas que a validação independente; prevalecem as ressalvas do relatório. A reconstrução em máquina limpa não foi testada e não se promete reprodução bit a bit.

Os inputs congelados incluem a marca T2S e fontes com licenças próprias. As declarações de composição musical programática não equivalem a parecer jurídico ou registro de direitos. Não há licença genérica concedendo direitos sobre todo o repositório.

Verificar integridade local sem executar código dos candidatos:

```sh
sha256sum -c SHA256SUMS.txt
```

Para visualizar, abrir `index.html` ou `report.html` em navegador local. Não publicar este diretório nem ativar GitHub Pages durante o teste cego.
