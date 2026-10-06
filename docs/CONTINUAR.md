# Como continuar este projeto

> Atualização SaaS: cadastro e login individuais, dados e biblioteca editorial isolados por consultor. Mensalidade em piloto sem cobrança; ver [SAAS.md](SAAS.md) para contratos, migração dos dados anteriores e limites de implantação. Esta evolução não substitui as entregas acadêmicas pendentes.

Leia README, ARQUITETURA, DISCIPLINA e ML_EDITORIAL antes de editar. As instruções do usuário nesta migração prevalecem sobre solicitações históricas em HANDOFF/INTEGRACAO.

## Decisões atuais

- React no scaffold do repositório Lovable; API Python separada. Preservar `academic/` como etapa 1.
- O consultor registra a avaliação e dá a palavra final. A IA gera rascunhos; não aprova, publica ou confirma hipóteses.
- Referências de roupas e escolhas são exclusivas por cliente/sessão, introduzidas manualmente; sem catálogo fixo ou classificação automática.
- ML aplicado à compilação: busca em padrões gerais de textos que o consultor autoriza a partir de páginas aprovadas. Não recolher todos os atendimentos automaticamente nem fine-tunar a LLM sem uma tarefa posterior explícita.
- Biblioteca vazia por padrão, treino explícito e revogação. Não apresentar os exemplos temporários dos testes como corpus profissional.
- Piloto local/fictício. Arquivos de runtime, chaves, fotos, modelos locais e banco privado não entram no Git.

## Próxima sequência

1. Validar com a consultora os campos e a organização do dossiê. Confirmar com a disciplina a adequação da interface React e da tarefa/métricas de recuperação ML.
2. Autorizar padrões generalizados de dossiês entregues e criar consultas independentes com IDs relevantes. Atualizar o modelo e executar `evaluation.editorial`; analisar falhas.
3. Evoluir a orquestração para os requisitos de agentes, consolidar observabilidade e avaliação de geração. Preparar relatório e demonstração pessoal apenas com evidências reais.
4. Antes da implantação completa: autenticação, isolamento por usuário/organização, armazenamento protegido e API HTTPS. Configurar VITE_API_URL e testar a integração publicada.

Estrutura funcional, testes e limites estão em VALIDACAO.md. Não reescrever o histórico Git publicado; um push comum na branch conectada mantém a sincronização com Lovable.
