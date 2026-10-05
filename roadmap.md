# Roadmap — Etapa 1

- [x] 0. Apresentação do plano em PPTX
- [x] 1. Resumos temáticos aprovados pelo usuário
- [ ] 1a. Originais completos no app com campo "Consultar Texto Original" (vão ao GitHub público)
- [ ] 1b. Biblioteca de textos fixos (tipo A) derivada dos resumos — v1 redigida; aguardando revisão do consultor(a)
- [ ] 1c. Exemplos de imagens e produtos: selecionar arquivos públicos com licença de reutilização verificável; exibir apenas como exemplos. Na ficha de cada cliente fictício, permitir ao consultor(a) substituir/adicionar imagens e recomendações de produtos personalizadas, sem alterar a biblioteca geral. Não usar fotos ou dados reais de clientes.
- [x] 2. CSVs fictícios + script de carga DuckDB e consultas de exemplo (banco gerado localmente)
- [x] 3. ChromaDB + RAG concluído (66 trechos; gemini-3.8-flash; teste com 4 perguntas OK)
- [~] 4. App Streamlit (academic/app.py: chat com streaming, text-to-SQL, ficha + sugerir com IA) — falta teste completo quando o Gemini sair da sobrecarga (503)
- [x] 4a. Montagem do dossiê página a página, visual editorial, perfil editável, jornada de módulos, salvar/reabrir pasta da cliente (.zip)
- [x] 4c. Pacotes 1–9 com páginas dinâmicas + visual refinado (contraste, perfil centralizado, abas sem ícones)
- [x] 4d. Assinatura logo abaixo da saudação e páginas selecionadas pelas pílulas, sem seletor duplicado
- [ ] 4b. Próximos módulos de atendimento (revisão, guarda-roupa etc.) e formulário da cliente — fase futura
- [ ] 5. README CBL, .env.example, .gitignore, requirements.txt
- [ ] 6. Publicação Streamlit Cloud + roteiro do vídeo
- [ ] 7. Entrega Etapa 1: relatório PDF formal + roteiro do vídeo (problema, solução, arquitetura, limitações) — gravação de tela feita pelo usuário
