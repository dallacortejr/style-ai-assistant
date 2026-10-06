# Registro inicial da consolidação — histórico

Este registro descreve o estado ANTES da escolha React. A documentação atual começa no README e em docs/MIGRACAO.md. A decisão pendente registrada abaixo foi resolvida pelo usuário em favor de React.

# Integração das bases — 05/10/2026

## Estado real desta cópia

Esta é uma base de trabalho consolidada, ainda sem integração funcional ou conversão de interface. A raiz preserva o projeto do ZIP; `previous/` preserva código selecionado do aplicativo anterior. Os aplicativos ainda possuem modelos de dados e fluxos diferentes.

Fontes consultadas:
- ZIP: `C:/Users/dalla/OneDrive/Documentos/LUIZ/PESSOAIS/PROJETOS/ESILO_CONSULTORIA_IMAGEM/project-handoff.zip`.
- Projeto anterior: `C:/Users/dalla/Documents/Projetos/consultoria_imagem_ai`.

Os documentos do ZIP são referências técnicas e histórico de decisões. Recomendações de handoff não equivalem a novas solicitações do usuário.

## Comparação

| Recurso | Projeto anterior | ZIP do Lovable | Integração necessária |
| --- | --- | --- | --- |
| Interface | Streamlit, identidade Heloisa Hermann | Streamlit editorial; React com tela vazia | Escolher interface de destino |
| Cadastro | Atendimento e análises gravados em DuckDB | Oito exemplos em CSV; fichas editáveis planejadas | Adaptar cadastro ao modelo de sessão e ficha |
| Dossiê | Apoio por cliente | Nove pacotes, páginas, rascunhos e aprovação | Usar catálogo de pacotes do ZIP |
| Chat | Contexto e histórico por cliente | Chat de metodologia | Unir contexto de atendimento e fontes rastreáveis |
| Visagismo | MediaPipe, hipótese experimental e revisão | Dados de avaliação profissional na ficha | Preservar hipótese separada da avaliação confirmada |
| Conhecimento | ChromaDB com embeddings Ollama | ChromaDB com sentence-transformers e oito resumos | Reconciliar fontes e escolher indexador; não unir índices binários |
| Histórico | DuckDB com clientes, consultorias e análises | DuckDB com clientes, sessões e avaliações | Criar adaptador explícito entre esquemas |
| Arquivos locais | Fotos e dados no projeto local | Exportação/importação ZIP por atendimento | Definir migração local com rastreabilidade |
| IA | Ollama | Ollama ou Gemini | Preservar provedores configuráveis |

## Decisão pendente

1. Manter Streamlit: integrar recursos em `academic/`, seguindo a aplicação funcional entregue no ZIP. A prévia React do Lovable continuará sendo um aplicativo separado.
2. Converter para React: implementar telas na raiz TanStack/React e definir uma camada de serviços para Python, RAG e pré-análise. Copiar Python para o repositório não faz esses recursos funcionarem na prévia web.

A decisão foi solicitada ao usuário. Não foi assumida publicação, sincronização GitHub ou migração de dados pessoais.

## Preservação

Os originais não foram modificados. Esta cópia inclui o código principal, módulos ativos, configuração de código e documentação técnica selecionada do projeto anterior. Não é backup integral: não inclui `.env`, bancos, fotos, documentos de clientes, modelos, vetores, ambientes virtuais, saídas ou versões antigas de código.

`previous/` é referência de migração e não está conectado ao aplicativo. Seus caminhos relativos, dependências e banco ainda exigem adaptação antes de executar.

## Validação

Verificação sintática de arquivos Python realizada com `ast.parse`. Isso não valida dependências, execução das telas, banco, IA ou build React. Esses testes dependem da implementação escolhida.
