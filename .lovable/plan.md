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

## 3. O que os outros 4 dossiês confirmaram

Analisamos 3 dossiês Pacote 1 (Gizeli, Janine, Adriana) e 1 Pacote Completo Masculino, todos comparados com o Guia.

- **Estrutura estável:** a ordem Temperamento → Visagismo → Tipologia → Coloração se repete nas 3 clientes do Pacote 1, e a maior parte das páginas bate página a página com o Guia. O dossiê da Janine é uma versão mais antiga (biotipo em formato diferente, pontos de atenção por área como braços e papada) — confirma que a consultora evolui o layout, e que em divergência vale o Guia.
- **Biblioteca confirmada com valores reais:** os textos tipo A são idênticos entre clientes. Já vimos em uso: temperamentos Fleumático+Sanguíneo, Sanguíneo e Melancólico (das 4 combinações da biblioteca); rostos Oval, Retangular e Hexagonal de Base Reta/Diamante; biotipos femininos Triângulo e Ampulheta; cartelas Inverno Frio, Inverno Escuro e Outono Escuro.
- **Contraste calculado:** a régua tem 10 posições e a consultora marca onde ficam pele e cabelo; a "graduação" é a distância entre as marcas (ex.: 5 pontos = médio para alto; 4 = médio). Cálculo automático confirmado.
- **Biotipo por gênero:** no feminino, ombro/busto/cintura/quadril (Triângulo quando o quadril domina); no masculino, altura/peso/ombro/tórax/cintura/quadril (Trapézio quando ombro e tórax dominam). A ficha precisa de um modo masculino e um feminino.
- **Teste de coloração estruturado:** o método sazonal expandido registra etapas — profundeza, intensidade (brilhante x suave), temperatura (fria x quente) e teste dos vermelhos — com aprovação ✅/❌ por amostra. Essa entrada estruturada alimenta o diagnóstico e depois o ML de cartela.
- **Pacote Completo = escopo máximo:** além dos 4 blocos de análise, tem abertura (sobre o cliente, objetivos, desejo de imagem, moodboard), análise de estilo (estilo detectado → estilo desejado, mapa dos estilos) e um guia de estilo inteiro (cabelo/barba, estilo olfativo, óculos, acessórios, sapatos e cintos, uniforme, partes de cima/baixo, composição de looks, dicas, personal shopping, etiqueta, tecidos, resultados). Confirma a decisão: a ficha terá **blocos ligáveis por pacote** — Pacote 1 = análise; Pacote Completo = tudo.

**Páginas finais (51 em diante) — o que acrescentam:**

- **Final da coloração é quase todo tipo A por cartela:** estampas, animal print, metais, óculos por cor, pedras e maquiagem (blush, batom, sombra, rosto, esmaltes) se repetem para a mesma cartela. O que muda entre cartelas é previsível (ex.: Inverno = pratas brilhantes, fundo frio rosado, acabamento com brilho; Outono Escuro = dourados foscos, fundo quente, sem brilho).
- **Ajuste pelo contraste (regra automática):** o texto de estampas troca só o nível de contraste da cliente ("médio para alto" x "alto"). Um mesmo texto-base com a faixa de contraste preenchida pela régua resolve.
- **Catálogo de maquiagem = tabela de produtos:** cada item é marca + nome da cor + categoria + cartela (ex.: blush, batom, esmalte). Vira uma tabela no banco, fácil de atualizar quando um produto sai de linha — e vai para a biblioteca de conteúdo.
- **Guia de makes por família de estação:** existe um texto por grupo (Inverno, Outono…) sobre intensidade, brilho e quantas cores usar, além da lista por cartela.
- **Páginas opcionais (tipo C) que aparecem só em alguns dossiês:** "Guia do óculos" com avaliação de armações que a cliente já tem (formato e cor, com fotos) e página de cor de cabelo por cartela com recomendação de tonalidade. Viram **seções opcionais** que a consultora liga quando fizer sentido.
- **Guia de estilo (Pacote Completo) mistura A e C:** dicas de styling e medidas de caimento (barra da calça, bermuda, blazer, manga) e tecidos/fibras e etiqueta são textos fixos (A); composição de looks e personal shopping (lista de compras por categoria) são específicos do cliente (C/B).
- **Encerramento fixo:** "Desejo sucesso com suas descobertas!" + contatos, às vezes com uma citação de moda (ex.: Coco Chanel) — citação pode ser escolhida de uma lista.
- **Nada novo que mude a estrutura:** as páginas finais confirmam o modelo A/B/C e a organização em blocos; as únicas adições são as seções opcionais acima.

