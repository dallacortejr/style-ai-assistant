# Evolução orientada pela disciplina e pelo produto

> Atualização SaaS: cadastro e login individuais, dados e biblioteca editorial isolados por consultor. Mensalidade em piloto sem cobrança; ver [SAAS.md](SAAS.md) para contratos, migração dos dados anteriores e limites de implantação. Esta evolução não substitui as entregas acadêmicas pendentes.

## Prioridade atual

Concluir a migração da interface e a documentação, mantendo as regras de revisão humana e os dados fictícios. Testar com o consultor os campos da ficha e das referências exclusivas por atendimento. O cadastro de referências por atendimento começa vazio e é preenchida pelo profissional, sem classes automáticas ou catálogo fixo.

## Etapa 2

1. Consolidar a aplicação de ML escolhida: recuperação de padrões editoriais autorizados para compilar dossiês. O mecanismo já está integrado; formar o corpus revisado, rotular consultas independentes e medir qualidade. Confirmar a adequação da tarefa/métricas à rubrica; detalhes em ML_EDITORIAL.md.
2. Evoluir os dois papéis do chat para agentes com escolha de ferramentas limitada. Ferramentas: ler ficha, buscar metodologia, consultar dados, buscar referências do atendimento e consultar o modelo ML editorial. Aprovar e publicar continuam fora das ferramentas.
3. Cinco traces reais locais já foram capturados. Consolidar a documentação da equivalência acadêmica ou integrar Langfuse. Não inventar tokens, custos ou screenshots.
4. Revisar o golden dataset com o consultor, medir faithfulness e answer relevancy com DeepEval ou equivalente e escrever a análise das falhas.
5. Redigir relatório de 700–1500 palavras após obter métricas reais; preparar demonstração com fala do estudante.

## Etapa 3

1. Guardrails mais completos e testes adversariais de entrada/saída; anonimização e controle de acesso.
2. Publicação de interface e API protegida, com secrets gerenciados; confirmar equivalência da interface React na avaliação acadêmica.
3. Documentação final com screenshots, locks, limitações e evidências de execução.
4. Análise crítica do desafio original, resultados e três evoluções; reflexão pessoal e vídeo mostrando a URL.

## Aplicativo real após o piloto

| Evolução | Tecnologia possível | Impacto esperado |
| --- | --- | --- |
| Multiusuário com referências exclusivas | OIDC, PostgreSQL, políticas por organização, object storage privado | Separar dados e trabalho de cada consultor/cliente |
| Dossiê diagramado | Templates HTML/CSS e exportação PDF no servidor | Entrega consistente com revisão por página |
| Busca orientada pelo profissional | Busca textual/vetorial restrita ao atendimento e filtros do consultor | Localizar o material próprio sem padronizar escolhas |
| Monitoramento e avaliação contínua | Langfuse, DeepEval e CI | Detectar regressões e comparar mudanças de modelos |
| Referências e mídias com proveniência | Metadados de origem, consentimento e licença | Facilitar manutenção e publicação responsável |

Não há prazo ou integração contratada presumida. A troca de banco e a produção multiusuário dependem de requisitos posteriores.
