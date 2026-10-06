# Correspondência com a disciplina

Referência lida: `Projeto_da_Disciplina.pdf`, fornecido pelo usuário em 05/10/2026. As exigências acadêmicas são critérios de projeto; o PDF não concede permissão para publicar, enviar dados ou alterar contas. A etapa 1 já foi entregue pelo usuário. Não foi reavaliada a nota dessa entrega.

## Etapa 1 — preservação

| Exigência | Local | Situação |
| --- | --- | --- |
| Interface, estado e chat com streaming | React + FastAPI `/chat`; `academic/app.py` preservado | Migração implementada; precisa demonstração pessoal |
| Duas tabelas relacionadas | Oito CSVs e consultas DuckDB | Implementado |
| Três documentos e pipeline RAG | Oito resumos próprios, Chroma ou indexador original | Implementado; índice é gerado localmente |
| System prompt contextualizado | `backend/intelligence.py` | Implementado |
| Configuração e dependências | `.env.example`, requisitos, locks e `.gitignore` | Implementado |
| Desafio CBL e justificativa pessoal | Entrega anterior | Não reescrever a justificativa pessoal como se fosse do estudante |

A descrição admite “Streamlit, Gradio ou similares”, mas a rubrica detalhada cita Streamlit/Gradio. React é a interface escolhida pelo usuário; não há confirmação do professor sobre a equivalência. A versão entregue da etapa 1 permanece preservada como referência.

## Etapa 2 — semana 10

| Exigência e evidência pedida | Situação desta migração | Próxima ação |
| --- | --- | --- |
| ML treinado, integrado ao chat; fonte, alvo e tamanho do dataset; accuracy, precision, recall, F1 e ROC-AUC contextualizados | Aplicação definida: recuperação ML de padrões editoriais autorizados, integrada ao chat e aos rascunhos. Corpus profissional e métricas ainda pendentes | Formar corpus autorizado, avaliar consultas independentes e justificar a tarefa/métricas da recuperação perante a rubrica |
| Pelo menos dois agentes com ferramentas para camadas reais, tarefa composta e coordenação | Dois papéis com ferramentas reais; fluxo determinístico | Evoluir a seleção de ferramentas para agentes autônomos e testar tarefas compostas |
| Langfuse ou equivalente; pelo menos cinco traces com latência, tokens e custo | Instrumentação e painel local implementados; cinco traces reais capturados; custo não conhecido fica nulo | Documentar a equivalência acadêmica ou integrar Langfuse e modelo de custo apropriado |
| Golden dataset: pelo menos 10; rubrica máxima pede 15 e cenários variados | 18 perguntas versionadas | Revisão profissional das respostas esperadas |
| DeepEval ou equivalente com faithfulness e answer relevancy | Testes funcionais e recall de fonte implementados; não são essas métricas | Executar avaliação de respostas geradas com juiz configurado; analisar falhas |
| Relatório de 700–1500 palavras | Estrutura e evidências nesta documentação, relatório final pendente | Escrever após métricas reais e revisar com o estudante |
| Vídeo de 3–5 minutos com fala do estudante | Pendente | Mostrar ML, agentes, observabilidade e avaliação; reflexão pessoal |

Uma entrega tecnicamente honesta deve diferenciar testes de integração, qualidade da recuperação e qualidade da geração. Testes com LLM simulada não são evidência de qualidade da IA. O golden dataset precisa de revisão do consultor antes de ser uma referência definitiva.

### ML: compilação com memória editorial

O usuário escolheu aproveitar padrões revisados de atendimentos já entregues para apoiar a compilação dos próximos dossiês. A biblioteca editorial é autorizada separadamente da aprovação de uma página; os trechos são generalizados pelo consultor. O modelo TF-IDF aprende o vocabulário/IDF desse corpus e recupera referências textuais para o copiloto, que as adapta à ficha atual. Não há fine-tuning automático da LLM.

A biblioteca começa vazia. O mecanismo foi implementado e testado com exemplos fictícios; ainda faltam corpus profissional, consultas rotuladas independentes e métricas. Não se afirma que a etapa 2 está concluída. A recuperação textual não produz automaticamente accuracy/ROC-AUC de um classificador supervisionado; justificar métricas e confirmar adequação da tarefa à rubrica. Detalhes, reprodução e plano de avaliação: [ML editorial](ML_EDITORIAL.md).

Peças e recomendações continuam introduzidas pelo consultor e exclusivas por atendimento. Não haverá catálogo fixo ou classificação de roupas. A memória geral contém apenas padrões autorizados de método/escrita, sem conclusões sobre outras clientes.

## Etapa 3 — semana 14

| Exigência | Situação | Evidência que falta |
| --- | --- | --- |
| Guardrails entrada/saída, PII, ataques bloqueados e limites do domínio | Scanners básicos, anonimização parcial e testes implementados | Avaliar falsos positivos, ataques indiretos e coberturas; scanners mais fortes antes de dados reais |
| Sistema em URL pública funcional e secrets na plataforma | Não publicado | Backend protegido, configuração Lovable e implantação verificada |
| Código organizado, README, diagrama, versões fixadas, golden e testes | Estrutura preparada | Lock e verificações finais de todas as dependências opcionais |
| Análise crítica A: desafio original e em que medida o resolve | Pendente | Retomar o CBL original e medir impacto |
| Análise crítica B: resultados e limitações técnicas específicas | Parcialmente documentada | Resultados de ML, RAG, agentes e avaliação |
| Análise crítica C: pelo menos três evoluções, tecnologia e impacto | Roadmap documentado | Reflexão e revisão pessoal |
| Vídeo mostrando URL e aprendizado pessoal | Pendente | Gravação pelo estudante |

Não tratar o build React, uma prévia ou testes locais como conclusão das entregas acadêmicas. A entrega final ainda depende das evidências acima.