**Lote 1 — Apostilas de Coloração Pessoal (método Studio Immagine, de Luciana Ulrich, formadora da Helô):**

- **Roteiro do teste confirmado de ponta a ponta:** primeiro o contraste da pele (graduação de cinza 1–10; diferença de 1–3 graus = baixo, 4–5 = médio, 6+ = alto; fases claro/escuro e estampados), depois o TIP — Temperatura (fase 1, subtom e kit dos vermelhos: quente, neutra quente, neutra fria, fria), Intensidade (suave → brilhante, 5 níveis) e Profundidade (clara → escura, 5 níveis) — e por fim o kit das 12 estações. É exatamente essa sequência que a aba de coloração da ficha vai seguir.
- **Cada estação tem um TIP oficial** (Verão: fria/suave/clara; Outono: quente/suave/escura; Inverno: fria/brilhante/escura; Primavera: quente/brilhante/clara) mais recomendação de metais. Isso dá rótulos perfeitos para o **ML**: o modelo aprende a mapear as respostas do teste (TIP + contraste) na estação.
- **Regras de ouro do método:** repetir os pigmentos da cliente (harmonia) e analisar sempre por comparação, nunca uma cor isolada. Entra no system prompt da IA.
- **Conteúdo fixo para a biblioteca:** leitura dos tons de cabelo (base e nuances), guia de makes por estação, psicologia das cores, harmonias cromáticas (monocromático, análoga, complementar, tríade).
- **Direitos:** material da Studio Immagine — usar como conhecimento interno do sistema, sem reproduzir trechos longos na versão pública.

**Lote 2 — Visagismo (Apostila 1 do curso de especialização, Apostila 2 Senac e o livro "Visagismo Integrado", de Philip Hallawell):**

- **Base teórica do bloco Visagismo e do Temperamento:** o método liga linhas e formas (reta, curva, horizontal, vertical, diagonal) aos 4 temperamentos — sanguíneo, colérico, melancólico, fleumático. Isso explica por que o dossiê abre com temperamento e depois usa o rosto: o rosto "revela" o temperamento e o corte/maquiagem reforçam ou equilibram a imagem desejada.
- **Formatos de rosto confirmados para a biblioteca:** oval, redondo, quadrado, retangular, triangular, triangular invertido, hexagonal (e variações de base). Cada formato ganha texto A com a leitura do temperamento que ele transmite.
- **Partes do rosto e proporções:** terços, lado dominante, sobrancelhas, olhos, boca — dão as regras que a IA usa para rascunhar os textos C (sobrancelha, corte, interpretação dos terços).
- **Princípio "a forma segue a função":** primeiro entender o que a cliente quer transmitir, depois criar a imagem — vira pergunta da ficha ("imagem desejada") e regra do system prompt.
- **Análise da pele de Hallawell** (tipos com nomes próprios, cor de base e temperatura) complementa a coloração; entra como referência, sem substituir o método sazonal já usado pela consultora.
- **Aplicações extras** (corpo, postura, odontologia etc.) ficam fora do escopo do dossiê.
- **Direitos:** o livro é publicado — conhecimento interno para o RAG, sem reproduzir trechos longos na versão pública.

**Lote 3 — Tipologia Física (apostila do curso):**

