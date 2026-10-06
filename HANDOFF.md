> Registro histórico da etapa 1. A implementação React atual, as decisões do usuário e as pendências estão no README e em docs/. Este snapshot não substitui as instruções atuais do usuário.

# HANDOFF — Copiloto de Consultoria de Imagem e Estilo

Snapshot gerado em 05/10/2026. Projeto acadêmico (disciplina IA Factory, Etapa 1). Idioma do produto: português (Brasil).

## 1. Visão geral do sistema
Copiloto que apoia um consultor de imagem e estilo a montar o dossiê da cliente **página por página**. Cruza dados da cliente (ficha) + avaliação do consultor + metodologia (RAG sobre resumos autorais) e sugere textos; **o consultor revisa e aprova** cada página. Não substitui a análise profissional e não automatiza métricas administrativas.

Regras inegociáveis:
- Dados reais de clientes (nomes, fotos, medidas) **nunca** entram no app, banco ou GitHub. Só dados fictícios (Cliente A..H). Dados reais ficam em `.zip` locais no computador do consultor.
- Livros/apostilas de terceiros não são indexados; apenas os resumos aprovados em `academic/knowledge/`.
- Produto genérico: tratar sempre como "consultor" (sem "(a)").
- Dossiê de referência (PDF da consultora, não versionado) é a base de estrutura, cores e formatação.

## 2. Stack tecnológica
**Aplicação principal (a que importa): `academic/` — Python**
- Python 3.11+ (testado 3.12), Streamlit ≥1.40 (interface)
- DuckDB ≥1.2 (dados estruturados fictícios, Text-to-SQL)
- ChromaDB ≥1.0 + sentence-transformers ≥5 (`paraphrase-multilingual-MiniLM-L12-v2`, local) — RAG
- LLM: **Ollama local** (`llama3.1`, padrão usado na demonstração) ou Google Gemini (`gemini-3.8-flash` via `google-genai`; não reverter para `gemini-2.5-flash`, que retorna 404)
- pandas, tabulate, python-dotenv, requests

**Casca web Lovable (secundária): raiz do repo — TypeScript**
- TanStack Start v1 + React 19 + Vite 7 + Tailwind v4, alvo Cloudflare Workers. Contém apenas uma página `/` informativa. Não há backend, banco ou auth nela. Pode ser ignorada para continuar o copiloto.

## 3. Arquitetura
```text
Streamlit (academic/app.py)
 ├─ Dossiê da cliente ── pacotes.py (páginas por pacote) ── rag.generate() ── LLM
 ├─ Metodologia (chat) ── rag.stream_answer() ── knowledge_index.retrieve() ── ChromaDB (chroma_store/)
 ├─ Histórico de casos ── text_to_sql.py ── LLM gera SELECT ── DuckDB (demonstracao.duckdb, somente leitura)
 └─ Pasta da cliente ── export/import .zip (ficha.json + fotos) no computador do consultor
```
Sem autenticação, sem servidor remoto, sem banco em nuvem. Tudo roda local.

## 4. Estrutura de pastas
- `academic/app.py` — app Streamlit completo (UI, CSS editorial, estado, abas, export/import zip).
- `academic/pacotes.py` — catálogo das páginas do dossiê (`PAGINAS`) e dos 9 pacotes (`PACOTES`).
- `academic/rag.py` — prompt de sistema, provedores (Gemini/Ollama), streaming, `generate()` com retentativas.
- `academic/knowledge_index.py` — divisão em trechos (≤350 palavras), indexação ChromaDB, recuperação híbrida (semântica + palavras-chave, reranking de todos os trechos).
- `academic/text_to_sql.py` — pergunta → SQL DuckDB somente leitura (bloqueio por regex) → resumo.
- `academic/init_db.py` — cria `demonstracao.duckdb` a partir dos CSVs.
- `academic/data/*.csv` — fonte única de dados sintéticos.
- `academic/knowledge/*.md` — 8 resumos aprovados (fonte única do RAG).
- `academic/.env.example` — variáveis.
- `src/` — casca TanStack (ver `PROJECT_INVENTORY.md`).
- `.lovable/plan.md` — plano pendente das Fichas (questionário + avaliação técnica).
- `roadmap.md`, `AGENTS.md` — tarefas e decisões técnicas.

## 5. Rotas e telas
Streamlit (single page, navegação por pílulas):
- Cabeçalho: saudação "Boa tarde, Consultor" + assinatura; barra lateral com perfil do consultor.
- **Atendimento**: reabrir pasta `.zip`, seletor de cliente e pacote contratado.
- **Ficha**: leitura dos dados fictícios (medidas, temperamento, visagismo, coloração).
- Pílula **Dossiê da cliente**: pílulas das páginas do pacote → editor de texto, "Sugerir texto desta página", aprovar, fotos por página, exportar `.zip`.
- Pílula **Metodologia**: chat RAG (fontes ocultas na resposta), ícone ↺ limpa conversa.
- Pílula **Histórico de casos**: pergunta livre → SQL (em expansor técnico) → tabela + resumo; ↺ limpa.

Web TanStack: `/` (src/routes/index.tsx) apenas.

