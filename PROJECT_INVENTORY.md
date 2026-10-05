# PROJECT_INVENTORY

## Páginas / rotas
- Streamlit `academic/app.py` (página única): Atendimento, Ficha, abas Dossiê da cliente / Metodologia / Histórico de casos.
- TanStack: `/` → `src/routes/index.tsx`; layout `src/routes/__root.tsx`.

## Componentes / funções principais (app.py)
`secao`, `exportar_pasta`, `importar_pasta`, `linha`, `_abrir_aba`, editor de página, chat de metodologia, painel Text-to-SQL.

## Módulos Python (services)
- `rag.py`: `api_key`, `client`, `stream_answer`, `answer`, `generate`, `_ollama`
- `knowledge_index.py`: `split_sections`, `chunks`, `keywords`, `collection`, `rebuild`, `retrieve`
- `text_to_sql.py`: `ensure_db`, `to_sql`, `run`, `summarize`
- `pacotes.py`: `PAGINAS`, `PACOTES`, `nome`, `paginas`
- `init_db.py`: `SCHEMA`, `main`

## Hooks / providers (TanStack)
`src/hooks/use-mobile.tsx`; `src/router.tsx`; `src/start.ts` (middlewares erro + CSRF); `src/server.ts`.

## Tabelas (DuckDB)
consultores, clientes, sessoes, medidas, temperamento, visagismo, teste_coloracao, coloracao.

## Coleções vetoriais
ChromaDB `resumos_aprovados_v1` (de `academic/knowledge/*.md`).

## Funções de banco / Edge Functions
Nenhuma.

## APIs / integrações
Ollama (local), Google Gemini (opcional), Hugging Face (download do modelo de embeddings).

## Bibliotecas relevantes
Python: streamlit, duckdb, chromadb, sentence-transformers, google-genai, pandas, tabulate, python-dotenv, requests.
JS: @tanstack/react-start, react 19, vite 7, tailwindcss 4, radix-ui/shadcn.
