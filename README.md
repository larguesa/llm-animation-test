# LLM Animation Test: T2S AI-Native Delivery Pods

Cinco modelos de linguagem receberam o mesmo briefing para produzir um vídeo de motion graphics de 30 segundos, com identidade oficial da T2S, áudio e fontes editáveis. Este repositório reúne os vídeos originais, o processo, a contabilidade e um retrato da percepção do público.

> **Veja a crítica dos vídeos e a revelação dos modelos no [Desbugados #076](https://www.youtube.com/watch?v=YXr0z2-87PQ).**
>
> [5 MODELOS VS 1 ANÚNCIO: QUAL FEZ O MELHOR MOTION GRAPHICS? l DESAFIO AO VIVO | DESBUGADOS #076](https://www.youtube.com/watch?v=YXr0z2-87PQ)
>
> Ricardo registra que os resultados foram discutidos criticamente e os modelos revelados nesse episódio. Assista para acompanhar a avaliação dos apresentadores, separada dos testes técnicos documentados aqui.

**Repositório público, conforme verificação do GitHub em 01/10/2026.** A correspondência entre versões e modelos e a coleta de percepção estão documentadas. Esta atualização preserva a visibilidade encontrada, sem alterar configurações do repositório ou ativar GitHub Pages.

## Resumão do relatório

- **Produção:** cinco MP4s finais de 30 s, 1920×1080, 30 fps e áudio AAC, aprovados nas verificações técnicas registradas. A saída do Luna foi composta internamente em 1280×720 e ampliada, limitação documentada.
- **Gasto total dos candidatos:** USD 40.445492892, nas cinco chaves OpenRouter. MiMo teve o menor gasto, USD 0,330521967; Muse terminou mais rápido, em 47min17s. Tempos incluem filas, retomadas, renderização e correções, não somente inferência.
- **Percepção coletada em 30/09/2026, entre 15h08 e 15h10:** 33 likes, 36 comentários de 8 contas e 16 acertos brutos de modelo em 36 palpites, **44,4%**.
- **Mais likes e mais reconhecido neste retrato:** Opus 5.5, com 12 likes e 6/8 acertos. Astra teve 8 likes e 5/8 acertos. Muse não foi identificado corretamente nos seis comentários de sua versão.
- **Expectativa versus realidade:** todas as médias estimadas de tempo ficaram abaixo dos tempos reais. O gasto foi subestimado nas versões 1 a 4; para MiMo, a média estimada de USD 0,70 ficou acima do gasto real de USD 0,330521967.
- **Limite central:** uma execução por modelo e uma amostra voluntária pequena. Likes não são votos exclusivos. Não se comprovou que todos os palpites e suas edições ocorreram antes da revelação; não é ranking geral nem teste cego controlado.

[**Ler o relatório completo em Markdown**](report.md) · [**Baixar o relatório HTML (.zip)**](https://github.com/larguesa/llm-animation-test/raw/refs/heads/main/report-html.zip)

## Tempo e gasto por modelo, com os vídeos

| Versão | Modelo | Tempo total | Gasto da chave (USD) | Vídeo no YouTube | Original / fontes |
| --- | --- | --- | ---: | --- | --- |
| 1 | `openai/gpt-6-luna` | 01:27:47 | 0.467660 | [Versão 1](https://www.youtube.com/watch?v=DG9gIfH_3Hc) | [MP4](luna/luna-t2s-pods.mp4) / [ZIP](luna/luna-fontes.zip) |
| 2 | `openai/gpt-6-astra` | 01:36:14 | 10.607166 | [Versão 2](https://www.youtube.com/watch?v=IWdM82_2kN0) | [MP4](astra/astra-t2s-pods.mp4) / [ZIP](astra/astra-fontes.zip) |
| 3 | `anthropic/claude-opus-5.5` | 03:00:07 | 25.918514 | [Versão 3](https://www.youtube.com/watch?v=lE9gV8PbZ2w) | [MP4](opus/opus-t2s-pods.mp4) / [ZIP](opus/opus-fontes.zip) |
| 4 | `meta/muse-spark-1.3` | 00:47:17 | 3.121632 | [Versão 4](https://www.youtube.com/watch?v=5K7dABXSM94) | [MP4](muse/muse-t2s-pods.mp4) / [ZIP](muse/muse-fontes.zip) |
| 5 | `xiaomi/mimo-v2.6-pro` | 02:02:00 | 0.330522 | [Versão 5](https://www.youtube.com/watch?v=5FdPaSsJwsg) | [MP4](mimo/mimo-t2s-pods.mp4) / [ZIP](mimo/mimo-fontes.zip) |

A numeração é ordem de apresentação, não classificação. Os gastos acima são das chaves dedicadas, incluindo serviços auxiliares e correções; não incluem supervisão, diagnósticos, infraestrutura ou assinaturas. A tabela está arredondada a seis casas; valores originais no [resumo de produção](summary.json).

## Likes, comentários e palpites

| Vídeo | Likes | Comentários | Palpites de modelo | Acertos |
| --- | ---: | ---: | --- | ---: |
| [Versão 1](https://www.youtube.com/watch?v=DG9gIfH_3Hc) | 5 | 7 | Muse: 3; MiMo: 2; Luna: 2 | 2/7 |
| [Versão 2](https://www.youtube.com/watch?v=IWdM82_2kN0) | 8 | 8 | Astra: 5; Opus: 2; Muse: 1 | 5/8 |
| [Versão 3](https://www.youtube.com/watch?v=lE9gV8PbZ2w) | 12 | 8 | Opus: 6; Astra: 2 | 6/8 |
| [Versão 4](https://www.youtube.com/watch?v=5K7dABXSM94) | 4 | 6 | Luna: 4; MiMo: 2 | 0/6 |
| [Versão 5](https://www.youtube.com/watch?v=5FdPaSsJwsg) | 4 | 7 | MiMo: 3; Muse: 3; Astra: 1 | 3/7 |

Métricas são um retrato das páginas individuais no horário da coleta, não contadores em tempo real. O [relatório completo](report.md#8-vídeos-percepção-do-público-e-revelação-dos-modelos) compara as médias de tempo e custo com o real, explica o palpite “até 30 min” e registra as limitações da análise.

[Playlist numerada](https://www.youtube.com/playlist?list=PLSxq4U-bytMY) · [Dados pseudonimizados e cálculos da percepção](docs/percepcao-2026-09-30.json)

## Material disponível

- [Relatório completo](report.md): prompt integral, estratégia e procedimento por modelo, custos, consumo, validações, intervenções, percepção e limitações.
- [HTML atualizado para download (.zip)](https://github.com/larguesa/llm-animation-test/raw/refs/heads/main/report-html.zip). O ZIP contém somente `report.html`; para vídeos e imagens offline, extraia-o na raiz de uma cópia completa do repositório, mantendo os caminhos relativos.
- [Resumo original de produção](summary.json) e [dados da percepção](docs/percepcao-2026-09-30.json), mantidos separados para preservar os registros históricos.
- [Prompt original](prompt.txt), preservado byte a byte. SHA-256: `7684288063461022ad603973b1069536705504b2802c84f9fc4abd7467be9d8c`.
- [Página local dos vídeos](index.html): MP4s, posters, contact sheets, READMEs, declarações de música e ZIPs nas pastas de cada modelo.
- `sources/{slug}/`: conteúdo integral dos ZIPs, incluindo inputs oficiais, fontes, documentação e manifestos dos pacotes.
- [Notas de reprodução](docs/reproducao.md), [verificação histórica da preparação](verification.json) e [SHA256SUMS.txt](SHA256SUMS.txt), inventário atual de hashes.

Logs, históricos de agentes, chaves, ambientes virtuais e estado operacional bruto não estão no repositório. Os participantes aparecem somente como P01 a P08, sem nomes ou handles. Não foi validada equivalência audiovisual entre a transcodificação do YouTube e os MP4s originais.

## Tempo em segundos e definição de custo

| Versão | Modelo | Segundos |
| --- | --- | ---: |
| 1 | openai/gpt-6-luna | 5267 |
| 2 | openai/gpt-6-astra | 5774 |
| 3 | anthropic/claude-opus-5.5 | 10807 |
| 4 | meta/muse-spark-1.3 | 2837 |
| 5 | xiaomi/mimo-v2.6-pro | 7320 |

Custo é o gasto registrado na chave OpenRouter dedicada de cada candidato, incluindo serviços auxiliares e eventuais chamadas truncadas ou com erro cobradas. Não inclui supervisão, diagnósticos, infraestrutura ou assinaturas. Valores em dólares americanos, arredondados a seis casas; precisão original no campo `key_usage_total_usd` de cada candidato no [resumo estruturado](summary.json). Não é preço por token nem estimativa de uma nova execução.

Tempo total é `ended_at - started_at`, em UTC, incluindo filas, retries, pausas, renderização e correções dentro do intervalo. Não é latência pura do modelo nem tempo exclusivo de render. Preparação anterior e publicação posterior não integram esse cálculo. A numeração é ordem de apresentação, não classificação.

## Limitações e direitos

A validação original foi técnica e visual amostral, sem escuta humana integral. A crítica pública no episódio é outra evidência, não substitui nem amplia os testes originais. Estratégias são sínteses de READMEs e código, não transcrições do raciocínio interno. A reprodução em máquina limpa e bit a bit não foram demonstradas.

A marca T2S, fontes e outros inputs têm direitos próprios. Declarações de composição musical programática não equivalem a parecer jurídico ou registro de direitos. Não há licença genérica concedendo direitos sobre todo o repositório.

Verificar integridade local sem executar código dos candidatos:

```sh
sha256sum -c SHA256SUMS.txt
```

Para visualizar offline, abrir `index.html` ou `report.html` em navegador local.
