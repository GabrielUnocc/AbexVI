# PROMPT PARA O CHAT DO CLAUDE: CRIAR SLIDES DA AV1

Cole este prompt inteiro no chat do Claude (claude.ai) para gerar os slides.

---

Preciso que você crie o conteúdo completo de uma apresentação de slides para a AV1 de um projeto universitário de análise de dados. Vou te passar tudo: contexto, estrutura exigida pelo professor, dados reais da análise, decisões tomadas e o que deve constar em cada slide. No final, quero também anotações de apresentação para a equipe ler antes de subir ao palco.

---

## CONTEXTO DO PROJETO

- **Curso:** Sistemas de Informação, Unochapecó, ABEX VI: Projeto Integrado III
- **Professor:** Mateus Henrique Zeiser
- **Equipe:** Gabriel Victor Rosário, João Wictor Decarli, Rafael Lucas Rockenbach, Bernardo Dal Piva Bernardi
- **Data da apresentação:** 15/10/2026
- **Tema:** Análise de fatores associados à gravidade de acidentes em rodovias federais da Região Sul (SC, PR, RS)
- **Pergunta central:** Quais fatores de contexto estão associados à maior gravidade dos acidentes?
- **Variável de desfecho:** `classificacao_acidente` e a variável derivada `grave_ou_fatal` (1 se feridos graves > 0 ou mortos > 0)
- **Públicos-alvo:** PRF (primário) e DNIT (secundário)
- **Fonte dos dados:** Portal de dados abertos da PRF (portal.prf.gov.br/dados-abertos-acidentes), base "por ocorrência" (datatran), CSV

---

## REGRAS DO PROFESSOR (OBRIGATÓRIAS — siga à risca)

O professor avalia o processo e o raciocínio, não a quantidade de gráficos. As regras são:

1. **Um gráfico, uma pergunta, uma frase.** Cada slide de achado responde a UMA pergunta do projeto e vem com UMA interpretação escrita.
2. **Estrutura de cada achado:** Pergunta → Evidência (dados) → Interpretação → Limitação → Próximo passo.
3. **Gráfico explicativo, não exploratório:** título que AFIRMA o achado (não o nome da variável), eixos nomeados em português, no máximo uma cor de destaque (resto em cinza), linha de referência (média ou total), n e fonte indicados.
4. **Use taxas e percentuais, nunca contagens absolutas** ao comparar grupos de tamanhos diferentes.
5. **Verbos seguros nas conclusões:** "é maior/menor em", "se concentra em", "está associado a", "tende a", "variou de...para...". NUNCA use: causa, provoca, faz com que, prova que, sempre, nunca.
6. **Declare limitações abertamente** — o professor considera isso sinal de maturidade.
7. **Não mostrar código nem df.head()** como resultado.
8. **4 a 6 gráficos explicativos** com o mesmo padrão visual.

---

## ESTRUTURA EXIGIDA (roteiro sugerido pelo professor)

| Slide | Tema | O que mostrar |
|---|---|---|
| 1 | Capa | Título, equipe, data, instituição |
| 2 | Problema e público | Problema investigado, quem se beneficia, objetivo |
| 3 | Dados | Fonte, confiabilidade, período, granularidade, tamanho da base |
| 4 | Preparação dos dados | Decisões de tratamento, antes/depois |
| 5-9 | Achados (4 a 5 slides) | Um gráfico explicativo + uma frase por slide |
| 10 | Conclusões parciais | O que já dá para afirmar e o que ainda não dá |
| 11 | Limitações e próximos passos | Qualidade dos dados, hipóteses, ML e BI |

---

## DADOS REAIS DA ANÁLISE (use estes números exatos)

### Base de dados
- 8.703 acidentes registrados, janeiro a maio de 2026
- Santa Catarina: 3.538 (40,6%), Paraná: 3.254 (37,4%), Rio Grande do Sul: 1.911 (22,0%)
- 30 colunas originais; 51 colunas após pré-processamento
- Sem duplicatas no identificador `id`
- Total de mortos no período: 531 | Feridos graves: 2.165 | Feridos leves: 7.737

### Variável principal (classificacao_acidente)
- Com Vítimas Feridas: 6.846 (78,7%)
- Sem Vítimas: 1.406 (16,2%)
- Com Vítimas Fatais: 451 (5,2%)
- Variável derivada `grave_ou_fatal`: 2.137 acidentes (24,6%) resultaram em vítima grave ou fatal

