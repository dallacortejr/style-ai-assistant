# Teste do RAG com a chave Gemini (fim da tarefa 3 da Etapa 1)

## Objetivo
Com a chave criada pelo usuário no Google AI Studio, testar o pipeline completo: indexação dos resumos no ChromaDB + resposta real do Gemini a partir dos trechos recuperados.

## Passos

1. **Guardar a chave em campo seguro**
   - Abrir o formulário seguro do projeto para a variável `GEMINI_API_KEY` (o usuário cola a chave `AIza...` diretamente no formulário; a chave nunca passa pelo chat).
   - O RAG (`academic/rag.py`) já lê `GEMINI_API_KEY` do ambiente.

2. **Indexar os resumos**
   - Rodar `python academic/knowledge_index.py --rebuild` para criar a coleção ChromaDB `resumos_aprovados_v1` com os 8 resumos aprovados, fatiados por seção (~350 palavras), com tema e nível como metadados.
   - Instalar as dependências necessárias no sandbox (duckdb/chromadb/sentence-transformers) antes da execução.

3. **Testar o RAG de verdade**
   - Rodar consultas de teste via `academic/rag.py` cobrindo os blocos principais do dossiê, por exemplo:
     - "Quais são as 12 estações e o TIP de cada uma?"
     - "Como funciona a graduação de contraste no teste de coloração?"
     - "Quais silhuetas femininas existem e como identificar cada uma?"
     - "Que temperamento uma linha reta transmite no visagismo?"
   - Verificar em cada resposta: citação de fonte/seção, fidelidade ao método e ausência de alucinação.

4. **Registrar resultados e próximos passos**
   - Anotar no `roadmap.md` a conclusão da tarefa 3 (indexação + teste).
   - Próxima tarefa: app Streamlit (chat com streaming, consulta ao banco em linguagem natural, ficha da sessão e botão "sugerir com IA").

## Notas
- A chave fica só no armazenamento seguro do projeto (e depois nos Secrets do Streamlit Cloud) — nunca no repositório.
- Sempre dados fictícios; tom de consultor(a) genérico.
