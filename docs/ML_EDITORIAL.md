# ML para a compilação da consultoria personalizada

> Atualização SaaS: cadastro e login individuais, dados e biblioteca editorial isolados por consultor. Mensalidade em piloto sem cobrança; ver [SAAS.md](SAAS.md) para contratos, migração dos dados anteriores e limites de implantação. Esta evolução não substitui as entregas acadêmicas pendentes.

## Finalidade escolhida pelo usuário

A consultora reaproveita referências de atendimentos concluídos, sobretudo padrões de apresentação de perfil, visagismo e análise. O objetivo é reduzir a busca e o copiar/colar, sem transferir as conclusões sobre uma pessoa para outra. O ML apoia a seleção dos textos que podem ajudar a compilar um novo dossiê. Não classifica roupas, rosto, temperamento ou clientes.

Fluxo: **página aprovada → padrão generalizado e autorizado → treinamento explícito → recuperação ML → rascunho contextualizado → revisão/aprovação humana**.

## O que foi implementado

1. A biblioteca editorial começa vazia. O consultor escolhe uma página aprovada como origem e escreve uma versão geral do trecho, com título e assunto.
2. Uma confirmação específica autoriza o uso reutilizável após retirar dados pessoais. Aprovar uma página não autoriza automaticamente incluí-la na biblioteca.
3. O backend exige a revisão atual e uma página aprovada, bloqueia alguns identificadores e guarda proveniência, hash e auditoria. Não recolhe automaticamente prontuários, fotos ou referências de peças.
4. Com pelo menos dois padrões distintos, a ação **Atualizar modelo** ajusta um vetorizador TF-IDF ao corpus autorizado. Ele aprende vocabulário e pesos IDF; a similaridade cosseno ordena os resultados.
5. O chat e o gerador de rascunhos recuperam até três padrões com similaridade mínima 0,12, junto à metodologia. As fontes identificam os padrões utilizados; dados da sessão de origem não entram no prompt.
6. Incluir/retirar um padrão torna o modelo desatualizado. A recuperação editorial pausa até novo treinamento, evitando continuar usando material retirado.
7. O dataset autorizado pode ser exportado em JSON, sem a proveniência da cliente. A biblioteca permanece no banco local, fora do Git e fora do ZIP individual do atendimento.

O modelo não muda os pesos da LLM. A melhoria inicial do copiloto ocorre pela seleção de referências melhores no contexto. Fine-tuning é uma possível evolução, dependente de corpus suficiente, autorização, avaliação e finalidade específica; não é feito nesta implementação.

## Mecanismo e reprodução

`backend/library.py` é responsável pela curadoria, persistência e ML. Usa scikit-learn 1.9.1: `TfidfVectorizer(strip_accents="unicode", ngram_range=(1,2), sublinear_tf=True)`. Os vetores são normalizados por L2; produto escalar equivale à similaridade cosseno. O ajuste é determinístico no mesmo corpus e versão.

SQLite guarda metadados do treinamento e o hash do corpus. O objeto numérico é reconstruído deterministicamente a partir do corpus autorizado ao reiniciar e fica em cache na memória. Não se importam arquivos pickle/joblib externos. O campo `metricas_validacao` começa nulo: ajustar o modelo não mede qualidade.

A similaridade exibida é proximidade textual, **não probabilidade de acerto**. Dois padrões são suficientes para executar o mecanismo, mas não para afirmar qualidade profissional. Os assuntos do formulário são metadados escolhidos pelo consultor; não há classificador supervisionado de assuntos nesta versão.

Referências técnicas: [TF-IDF no scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) e [avaliação e prevenção de vazamento](https://scikit-learn.org/stable/modules/cross_validation.html).

## Evidências necessárias para a etapa 2

A aplicação de ML foi definida e integrada. O corpus de atendimentos entregues **não foi disponibilizado nesta migração**. A suíte usa exemplos fictícios pequenos para verificar o fluxo, não como dataset de avaliação profissional. Não foram inventadas métricas.

Para concluir a evidência acadêmica:

- Formar um corpus autorizado e documentar fonte, licença/autorização, tamanho, assuntos, deduplicação e limites.
- Criar consultas de avaliação independentes dos textos e marcar os IDs de referências relevantes com revisão profissional. Separar conjuntos de desenvolvimento e teste; não ajustar o limiar nas consultas finais.
- Medir precisão@k, recall@k, F1@k, acerto do primeiro resultado e MRR. Documentar consultas sem referência e falhas de vocabulário. O script `python -m evaluation.editorial --consultant-email "email-da-conta" --golden caminho.json` gera essas métricas.
- Para ROC-AUC/classificação, estabelecer primeiro uma tarefa binária rotulada de relevância e justificar as métricas; esta versão é recuperação textual. Não apresentar similaridade como accuracy ou ROC-AUC. Confirmar com a disciplina a adequação dessa tarefa às métricas exigidas; se necessário, acrescentar um classificador supervisionado de relevância com dados rotulados.
- Medir se os padrões melhoram o dossiê com avaliação da geração: faithfulness, answer relevancy, adequação profissional e tempo economizado. Isso não é medido pelos testes funcionais.

Formato do golden editorial: uma lista com `id`, `consulta` e `relevantes` (lista de IDs do dataset autorizado). Pelo menos 10 consultas independentes; o script exige esse mínimo e IDs válidos. Não há golden preenchido porque as referências reais ainda não foram selecionadas.

## Fronteira da exclusividade

A biblioteca reutilizável guarda **estrutura e explicação gerais**. Peças, preferências, medidas, fotos e recomendações personalizadas continuam apenas no atendimento. O sistema não detecta todos os nomes/dados identificáveis: a generalização humana é obrigatória. Antes de uso real, implementar controle de acesso por consultor/organização, consentimento e retenção, conforme `SEGURANCA.md`.

A origem registrada é a versão da página no momento da autorização. Editar a página depois não altera o padrão generalizado: ele tem aprovação independente e pode ser retirado explicitamente na biblioteca. Essa separação preserva o histórico e evita trocar silenciosamente o material já autorizado.
