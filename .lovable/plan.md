# Copiloto de Consultoria de Imagem — Plano "de trás para frente"

Ponto de partida: o **dossiê final (Pacote 1, 65 páginas)**. Primeiro entendemos cada página, depois definimos como a consultora alimenta cada uma, e só então colocamos a IA por cima. Abordagem híbrida mantida: Streamlit (entrega acadêmica) + app web no Lovable (produto que a consultora usa). Dados de clientes fictícios.

**Regra de referência:** o Pacote 1 enviado agora é o **dossiê-base canônico** — estrutura, cores, fontes e formatação seguem sempre ele. Os próximos dossiês (masculinos e de outras clientes) servem apenas para extrair padrões de conteúdo e variações dos tipos A/B/C; em qualquer divergência de layout ou formatação, vale o Pacote 1. Dados pessoais reais desses arquivos ficam só como referência no chat — nada entra no app, que usa exemplos fictícios.

## 1. A grande descoberta do dossiê

Lendo as 65 páginas, fica claro que todo o conteúdo do dossiê pertence a um de três tipos. Separar esses três tipos é o que torna a automação possível, porque cada um é resolvido de um jeito diferente.

### Tipo A — Conteúdo fixo por categoria

**O que é:** textos e imagens que dependem só do *resultado* do diagnóstico, não da pessoa. Duas clientes com a mesma cartela Outono Suave recebem exatamente as mesmas páginas de cores, looks, estampas, metais, pedras e maquiagem.

**Exemplos reais no dossiê:**
- Temperamento Fleumático: "O fleumático é o tipo mais tranquilo, estável e racional…", com listas de características positivas, negativas e físicas (p.4–6). O mesmo vale para o Melancólico (p.8–9).
- Rosto Oval: "caracterizado por linhas curvas no contorno do rosto e perfil…" (p.13), e as regras de óculos, decotes e acessórios para esse formato.
- Corpo Ampulheta: "Sobre o corpo ampulheta", com tecidos indicados (algodão, seda, linho, jersey) e estampas (p.30).
- Cartela Outono Suave: moodboard, cores para abusar e evitar, harmonias no círculo cromático, looks por cor, estampas, metais foscos, pedras (granada, malaquita) e a lista de produtos de maquiagem com marca e nome (p.32–61).

**Como o sistema resolve:** a consultora escreve cada texto **uma única vez** numa biblioteca, organizado por categoria (4 temperamentos, cerca de 7 formatos de rosto, 5 biotipos, 12 cartelas). Quando ela escolhe "Outono Suave" na ficha, todas essas páginas entram sozinhas no dossiê. Essa biblioteca também vira a base de conhecimento que a IA consulta.

### Tipo B — Dados da cliente

**O que é:** números, notas e escolhas que a consultora registra durante a sessão. São curtos, mas mudam de cliente para cliente e alimentam cálculos.

**Exemplos reais no dossiê:**
- Medidas corporais: ombro 94, busto 85, cintura 69, quadril 91 cm (p.26), a partir das quais se chega ao biotipo Ampulheta.
- Terços do rosto: superior 8 cm, médio 6 cm, inferior 7,5 cm (p.15), indicando o terço dominante.
- Contraste: pele nota 4, cabelo nota 7, resultando em "médio para baixo contraste" (p.11).
- Percentuais de temperamento: Pensar 80%, Sentir 30%, Agir 20%, Comunicar 40%, Determinar 60% (p.3).
- Escolhas diretas: temperamento primário e secundário, formato de rosto, lado dominante (direito), cartela.
- Fotos: rosto, perfil, corpo inteiro para a régua de proporções, teste de coloração.

**Como o sistema resolve:** uma ficha de entrada rápida (campos numéricos, seleções, controles deslizantes, upload de fotos). O sistema faz os cálculos sozinho — pontuação de contraste, terço dominante, sugestão de biotipo — e coloca cada dado no lugar certo da página.

### Tipo C — Análise personalizada

**O que é:** o olhar profissional da consultora sobre *aquela* cliente específica. É a parte que mais exige conhecimento e que hoje é escrita do zero a cada dossiê.

**Exemplos reais no dossiê:**
- Cabelo: "O corte ideal é de comprimento médio, com movimento e leve repicado nas laterais a partir do queixo. Uma franja longa, na altura das têmporas…" e a cor das mechas em "loiro médio quente" (p.17–19).
- Sobrancelha: "Ambas estão corretas no comprimento porém no limite… na base interna, sempre reforçar com um pouco de sombra" (p.16).
- Interpretação dos terços: "O terço médio é o de menor proporção, e aliado aos olhos cerrados, mostra um afastamento das emoções…" (p.15).
- Pontos de atenção do corpo: "Para disfarçar canelas grossas: evitar roupas justas, usar calças retas e soltas…" (p.31).

