# Copiloto de Consultoria de Imagem e Estilo — Plano das 3 Etapas

Projeto AI Factory (PUCPR). Abordagem híbrida aprovada: aplicação **Streamlit em Python** como entrega acadêmica (fiel à stack da rubrica) e um **app web aqui no Lovable** como vitrine pública do produto. Dados de clientes serão **fictícios**; os documentos técnicos seguem o padrão do dossiê HH_Pacote1.

## O que o sistema faz

A consultora cadastra a cliente e as medições da sessão (medidas corporais, contraste pele/cabelo/olhos, formato de rosto, respostas do questionário de temperamento). O copiloto:

1. Sugere classificações técnicas (temperamento, biotipo, cartela de coloração) com um modelo de ML — sempre como **sugestão**, nunca decisão final.
2. Consulta a base de conhecimento da consultora (RAG) para fundamentar recomendações de cabelo, maquiagem, decotes, óculos, combinações de cores.
3. Monta o rascunho do dossiê seguindo a estrutura do PDF de referência, seção por seção.
4. A consultora revisa, edita e aprova; então o dossiê é exportado em PDF.

## Etapa 1 — Engajar (semana 6)

Entregar o sistema base funcional com interface, LLM, dados e RAG.

- **Declaração CBL** no README (a que você já escreveu, com a justificativa pessoal mantida em suas palavras).
- **Dados estruturados (CSVs → DuckDB)**, mínimo 2 tabelas relacionadas — teremos 5:
  - `clientes` (id, nome fictício, idade, cidade, pacote contratado, data)
  - `sessoes` (id, cliente_id, data, status, consultora)
  - `medidas` (sessao_id, ombro, busto, cintura, quadril, altura, proporção superior/inferior)
  - `diagnosticos` (sessao_id, temperamento primário/secundário, formato de rosto, contraste, biotipo, cartela de coloração)
  - `dossies` (sessao_id, status de revisão, data de aprovação, tempo de preparo)
  - Volume: ~400 clientes sintéticos, gerados por script com regras coerentes (ex.: medidas compatíveis com o biotipo rotulado) para servir também de dataset de ML na Etapa 2.
- **Documentos para RAG (ChromaDB)**, no mínimo 3 — planejados 5:
  - Manual de Visagismo (temperamentos, formatos de rosto, terços e proporções)
  - Manual de Tipologia Física (biotipos, proporção corporal, decotes, comprimentos)
  - Manual de Coloração Pessoal (estações, cores universais, combinações, cores a evitar)
  - Guia de Detalhamento (cabelo, maquiagem, óculos, acessórios)
  - FAQ de atendimento e padrões de entrega dos pacotes
- **Pipeline RAG** com embeddings + busca semântica, respostas com citação da fonte.
- **Interface Streamlit**: cadastro de cliente/sessão, consulta de dados, chat com o copiloto, visualização do rascunho do dossiê.
- **System prompt** especializado: fala como assistente técnico da consultora, nunca inventa diagnóstico, sempre cita a seção do manual.
- **Higiene de repositório**: `.env.example`, `.gitignore`, `requirements.txt`, nenhuma chave no código.

## Etapa 2 — Investigar (semana 10)

- **Modelo preditivo**: classificação da **cartela de coloração pessoal** (12 estações → agrupadas em 4–6 classes para ter volume por classe), a partir de contraste, subtom de pele, profundidade de cabelo e olhos. Justificativa para a rubrica: é a tarefa que mais consome tempo de análise, tem alvo categórico claro e conecta diretamente à seção principal do dossiê. Alvo secundário se sobrar tempo: previsão de tempo de preparo do dossiê (regressão).
  - Treino com scikit-learn, comparação de 2–3 algoritmos, matriz de confusão, métricas por classe.
- **Agentes** (mínimo 2 tarefas além de responder perguntas) — planejados 3:
  - *Agente de Dados*: consulta DuckDB (histórico da cliente, medidas, estatísticas).
  - *Agente de Conhecimento*: busca RAG nos manuais e fundamenta recomendações.
  - *Agente Redator*: monta o rascunho do dossiê seção por seção, combinando diagnóstico + ML + RAG.
- **Observabilidade**: Langfuse instrumentando todas as chamadas de LLM (latência, custo, traces de ferramentas).
- **Testes**: golden dataset com ~30 perguntas do domínio + suite DeepEval (faithfulness e answer relevancy), com análise dos pontos fracos.
- **Relatório técnico** (700–1500 palavras) cobrindo dataset, modelo, agentes, observabilidade e testes.

## Etapa 3 — Agir (semana 13)

- **Segurança**: mascaramento de dados pessoais das clientes, guardrails contra prompt injection e contra o sistema emitir diagnóstico sem revisão humana, controle de acesso da consultora.
- **Publicação**: Streamlit Community Cloud (ou Hugging Face Spaces) com secrets em variáveis de ambiente; o app vitrine publicado pelo Lovable.
- **Exportação do dossiê em PDF** com o layout do arquivo de referência (capa, seções de Visagismo, Tipologia Física, Coloração Pessoal, moodboards e inspirações).
- **Documentação**: README completo, arquitetura, instruções de execução, vídeo/demonstração.
- **Reflexão crítica**: Parte A (o sistema resolve o desafio?), Parte B (o que funciona e o que não funciona, tecnicamente), Parte C (visão de futuro).

## Detalhes técnicos

**Entrega acadêmica (Python)** — `streamlit`, `duckdb`, `chromadb`, `scikit-learn`, `pandas`, `langfuse`, `deepeval`, `reportlab` (PDF), `python-dotenv`. Estrutura: `app/` (páginas Streamlit), `data/` (CSVs), `docs/` (fontes do RAG), `src/` (rag, agents, ml, db), `tests/`.

**Vitrine (Lovable)** — TanStack Start + React + Tailwind. Landing do produto, demonstração navegável do fluxo (formulário → diagnóstico sugerido → rascunho do dossiê) e visualização do dossiê no estilo da referência. Se quisermos que a vitrine seja funcional de verdade, ativamos Lovable Cloud para banco e busca vetorial; caso contrário ela roda com dados de exemplo.

## Sequência sugerida de trabalho

1. Gerador de dados sintéticos + os 5 documentos-base do RAG (fundação das 3 etapas).
2. Etapa 1: DuckDB + ChromaDB + RAG + Streamlit + system prompt.
3. Etapa 2: ML, agentes, Langfuse, DeepEval, relatório.
4. Etapa 3: segurança, export PDF, deploy, documentação e reflexão.
5. Vitrine no Lovable em paralelo, após a Etapa 1 estabilizar o fluxo.

## Fora deste plano por enquanto

- Análise automática de fotos do rosto (visão computacional) — fica como "visão de futuro" na Etapa 3.
- Integração com agenda/pagamentos.
