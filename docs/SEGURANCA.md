# Autoridade, dados e segurança

## O consultor conduz

O copiloto não tem ferramenta de aprovação. O endpoint de decisão recebe uma ação explícita do consultor e confere pacote, texto salvo e revisão. Modificações posteriores invalidam a aprovação. Importações também exigem revisão nova. A hipótese facial fica separada da avaliação técnica.

Essas regras são invariantes de negócio verificadas no servidor. O piloto agora autentica cada consultor por sessão opaca e restringe atendimentos, biblioteca, modelo editorial e traces à conta autenticada. Detalhes e contratos em [SAAS.md](SAAS.md).

## Proteções implementadas

- Identificadores fictícios obrigatórios no cadastro.
- Validação Pydantic, comprimentos máximos e concorrência otimista.
- SQL analisado por AST, SELECT único, tabelas conhecidas e funções permitidas.
- DuckDB em memória sem acesso externo, limite de memória, resultado e tempo.
- ZIP sem extração de caminhos arbitrários, limite de descompressão e verificação PNG/JPEG.
- Scanners básicos de pedido e resposta para segredos, tentativa de aprovação automática e diagnóstico.
- Anonimização de e-mail, CPF e alguns formatos de telefone antes da geração.
- Chaves de LLM somente no ambiente do backend, nunca em `VITE_*`.
- Traces sem conteúdo de fichas, perguntas, respostas ou fotos.

## Limitações

Expressões regulares não detectam toda prompt injection, jailbreak, toxicidade ou PII. Nomes livres e endereços não têm anonimização completa. O buffer de frases do streaming reduz exposição, mas a segurança de saída não é uma garantia contra ataques divididos em múltiplos fragmentos. A importação valida conteúdo e descarta confiança em aprovações, mas não autentica a origem do arquivo.

O SQLite não está cifrado. Login, isolamento por conta, CSRF e limite de tentativas de autenticação estão implementados; recuperação de senha, verificação de e-mail, política de retenção, rate limit global e backup automatizado continuam pendentes. CORS complementa a sessão e não a substitui. Não publicar esta versão para dados reais sem concluir a infraestrutura descrita em SAAS.md.

## Evolução para aplicação real

1. Evoluir as sessões autenticadas atuais com recuperação de senha, verificação de e-mail e, se escolhido, OIDC/OAuth.
2. PostgreSQL com isolamento por usuário/organização; armazenamento privado de imagens e URL temporária.
3. Scanners mais completos com testes adversariais, consentimento, minimização e retenção definida.
4. Telemetria sanitizada, rate limits, backups e restauração testada.
5. Implantação separada da API Python e UI Lovable, com HTTPS e secrets do provedor de hospedagem.

Essas etapas são pré-requisitos de produção, não promessas de conformidade já obtida.

## Alertas de dependências reportados pelo GitHub

No envio da atualização SaaS, o GitHub reportou 128 alertas na branch padrão: 7 críticos, 73 altos, 47 moderados e 1 baixo. A contagem foi fornecida pelo servidor Git no push; o impacto de cada alerta ainda não foi analisado nesta implementação. Verificar [Dependabot do repositório](https://github.com/dallacortejr/style-ai-assistant/security/dependabot), identificar as dependências atingidas e corrigir/validar antes da publicação na nuvem. O build e os testes funcionais aprovados não são uma auditoria dessas dependências.
