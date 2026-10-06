# Contrato HTTP

> Atualização SaaS: cadastro e login individuais, dados e biblioteca editorial isolados por consultor. Mensalidade em piloto sem cobrança; ver [SAAS.md](SAAS.md) para contratos, migração dos dados anteriores e limites de implantação. Esta evolução não substitui as entregas acadêmicas pendentes.

Serviço local: `http://127.0.0.1:8000`. Documentação interativa gerada automaticamente: `/docs`. Todos os identificadores de clientes novos seguem `Cliente A`, `Cliente B`, `Cliente AA` etc. Os IDs de sessões são gerados pelo servidor.

| Método | Rota | Função |
| --- | --- | --- |
| GET | `/health` | Modo de execução, provedor e RAG |
| GET | `/catalog` | Nove pacotes e páginas |
| GET/POST | `/sessions` | Listar/criar atendimentos |
| GET | `/sessions/{sid}` | Reabrir atendimento persistido |
| PUT | `/sessions/{sid}/ficha` | Questionário e avaliação; exige `revision` |
| PUT | `/sessions/{sid}/pages/{page}` | Salvar texto; exige `revision` |
| POST | `/sessions/{sid}/pages/{page}/decision` | `aprovar` ou `reabrir`, sempre pelo consultor |
| POST | `/sessions/{sid}/pages/{page}/draft` | Sugerir rascunho com fontes; nunca aprova |
| POST | `/sessions/{sid}/pages/{page}/photos` | Referência PNG/JPEG, até 3 MB; invalida aprovação |
| POST | `/sessions/{sid}/vision` | Pré-análise experimental opcional; não altera avaliação |
| POST | `/chat` | Chat por atendimento; resposta NDJSON com streaming |
| POST | `/history` | Consulta somente leitura aos CSVs de demonstração |
| GET | `/knowledge` | Fontes aprovadas; `?q=` busca trechos |
| GET | `/sessions/{sid}/export` | ZIP versão 3 com ficha, textos e imagens |
| POST | `/import` | ZIP versões 2/3, corpo binário; cria nova sessão em revisão |
| GET | `/traces` | Últimos 100 registros locais |

### Revisões

As escritas recebem a revisão atual. Exemplo de salvar texto: `{"revision": 2, "texto": "Texto revisado..."}`. O servidor retorna a sessão completa, já com revisão incrementada. A interface deve substituir o estado local pelo retorno. Revisão antiga retorna 409; entrada inválida, 422; sessão inexistente, 404; IA indisponível, 503 ou evento `erro` no streaming.

### Pasta de atendimento

O ZIP novo usa `ficha.json` versão 3 e `fotos/NN/nome.ext`. Importação não extrai arquivos arbitrários, limita tamanho e valida as imagens. Aprovações de arquivos importados não são automaticamente confiáveis: a nova sessão exige revisão. Fotos e textos da pasta são mantidos; o histórico exportado e a auditoria são evidências históricas e ainda não são restaurados como eventos ativos. A importação não migra o DuckDB privado do projeto anterior.

### Segurança do piloto

Sem autenticação por usuário nesta versão. CORS permite somente as origens locais configuradas; isso não substitui autenticação. O script padrão inicia em loopback. A publicação de uma API Python exige uma fronteira autenticada antes de habilitar dados pessoais ou múltiplos usuários.

## Referências exclusivas por atendimento

`POST /sessions/{sid}/references` registra título, tipo preenchido pelo consultor, ocasião, cor/modelagem, orientação e link. `GET /sessions/{sid}/references?q=` busca apenas nessa sessão. As referências começam vazias; não há catálogo fixo de peças, classificação automática ou transferência de escolhas entre clientes. O copiloto recebe somente as referências do atendimento ativo que correspondam ao pedido. São preservadas na pasta ZIP. O histórico CSV acadêmico serve a demonstrações, não alimenta recomendações personalizadas.

## Biblioteca editorial e ML

| Método | Rota | Função |
| --- | --- | --- |
| GET | `/library` | Trechos curados, incluindo retirados, e estado do modelo |
| POST | `/sessions/{sid}/pages/{page}/library` | Autorizar um padrão geral; origem aprovada, `revision`, título/tema/texto e confirmação obrigatória |
| POST | `/library/{rid}/revoke` | Retirar referência; impede recuperação pelo modelo desatualizado |
| POST | `/library/train` | Ajustar TF-IDF com pelo menos dois padrões; registra versão |
| GET | `/library/search?q=` | Recuperar até três referências com ML treinado e corpus vigente |
| GET | `/library/dataset` | Exportar corpus autorizado sem proveniência pessoal |

A autorização de um padrão não aprova páginas nem altera a ficha. Nenhum atendimento inteiro entra automaticamente no modelo. A recuperação retorna similaridade textual, não confiança probabilística. ML_EDITORIAL.md documenta o ajuste, cache, corpus e métricas pendentes.

## Identidade e assinatura

Todos os endpoints de dados exigem `consultoria_session`, cookie HttpOnly. Escritas exigem também `X-CSRF-Token`. O browser usa `credentials: include`. A identidade/proprietário não é um campo aceito das entradas.

| Método | Caminho | Resultado |
| --- | --- | --- |
| POST | `/auth/register` | `{name,email,password}`; 201, conta e CSRF; cookie de sessão |
| POST | `/auth/login` | `{email,password}`; conta e CSRF; troca a sessão do navegador |
| GET | `/auth/me` | Conta atual e CSRF, ou 401 |
| PUT | `/auth/profile` | `{name}`; perfil atualizado; não altera senha, e-mail nem assinatura |
| POST | `/auth/logout` | Revoga a sessão e remove o cookie |
| POST | `/demo/seeds` | Carrega exemplos fictícios somente se a conta está vazia |
| POST | `/billing/checkout` | 503: provedor não configurado; não cria cobrança |

A conta pública contém `id,name,email,created,subscription`. A assinatura inclui `status,cycle,provider,checkout_available,price`, com estado inicial `pilot`, ciclo `monthly` e valores comerciais indefinidos. Tentativas de modificar o status via perfil retornam 422. Falta de sessão: 401; CSRF/origem: 403; registro de outra conta: 404; assinatura inativa sob enforcement: 402; limite de autenticação: 429. `/health` e schemas OpenAPI continuam públicos sem dados privados.