- **Silhuetas oficiais da biblioteca:** Ideal, Ampulheta/X, Triângulo/A, Retângulo/H, Magro/I, Triângulo Invertido/Y e Oval — cada uma com texto A (características, tecidos, estampas, volumes).
- **Método de medição com varetas** (ombro→quadril, ângulo e distância da cintura): confirma que a ficha pode sugerir o biotipo pelas medidas, com a consultora confirmando na observação.
- **Lista de pontos de atenção pronta:** postura (ombros desalinhados/caídos, hiperlordose, cabeça projetada, hiperextensão do joelho etc.) e objetivos de proporção (parecer mais alta/baixa/magra/cheia, suavizar ombros largos...) — cada um com dicas fixas (tipo A) que alimentam a página de pontos de atenção do dossiê.
- **Elementos e princípios de design** (linhas, forma, cor, textura, padronagem; equilíbrio, proporção, escala, ritmo, destaque, harmonia) e **coordenação de cores, estampas, linhas e texturas**: conteúdo fixo que fundamenta as estratégias de proporção e o guia de estilo — base do RAG e dos rascunhos C.

**Lote 4 — Imagem e Estilo Masculino (apostila do curso):**

- **Modo masculino da ficha confirmado:** tipos físicos masculinos Retangular, Triângulo, Trapézio, Oval e Triângulo Invertido, com pontos de medição e listas "apostar / evitar" por tipo (tipo A).
- **7 estilos universais** (Esportivo/Natural, Elegante, Tradicional, Romântico, Dramático, Sedutor, Criativo): alimentam a análise de estilo do Pacote Completo (estilo detectado → desejado) — valem para os dois gêneros.
- **Guia de estilo masculino como biblioteca:** tipos de camisa (social, casual, esportiva), calças, sapatos (Derby, Oxford, Loafer, Monk, Brogue, Chelsea…), meias, tecidos, níveis de formalidade (baixa, média, alta), dress code corporativo e montagem de mala — textos fixos para as seções do guia de estilo.
- **Diferença feminino × masculino:** mesmo fluxo de sessão, com biblioteca e medidas próprias por gênero.

**Referência complementar — "Visagismo: Harmonia e Estética" (Philip Hallawell, Senac):**

- Livro de formação de base, pouco usado no dia a dia: composição e proporção, geometria da cabeça, formatos básicos do rosto, partes do rosto, teoria e uso da cor, tipos cromáticos e processo criativo.
- **Uso no sistema:** entra no RAG com peso menor, só como fundamentação teórica quando a IA precisar justificar uma recomendação; não gera páginas do dossiê. O arquivo é digitalizado (imagem), então precisa de leitura por OCR na preparação da base.
- **Direitos:** livro publicado — conhecimento interno, sem reproduzir trechos na versão pública.

**Base de conhecimento consolidada:** coloração (método sazonal expandido), visagismo (linhas × temperamentos, formatos e partes do rosto), tipologia física (silhuetas femininas e masculinas, pontos de atenção, design), estilo masculino e estilos universais, e a referência teórica de Hallawell. Com isso a biblioteca cobre todos os blocos do dossiê.

**Níveis da base de conhecimento (para o RAG e os agentes):**
1. **Biblioteca do dossiê** — textos fixos que viram páginas (prioridade máxima).
2. **Apostilas do método** — fundamentam os rascunhos da IA.
3. **Referências complementares** — outras publicações que não geram páginas, mas respondem consultas da consultora no chat e apoiam os agentes (peso menor na busca, sempre com a fonte citada).

