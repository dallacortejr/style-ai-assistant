# Fichas de preenchimento com base nos dossiês da Heloísa

## Sobre o botão "Nova conversa no assistente"
Ele já funciona: apaga o histórico de perguntas da aba **Metodologia**. Como fica na barra lateral, longe do chat, parece que não faz nada. Proposta: tirar da barra lateral e colocar como "Limpar conversa" dentro da aba Metodologia, logo acima do chat.

## Cruzamento dos dossiês (Pacote 1 guia + exemplos + Completo Masculino)
Todo dado que a Heloísa escreve no dossiê vem de uma de duas fontes. As fichas reproduzem essas fontes, na ordem em que aparecem no dossiê.

### Ficha 1 — Questionário da cliente ("o que ela trouxe")
- Identificação fictícia, modo (feminino/masculino), data da sessão, pacote
- **Objetivos / intenção de imagem** (ex.: "transmitir segurança, jovialidade")
- **Principais dúvidas e queixas** (ex.: corte, óculos, barba; "pochete")
- Rotina e ocasiões frequentes (trabalho, eventos, dia a dia)
- Estilo com que se identifica hoje e peças que ama/evita
- Cuidados atuais: cabelo (cor, química, finalização), maquiagem do dia a dia, barba (masc.)
- Uso de óculos (grau/sol) e acessórios

### Ficha 2 — Avaliação técnica do consultor (na sessão)
**Temperamento**
- Primário e secundário (sanguíneo, colérico, melancólico, fleumático) + percentuais

**Visagismo**
- Contraste: posição da pele e do cabelo na escala → graus → faixa (baixo/médio/alto)
- Formato do rosto (oval, redondo, quadrado, retangular, triangular, coração, hexagonal) + observação do perfil (ex.: queixo retraído/projetado)
- Terços em cm (superior, médio, inferior) → terço dominante e menor
- Lado dominante (direito/esquerdo)
- Sobrancelha: comprimento, base, arqueamento (observação)
- Cabelo: corte atual, cor natural, finalização; barba (masc.)

**Tipologia física**
- Fem.: altura, ombro, busto, cintura, quadril; masc.: altura, peso, ombro, tórax, cintura, quadril
- Tronco × pernas (curto/padrão/longo) → biotipo sugerido e confirmado
- Pontos de atenção (canelas, braços, abdômen, ombros, altura, postura)

**Coloração pessoal**
- Teste TIP: temperatura, intensidade, profundidade, vermelhos, contraste observado
- Cartela sugerida (12 estações) e confirmada; metais (dourado/prata/cobre, fosco/brilho)

**Estilo** (pacotes com análise de estilo)
- Estilo detectado e estilo desejado (principal + toques)

## Como entra no app
- Nova pílula **"Fichas"** antes de "Dossiê da cliente": duas sub-pílulas, *Questionário da cliente* e *Avaliação técnica*.
- Os campos mostrados seguem o pacote contratado (Pacote 1 = temperamento, visagismo, tipologia, coloração; estilo só nos pacotes que o entregam) e o modo feminino/masculino.
- Cálculos automáticos já usados nos dossiês: contraste (pele × cabelo), terço dominante, biotipo sugerido pelas medidas — sempre editáveis pelo consultor.
- A **Ficha** do topo passa a mostrar o que foi preenchido; os rascunhos das páginas do dossiê usam esses dados + metodologia.
- Tudo salvo na pasta `.zip` da cliente (`ficha.json`), nunca no banco nem no GitHub. As 8 clientes de exemplo vêm pré-preenchidas com dados fictícios.

## Detalhes técnicos
- Novo módulo `academic/fichas.py` com a definição dos campos (tipo, opções, seção, pacotes, modo) para a tela ser gerada a partir dele.
- Estado em `st.session_state["ficha_{sid}"]`; `ficha.json` ganha `questionario` e `avaliacao` (versão 2, lendo também a versão 1).
- Prompt de "Sugerir texto desta página" passa a receber os campos da página correspondente.
- CSVs fictícios ganham colunas novas (terços, lado dominante, perfil, estilo) e `init_db.py` é atualizado.
