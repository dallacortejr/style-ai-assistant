<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

<!-- Project decisions -->
- Keep reusable sample media/product references separate from per-client recommendations; the consultant edits each client's selections without changing the general library, so examples never become personalized advice by default.
- Treat academic/data CSVs as the sole reproducible synthetic demo source and regenerate DuckDB with academic/init_db.py; this prevents real client data and local database binaries entering the public repository.
- Index only approved original-language summaries in academic/knowledge with section/source metadata; full third-party PDFs stay outside the RAG index to keep retrieval attributable and avoid copying protected texts.

## Decisões técnicas

- Modelo LLM da Etapa 1: `gemini-3.8-flash` (google-genai). O `gemini-2.5-flash` foi descontinuado pela API para chaves novas (404) — não reverter.
- Busca RAG: reranking avalia TODOS os trechos (corpus pequeno); embeddings locais subestimam trechos-tabela curtos. keywords() corta "s" final (singular/plural).