### Achado 1: Colisão frontal concentra a maior letalidade
Índice de letalidade (mortos por 100 acidentes) por tipo de acidente:
- Colisão frontal: 37,1 (534 casos, 198 mortos)
- Atropelamento de pedestre: 30,0 (267 casos, 80 mortos)
- Atropelamento de animal: 7,0
- Saída de leito carroçável: 4,0 (mais frequente, 1.414 casos, mas menos letal)
- Colisão traseira: 3,8 (mais comum, 1.665 casos)
- Média geral: 6,1 mortos por 100 acidentes

### Achado 2: Pista simples está associada a maior gravidade
Proporção de acidentes graves ou fatais por tipo de pista:
- Pista simples: 29,1% (maioria das rodovias do interior)
- Pista múltipla: 21,8%
- Pista dupla: 20,2%

### Achado 3: Área rural concentra mais desfechos graves
Proporção de acidentes graves ou fatais por contexto de uso do solo:
- Área rural (uso_solo = Não): 26,6%
- Área urbana (uso_solo = Sim): 22,0%

### Achado 4: Período do amanhecer concentra maior proporção de graves
Proporção de acidentes graves ou fatais por fase do dia:
- Amanhecer (nascer do sol): 29,1%
- Plena noite: 26,6%
- Anoitecer: 24,6%
- Pleno dia: 23,0%

### Achado 5: Falha de atenção domina as causas, mas álcool é desproporcional
Distribuição por macrocausa:
- Falha de atenção ou reação: 4.652 acidentes (53,5%)
- Comportamento de risco: 1.440 (16,5%)
- Outras: 880 (10,1%)
- Álcool ou substâncias: 563 (6,5%)
- Condição do veículo: 503 (5,8%)
- Infração de trânsito: 236 (2,7%)
- Condição da via ou ambiente: 194 (2,2%)
- Fator externo: 136 (1,6%)
- Pedestre ou ciclista: 99 (1,1%)

Top causas individuais: Ausência de reação do condutor (1.365), Reação tardia ou ineficiente (1.336), Acessar a via sem observar presença de outros veículos (944), Ingestão de álcool (555), Velocidade incompatível (531).

---

## DECISÕES DE PRÉ-PROCESSAMENTO TOMADAS

Estas decisões devem aparecer no slide de Preparação com justificativa:

| Decisão | Problema | Solução | Registros afetados |
|---|---|---|---|
| D1 | Período disponível é jan-mai/2026 (não 2018 em diante como planejado) | Trabalhar com 2026 e declarar como limitação | Toda a base |
| D2 | Foco da análise | Gravidade geral dos acidentes (não comparação entre estados) | Toda a base |
| D3 | Variável-alvo para o modelo ML | Binário: `grave_ou_fatal` (feridos graves > 0 OU mortos > 0) | 8.703 linhas |
| D4 faixas | `horario` era texto contínuo | Criadas faixas: Madrugada (0-5h), Manhã (6-11h), Tarde (12-17h), Noite (18-23h) | 8.703 linhas |
| D4 causas | 65 categorias em `causa_acidente`, muitas raras | Agrupadas em 8 macrocausas com base em frequência e letalidade | 8.703 linhas |
| D5 | "Ignorado" e "Não Informado" são ausências disfarçadas | Convertidos para NaN (ausência explícita) | 83 registros |
| T1 | `data_inversa`, `km`, `latitude`, `longitude` estavam como texto | Convertidos para datetime e numérico | 8.703 linhas |
| T2 | `tracado_via` era multivalorado separado por ";" | Normalizado e expandido em 12 colunas dummies binárias | 8.703 linhas |
| T3 | Valores extremos em `pessoas` (máx 50) e `mortos` (máx 11) | Mantidos: são casos reais (ônibus) e os mais relevantes para o projeto | 0 removidos |

Antes: 8.703 linhas x 30 colunas. Depois: 8.703 linhas x 51 colunas. Nenhuma linha removida.

---

## CONCLUSÃO PARCIAL (use verbos seguros)

Com base nos dados de jan-mai/2026 para rodovias federais da Região Sul:

- A colisão frontal concentra a maior letalidade relativa (37,1 mortos por 100 acidentes), muito acima da média geral de 6,1, apesar de representar apenas 6,1% dos casos.
- Acidentes em pista simples estão associados a proporção de graves ou fatais 44% maior do que em pista dupla (29,1% vs 20,2%).
- O período do amanhecer tende a concentrar maior proporção de desfechos graves (29,1%) em comparação ao pleno dia (23,0%).
- A macrocausa "Falha de atenção ou reação" domina em frequência (53,5%), mas ações focadas em colisão frontal e pista simples podem ter maior impacto na redução de mortos.