**Referências complementares recebidas (nível 3):**
- **Grupo 1:** "Técnicas de Maquiagem, Visagismo e Imagem Pessoal" (livro de graduação UniCesumar) — maquiagem corretiva e por formato de rosto, apoia as páginas de maquiagem e os rascunhos; "Beleza Leve — O visagismo aplicado ao autoconhecimento" (Luci Fagundes Maciel) — temperamento, identidade e estilo, reforça o bloco Temperamento e o tom acolhedor da persona; "Aula de Styling 2024" (Centro Europeu) — elementos de design, cores que comunicam, regra de 2 cores por look e truques de styling, apoia o guia de estilo e as dicas de composição.
- **Grupo 2:** "Consultoria de Cores" — significado e psicologia de cada cor, nuances, proporções de cores no look e identidade cromática digital (cores nas redes sociais); responde perguntas do tipo "o que essa cor comunica?" e pode virar um serviço extra no futuro. "Personal Stylist — Apostila 2" — teorias da personalidade (psicodinâmica, humanista, Bandura) e como a personalidade influencia a imagem; fundamenta o bloco Temperamento. "Carolina Garcia — Imagem e Estilo" — portfólio comercial de outra consultora (serviços como análise cromática, detox de guarda-roupa, montagem de looks, personal shopper e planos de assinatura). Não entra no RAG técnico; serve como referência de mercado para o cadastro de serviços e pacotes da consultoria.
- **Grupo 3:** "Personal Stylist — Apostila 1" — fundamentos da consultoria, estilos pessoais, visagismo e dress code social e corporativo; apoia a análise de estilo e as orientações de dress code. "Consultoria de Imagem Homens" (Bruna Corralo) — estilo x moda e os 7 estilos universais aplicados ao homem, com peças e tecidos por estilo; reforça o modo masculino e o guia de estilo. "Empreendedorismo em Consultoria de Imagem" (Centro Europeu) — posicionamento, dores e ganhos do cliente, promessas do atendimento e fontes de renda; não entra no RAG técnico, mas orienta o cadastro de serviços e a visão do app como produto para consultoras.
- **Grupo 4:** "Fundamentos da Consultoria de Imagem" — história e conceito da profissão (imagem pessoal como mudança exterior e interior); contexto para o chat. "Guia de Looks Masculinos" (Ferricelli) — combinação de roupas e sapatos por ocasião (casual, esporte fino, social); alimenta a composição de looks e as dicas do guia de estilo masculino. "Manual da Consultora de Imagem" (Érica Minchin) — carreira, abordagem com o cliente, perguntas pontuais e atendimento; ajuda a montar o questionário pré-sessão e o tom de atendimento da persona.

## 4. Como a consultora vai usar o sistema

```text
[Cadastro da cliente] -> [Ficha da sessão em 4 abas] -> [Rascunho automático] -> [Revisão] -> [PDF final]
                          Temperamento                   A preenchido sozinho     edita os
                          Visagismo                      B inserido nos lugares   textos C e
                          Tipologia                      C sugerido pela IA       aprova
                          Coloração
```

**Área da consultora (backoffice)** com três partes:

1. **Biblioteca** (preenchida uma vez, evolui com o tempo): textos por temperamento (4), formato de rosto (~7), biotipo (~5), cartela (12), pontos de atenção, catálogo de produtos de maquiagem, banco de imagens de looks/moodboards. É também a **base do RAG**.
2. **Atendimentos**: a ficha de cada cliente, seguindo a mesma ordem do dossiê.
3. **Perfil da consultoria** (cadastro da consultora): nome, marca, contatos e tom de voz. O sistema é uma **base genérica**: qualquer consultor(a) se cadastra e o app assume a identidade dela (capa, contatos e a "voz" que a IA usa nos rascunhos). A Helô é o primeiro perfil; os textos da biblioteca começam com o conteúdo dela e cada consultora pode adaptar.

**Tipos de entrada** usados na ficha, para ser rápido na sessão:

- Seleção única (temperamento, formato de rosto, biotipo, cartela, lado dominante)
- Controles deslizantes (as 5 barras de temperamento em %, notas de contraste 1–10)
- Campos numéricos (medidas corporais, terços em cm) com cálculos automáticos
- Lista de marcar (pontos de atenção do corpo)
- Upload de fotos (rosto, perfil, corpo, teste de coloração)
- Texto livre com botão "sugerir com IA" (todas as análises tipo C)

Cada campo mostra ao lado **em qual página do dossiê ele aparece**, para a consultora ver o dossiê se formando.

## 5. Onde entra a IA (depois do básico funcionar)