## 6. Principais funcionalidades
| Funcionalidade | Código | Serviço | Dados | Estado |
|---|---|---|---|---|
| Dossiê por pacote | app.py + pacotes.py | rag.generate | session_state, CSVs | Pronto |
| Sugestão de texto | app.py (botão) | rag.generate + LLM | ficha da sessão | Pronto |
| Chat de metodologia | app.py, rag.stream_answer | ChromaDB + LLM | knowledge/*.md | Pronto (perguntas precisam ser diretas) |
| Histórico de casos | text_to_sql.py | LLM + DuckDB | 8 tabelas | Frágil |
| Salvar/reabrir pasta | exportar_pasta / importar_pasta | zipfile | .zip local | Pronto |
| Layout mobile | CSS em app.py | — | — | Ajustado, não testado em aparelho real |
| Fichas (questionário/avaliação) | — | — | — | Planejado (.lovable/plan.md) |

## 7. Banco de dados
DuckDB local, gerado por `init_db.py` (não versionado). Esquema em `init_db.py::SCHEMA`:
`consultores` → `clientes` (consultor_id) → `sessoes` (cliente_id) → `medidas`, `temperamento`, `visagismo`, `teste_coloracao`, `coloracao` (todas PK/FK `sessao_id`). Sem triggers, views, enums, RLS. Campos vazios = não aplicável. ChromaDB local em `academic/chroma_store/`, coleção `resumos_aprovados_v1` (≈66 trechos), reconstruída com `--rebuild`. Não há Supabase/Lovable Cloud nem estrutura remota.

## 8. Autenticação e autorização
Não existe. Sem login, cadastro, roles ou RLS. App de uso local por um único consultor. Para uso multiusuário futuro será preciso adicionar autenticação.

## 9. Integrações externas
- **Ollama** (local, `OLLAMA_URL`) — geração de texto; usado em rag.py.
- **Google Gemini API** (opcional, `GEMINI_API_KEY`) — alternativa em rag.py.
- **Hugging Face** — download único do modelo de embeddings na primeira indexação.

## 10. Variáveis de ambiente
Ver `.env.example` (raiz) e `academic/.env.example`:
- `LLM_PROVIDER` — `ollama` ou `gemini`.
- `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`) — só se gemini. **Secret.**
- `OLLAMA_URL`, `OLLAMA_MODEL` — servidor/modelo local.
A casca TanStack não exige variáveis.

## 11. Como executar localmente
Copiloto (Windows PowerShell; em Linux/mac use `.venv/bin/python`):
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r academic/requirements.txt
copy academic\.env.example academic\.env   # editar LLM_PROVIDER etc.
ollama pull llama3.1                        # se usar Ollama
.\.venv\Scripts\python.exe academic/init_db.py
.\.venv\Scripts\python.exe academic/knowledge_index.py --rebuild
.\.venv\Scripts\python.exe -m streamlit run academic/app.py   # celular: --server.address=0.0.0.0
```
Casca web: Node 20+ e Bun → `bun install`, `bun run dev`, `bun run build`, `bun run lint`. Não há testes automatizados.

## 12. Deploy atual
Não publicado. Copiloto roda no computador do usuário (acesso pelo celular na mesma rede Wi‑Fi). Repositório GitHub sincronizado com Lovable (casca web). Publicação no Streamlit Cloud está no roadmap.

## 13. Pendências e limitações
- Histórico de casos: SQL gerado pode falhar em perguntas analíticas complexas (GROUP BY etc.).
- RAG sensível ao vocabulário; termos fora dos resumos retornam "sem respaldo".
- Latência alta com Ollama local (escolha consciente para economizar tokens).
- Fichas (questionário da cliente + avaliação técnica) não implementadas.
- Roadmap aberto: originais em "Consultar Texto Original", biblioteca de textos fixos, exemplos de imagens/produtos, novos módulos de atendimento, Streamlit Cloud.
- `app.py` é monolítico (~440 linhas, CSS embutido) — dívida técnica.
- Ajustes de rolagem dependem de truques de âncora/JS no Streamlit — frágeis.
- Mobile não validado em aparelho real.

## 14. Próximos passos recomendados
1. Implementar Fichas conforme `.lovable/plan.md`.
2. Robustecer Text-to-SQL (exemplos few-shot, retentativa com mensagem de erro).
3. Separar CSS e componentes de `app.py` em módulos.
4. Testes mínimos (pytest) para `pacotes.paginas`, `keywords`, bloqueio SQL.
5. Publicar no Streamlit Cloud com secrets.

## 15. Mapa rápido
- Dossiê → pílula Dossiê → app.py `_abrir_aba`/editor → rag.generate → CSVs/session_state
- Metodologia → pílula Metodologia → app.py chat → rag.stream_answer → knowledge_index.retrieve → ChromaDB
- Histórico → pílula Histórico → text_to_sql.to_sql/run/summarize → DuckDB
- Pasta da cliente → Atendimento → exportar_pasta/importar_pasta → .zip local
- Pacotes → seletor → pacotes.PACOTES/PAGINAS

## Estado do Git
- Branch: `edit/edt-4fdfc5a8-c04f-4bc2-9d69-e98856418cf8` (branch de edição Lovable; principal: `main`)
- Último commit: `6feebed` — "Corrigiu telas mobile do dashboard" (2026-10-05)
- Sem arquivos modificados ou não rastreados no momento do snapshot (exceto estes documentos de handoff).

## Validação
- Python: `py_compile` em todos os módulos de `academic/` — OK.
- Casca web: build sem erros registrados; `eslint`: 2 erros apenas de formatação Prettier em `src/routes/index.tsx` (corrigíveis com `bun run format`) e 6 avisos. Não corrigido para não alterar o produto.
- Sem testes automatizados.

## Segurança
Varredura sem segredos reais versionados. Nenhum `.env` no pacote. Um plano antigo em `.lovable/plan/` cita apenas o prefixo genérico `AIza...` (não é chave). Chave Gemini, se existir, está só no `academic/.env` local do usuário.