---

## LIMITAÇÕES A DECLARAR

1. A base cobre apenas 5 meses (jan-mai/2026). Sazonalidade e feriados podem distorcer os padrões.
2. Sem dados de volume de tráfego: não é possível calcular risco por quilômetro percorrido. Rodovias mais movimentadas têm mais acidentes simplesmente por terem mais veículos.
3. Cobre apenas rodovias federais registradas pela PRF. Rodovias estaduais e trânsito urbano não estão incluídos.
4. `causa_acidente` depende do julgamento do policial no registro: pode ter variação entre turnos e regiões.

---

## PRÓXIMOS PASSOS

- Notebook 04 (modelo ML): classificação binária `grave_ou_fatal` com regressão logística, árvore de decisão e random forest. Só usa variáveis de contexto (sem vazamento de dados).
- Notebook 05 (BI): exportação para Looker Studio com KPIs: total de acidentes, total de mortos, letalidade por 100 acidentes, % grave ou fatal, trechos críticos por BR e faixa de km.
- AV2 em 03/12/2026: solução completa com modelo e dashboard.

---

## O QUE EU QUERO QUE VOCÊ PRODUZA

### 1. Roteiro completo dos slides

Para cada slide, escreva:
- **Título do slide** (afirma o achado, não o nome da variável)
- **Conteúdo principal** (texto, tabela, ou descrição detalhada do gráfico que deve ser inserido)
- Para slides de achado: siga a estrutura Pergunta / Evidência / Interpretação / Limitação / Próximo passo
- Marque com `[INSERIR GRÁFICO: descrição do gráfico]` onde a equipe vai colar a figura

Os slides de achado que precisam de gráfico são:
- Achado 1: barras horizontais de letalidade por tipo de acidente, destacando colisão frontal em vermelho e os demais em cinza, com linha de referência na média (6,1), n de cada tipo, título que afirma o achado
- Achado 2: barras horizontais com % de grave/fatal por tipo de pista (simples, dupla, múltipla), linha de referência na média geral (24,6%)
- Achado 3: barras horizontais com % de grave/fatal por fase do dia (amanhecer, plena noite, anoitecer, pleno dia), linha de referência na média (24,6%)
- Achado 4: barras horizontais com % de grave/fatal por uso do solo (rural vs urbano)
- Achado 5: barras horizontais com frequência das macrocausas em %, ordenadas, cor de destaque no maior grupo

### 2. Slide de ficha do projeto (Passo 1 da oficina)

Preencha a ficha com os dados do projeto:
- Problema ou demanda
- Parceiro ou público beneficiado
- Fonte(s) dos dados
- Licença, autorização e cuidados éticos
- Granularidade e período
- Tamanho da base
- Variável principal

### 3. Slide de decisões de tratamento

Mostre o antes/depois da base e as principais decisões em formato visual (tabela ou lista), seguindo o que o professor pede no Passo 2 da oficina.

### 4. Quadro de achados (Passo 4 da oficina)

Produza o quadro com as colunas: # | Pergunta | Gráfico | Achado (frase) | Limitação | Próximo passo. Preencha uma linha para cada um dos 4-5 achados acima.

### 5. Anotações de apresentação (IMPORTANTE)

Depois dos slides, escreva um bloco chamado "ANOTAÇÕES PARA A EQUIPE LER ANTES DE APRESENTAR". Deve conter:
- Para cada slide, de 3 a 5 frases que a pessoa responsável por aquele slide deve ter na cabeça (não para ler, mas para saber de cor)
- Os números e percentuais mais importantes para não errar em voz alta
- As armadilhas que o professor pode questionar e como responder (ex: "por que não usar contagem absoluta?", "isso prova que a pista simples causa mais mortes?")
- Uma dica de postura e ritmo para cada membro da equipe
- A frase de abertura e a frase de encerramento sugeridas

---

## RESTRIÇÕES DE ESTILO

- Português do Brasil em tudo
- Sem travessão (use vírgula, dois-pontos ou parênteses)
- Títulos de slides afirmam o achado: "Colisão frontal concentra 37 mortos por 100 acidentes" e não "Letalidade por tipo de acidente"
- Conclusões usam verbos seguros: está associado a, se concentra em, tende a
- Nenhum slide mostra código Python
- Gráficos sempre com título, eixos nomeados, n e fonte

---

Produza o conteúdo completo agora, slide por slide, seguindo exatamente a estrutura acima.