**Como o sistema resolve:** hoje isso é 100% manual. No sistema, a IA lê os dados tipo B da cliente, consulta a biblioteca tipo A e **escreve um rascunho** no estilo da consultora. Ela lê, ajusta o que quiser e aprova. A decisão final continua sendo sempre dela.

### Resumo

| Tipo | Quem produz | Com que frequência | Solução no sistema |
|---|---|---|---|
| A. Fixo por categoria | Consultora | Uma vez, reaproveitado sempre | Biblioteca + preenchimento automático |
| B. Dados da cliente | Consultora na sessão | A cada atendimento, poucos minutos | Ficha de entrada + cálculos automáticos |
| C. Análise personalizada | Consultora (hoje) / IA como rascunho | A cada atendimento, parte mais demorada | Rascunho por IA + revisão e aprovação |

Estimativa: cerca de 70% do dossiê é tipo A, 15% tipo B e 15% tipo C. Ou seja: só com uma boa biblioteca e uma ficha de entrada já se elimina a maior parte do trabalho manual, **antes mesmo da IA**.

## 2. Mapa do dossiê — página por página

```text
BLOCO 0  Capa (p.1)                         B: nome da cliente, pacote
BLOCO 1  TEMPERAMENTO (p.2-9)
  p.2   Introdução                          A
  p.3   Diagnóstico primário + 5 barras %   B: tipo + Pensar/Sentir/Agir/Comunicar/Determinar (%)
  p.4-6 Primário: positivas/negativas/físico A (por temperamento: 4 textos)
  p.7   Diagnóstico secundário + tabela     B: tipo
  p.8-9 Secundário: descrição               A
BLOCO 2  VISAGISMO (p.10-24)
  p.11-12 Contraste                         B: notas pele/cabelo/olhos (1-10) -> pontuação e faixa calculadas
  p.13-14 Formato do rosto + perfil         B: formato (oval, redondo...) + fotos | A: texto do formato | C: observação do perfil
  p.15  Terços e proporções                 B: 3 medidas em cm -> dominante calculado | C: interpretação
  p.16  Lado dominante + sobrancelha        B: lado | C: orientação de sobrancelha
  p.17-19 Cabelo: corte / cor / finalização C (três textos) + fotos de referência
  p.20  Maquiagem de visagismo              A por formato de rosto + C
  p.21  Acessórios (brincos, colares)       A por formato + C
  p.22  Decotes                             A por formato
  p.23-24 Óculos: modelos e cor da armação  A por formato + regra por contraste (automática)
BLOCO 3  TIPOLOGIA FÍSICA (p.25-31)
  p.26  Medidas + biotipo                   B: ombro/busto/cintura/quadril -> biotipo sugerido (regra ou ML)
  p.27  Proporção tronco x pernas           B: medidas | C: frase de interpretação
  p.28  Estratégia de proporção             A por biotipo
  p.29  Régua de proporção corporal         B: foto da cliente + marcações (brinco, decote, cinto, blazer, saias, calças)
  p.30  "Sobre o corpo X"                   A por biotipo (tecidos, estampas, volumes)
  p.31  Pontos de atenção (ex. canelas)     B: selecionar pontos de uma lista | A: dicas por ponto
BLOCO 4  COLORAÇÃO PESSOAL (p.32-65)
  p.32  Diagnóstico da cartela              B: cartela (12 estações) + fotos do teste
  p.33  Moodboard da cartela                A (imagem por cartela)
  p.34  Cores universais                    A (igual para todas)
  p.35  Como combinar                       A por cartela
  p.36-37 Cores para evitar / abusar        A por cartela
  p.38-42 Círculo cromático e harmonias     A por cartela
  p.43-50 Inspirações de looks por cor      A por cartela (banco de imagens)
  p.51-53 Estampas e animal print           A por cartela + ajuste pelo contraste
  p.54-55 Metais e pedras                   A por cartela
  p.56-61 Maquiagem: blush, batom, sombra,
          rosto, esmaltes (com produtos)    A por cartela (catálogo de produtos)
BLOCO 5  Encerramento (p.62-65)             A: contatos da consultora
```

## 3. Como a consultora vai usar o sistema