| Camada | Uso no dossiê | Exigência da disciplina |
|---|---|---|
| Regras/cálculos | Pontuação de contraste, terço dominante, cor da armação | — |
| **ML** | Sugerir biotipo a partir das medidas e cartela a partir das notas de coloração | Etapa 2 — modelo preditivo |
| **RAG** | Busca na biblioteca para fundamentar os textos C | Etapa 1 — ChromaDB |
| **LLM** | Escrever rascunhos C (cabelo, sobrancelha, interpretação de terços) no tom da consultora | Etapa 1 — LLM + system prompt |
| **Agentes** | Agente Ficha (consulta dados), Agente Biblioteca (RAG), Agente Redator (monta o dossiê) | Etapa 2 |
| Revisão humana | Nada sai sem aprovação da consultora | Etapa 3 — segurança/guardrails |

## 6. Encaixe nas 3 etapas

- **Etapa 1 (sem. 6)** — ver checklist abaixo.
- **Etapa 2 (sem. 10)** — ML de cartela com ~400 clientes sintéticos, 3 agentes, Langfuse, DeepEval.
- **Etapa 3 (sem. 13)** — PDF final no layout guia, segurança, publicação, documentação e reflexão.

### Etapa 1 — o que a orientação exige x o que vamos entregar

Rubrica: 30% declaração CBL + justificativa; 70% sistema funcional (chat com streaming, session state, UX writing do domínio, system prompt específico, DuckDB com 2+ tabelas relacionadas consultáveis em linguagem natural, ChromaDB com 3+ documentos bem fatiados, RAG respondendo, chaves no .env). Nota zero se: não executa, cópia integral ou chave exposta.

| Exigência | Nossa entrega |
|---|---|
| Declaração CBL no README | Texto já pronto; justificativa escrita por você |
| App Streamlit com chat, streaming e session state | Copiloto da consultora: aba Chat + aba Ficha da sessão |
| CSVs 2+ tabelas relacionadas no DuckDB | consultoras, clientes, sessoes, medidas, teste_coloracao, coloracao (fictícios) |
| Consulta em linguagem natural (Text-to-SQL, visto na Unidade 2) | "Quantas clientes são Inverno Frio?", "Medidas da Cliente A" |
| 3+ documentos no ChromaDB (txtai/LangChain, Unidade 3) | Biblioteca A escrita por nós (temperamentos, rostos, biotipos, 12 estações) + resumos próprios das apostilas |
| System prompt do domínio | Persona "copiloto de consultoria de imagem", tom da consultora, nunca decide sozinho |
| .env.example, .gitignore, requirements.txt | Incluídos |
| Vídeo 3–5 min | Roteiro: 3 perguntas RAG + 2 consultas ao banco + rascunho de um texto C + aprendizados |

Fica para depois: PDF final, agentes, ML, fotos.

### Ferramentas: tudo gratuito, com código e dados na nuvem

| Parte | Escolha gratuita | Observação |
|---|---|---|
| Código | GitHub (repositório público, sem chaves) | Também serve como entrega da Etapa 1 |
| App | Streamlit Community Cloud | Publica direto do GitHub, sem custo; resolve a publicação da Etapa 3 |
| LLM | Gemini API (cota gratuita do Google AI Studio) | As assinaturas ChatGPT Pro e Gemini pago não dão acesso à API; a chave gratuita do AI Studio dá |
| Embeddings | Modelo local gratuito (sentence-transformers multilíngue) | Sem custo e sem limite de uso; roda também no Streamlit Cloud |
| Banco estruturado | DuckDB (arquivo .duckdb gerado a partir dos CSVs do repositório) | Fica junto com o app |
| Base vetorial | ChromaDB persistido em pasta do repositório | Indexado uma vez, lido pelo app |
| Observabilidade (Etapa 2) | Langfuse Cloud, plano gratuito | |
| Uso local | Ollama / LM Studio como alternativa de LLM offline; Codex e ChatGPT como apoio para escrever código | Um seletor no .env troca entre Gemini e Ollama |

Chaves só no .env (local) e no painel "Secrets" do Streamlit Cloud; o .env.example vai sem valores.