```text
[Cadastro da cliente] -> [Ficha da sessão em 4 abas] -> [Rascunho automático] -> [Revisão] -> [PDF final]
                          Temperamento                   A preenchido sozinho     edita os
                          Visagismo                      B inserido nos lugares   textos C e
                          Tipologia                      C sugerido pela IA       aprova
                          Coloração
```

**Área da consultora (backoffice)** com duas partes:

1. **Biblioteca** (preenchida uma vez, evolui com o tempo): textos por temperamento (4), formato de rosto (~7), biotipo (~5), cartela (12), pontos de atenção, catálogo de produtos de maquiagem, banco de imagens de looks/moodboards. É também a **base do RAG**.
2. **Atendimentos**: a ficha de cada cliente, seguindo a mesma ordem do dossiê.

**Tipos de entrada** usados na ficha, para ser rápido na sessão:

- Seleção única (temperamento, formato de rosto, biotipo, cartela, lado dominante)
- Controles deslizantes (as 5 barras de temperamento em %, notas de contraste 1–10)
- Campos numéricos (medidas corporais, terços em cm) com cálculos automáticos
- Lista de marcar (pontos de atenção do corpo)
- Upload de fotos (rosto, perfil, corpo, teste de coloração)
- Texto livre com botão "sugerir com IA" (todas as análises tipo C)

Cada campo mostra ao lado **em qual página do dossiê ele aparece**, para a consultora ver o dossiê se formando.

## 4. Onde entra a IA (depois do básico funcionar)

| Camada | Uso no dossiê | Exigência da disciplina |
|---|---|---|
| Regras/cálculos | Pontuação de contraste, terço dominante, cor da armação | — |
| **ML** | Sugerir biotipo a partir das medidas e cartela a partir das notas de coloração | Etapa 2 — modelo preditivo |
| **RAG** | Busca na biblioteca para fundamentar os textos C | Etapa 1 — ChromaDB |
| **LLM** | Escrever rascunhos C (cabelo, sobrancelha, interpretação de terços) no tom da consultora | Etapa 1 — LLM + system prompt |
| **Agentes** | Agente Ficha (consulta dados), Agente Biblioteca (RAG), Agente Redator (monta o dossiê) | Etapa 2 |
| Revisão humana | Nada sai sem aprovação da consultora | Etapa 3 — segurança/guardrails |

## 5. Encaixe nas 3 etapas

- **Etapa 1 (sem. 6)** — Biblioteca de conteúdo (docs no ChromaDB), ficha da sessão (tabelas no DuckDB: clientes, sessões, temperamento, visagismo, medidas, coloração), chat RAG e rascunho C por LLM, montagem do dossiê em tela.
- **Etapa 2 (sem. 10)** — ML de biotipo/cartela com ~400 clientes sintéticos, 3 agentes, Langfuse, DeepEval.
- **Etapa 3 (sem. 13)** — PDF final no layout HH, segurança, publicação, documentação e reflexão.

## 6. Perguntas para a consultora (antes de construir)

1. Quais são os outros pacotes e quais blocos cada um inclui? (Assim a ficha liga/desliga blocos por pacote.)
2. Os textos fixos (tipo A) já existem em algum arquivo (Canva, Word)? Aproveitá-los adianta muito a biblioteca.
3. Onde ela monta hoje o dossiê (Canva?) — define se o PDF final copia o layout ou se exportamos para a ferramenta dela.
4. Quais informações ela coleta antes da sessão (questionário de temperamento?) — pode virar um formulário que a própria cliente preenche.
5. As imagens de looks e produtos são dela ou de terceiros? (Direitos de uso na versão pública.)

## Detalhes técnicos

- **Modelo de dados** (idêntico no DuckDB acadêmico e no banco do app web): `clientes`, `sessoes` (pacote, status), `temperamento` (primário, secundário, 5 percentuais), `visagismo` (contraste pele/cabelo/olhos, formato, terços, lado, textos C), `medidas` (ombro, busto, cintura, quadril, tronco, pernas, biotipo), `coloracao` (cartela), `pontos_atencao`, `textos_gerados` (seção, rascunho IA, versão aprovada), `biblioteca` (categoria, chave, seção, texto, imagens).
- **Montagem**: cada página do dossiê vira um "modelo de seção" que recebe dados B, busca A na biblioteca pela chave (ex.: `cartela=outono_suave`, `secao=batons`) e insere C aprovado.
- **Streamlit** replica o fluxo com a mesma estrutura, para cumprir a rubrica (DuckDB + ChromaDB + LLM + RAG).