### Decisões da Etapa 1 (respondidas)

- **Escopo:** chat + ficha da sessão + rascunho de texto pela IA (não só o chat).
- **Demonstração:** você mesmo apresenta e usa o app no vídeo, com clientes fictícias.
- **Repositório:** público no GitHub (publicação gratuita no Streamlit Cloud).
- **Base de consulta:** nenhuma apostila entra inteira. Primeiro passo da implementação: gerar resumos próprios, um por tema (Coloração, Visagismo, Temperamento, Tipologia feminina, Tipologia masculina, Estilos universais, Maquiagem e acessórios, Styling e dress code), sem repetições e reescritos com palavras nossas, preservando o método e os termos técnicos. Esses resumos (arquivos .md) são os documentos indexados no ChromaDB, com a fonte citada em cada um. Você revisa os resumos antes de indexar.

### Ordem de trabalho da Etapa 1

0. Apresentação do plano em PowerPoint (.pptx, cerca de 12 slides): desafio CBL, o dossiê de trás para frente (tipos A/B/C), mapa do dossiê, base de conhecimento, como a consultora usa o sistema, onde entra a IA, ferramentas gratuitas, as 3 etapas e o cronograma da Etapa 1. Paleta inspirada nas cores do dossiê guia, sem dados reais de clientes.
1. Resumos temáticos das apostilas (base do RAG) + textos fixos da biblioteca.
2. CSVs fictícios (consultoras, clientes, sessões, medidas, teste de coloração, coloração) e carga no DuckDB.
3. Indexação no ChromaDB e pipeline RAG com Gemini.
4. App Streamlit: chat com streaming, consulta ao banco em linguagem natural, ficha da sessão e botão "sugerir com IA".
5. README com a declaração CBL (justificativa escrita por você), .env.example, .gitignore, requirements.txt.
6. Publicação no Streamlit Cloud e roteiro do vídeo.

## 7. Perguntas para a consultora (antes de construir)

1. Já vimos dois formatos — Pacote 1 (análise) e Pacote Completo (análise + guia de estilo). Faltam: existem outros pacotes intermediários e qual a ordem exata dos blocos em cada um?
2. Os textos fixos (tipo A) já existem em algum arquivo (Canva, Word)? Aproveitá-los adianta muito a biblioteca.
3. Onde ela monta hoje o dossiê (Canva?) — define se o PDF final copia o layout ou se exportamos para a ferramenta dela.
4. Quais informações ela coleta antes da sessão (questionário de temperamento?) — pode virar um formulário que a própria cliente preenche.
5. As imagens de looks e produtos são dela ou de terceiros? (Direitos de uso na versão pública.)

## Detalhes técnicos

- **Modelo de dados** (idêntico no DuckDB acadêmico e no banco do app web): `clientes` (com modo masculino/feminino), `sessoes` (pacote, status — blocos ligáveis por pacote), `abertura` (sobre, objetivos, desejo de imagem, moodboard — Pacote Completo), `temperamento` (primário, secundário, 5 percentuais), `visagismo` (régua de contraste com posições pele/cabelo, formato, terços, lado, sobrancelha, textos C), `medidas` (feminino: ombro, busto, cintura, quadril; masculino: altura, peso, ombro, tórax, cintura, quadril; tronco, pernas, biotipo), `teste_coloracao` (etapas profundeza, intensidade, temperatura, vermelhos — amostras ✅/❌), `coloracao` (cartela), `estilo` (detectado, desejado — Pacote Completo), `pontos_atencao`, `textos_gerados` (seção, rascunho IA, versão aprovada), `biblioteca` (categoria, chave, seção, texto, imagens — cobre também os blocos do guia de estilo).
- **Montagem**: cada página do dossiê vira um "modelo de seção" que recebe dados B, busca A na biblioteca pela chave (ex.: `cartela=outono_suave`, `secao=batons`) e insere C aprovado.
- **Streamlit** replica o fluxo com a mesma estrutura, para cumprir a rubrica (DuckDB + ChromaDB + LLM + RAG).
