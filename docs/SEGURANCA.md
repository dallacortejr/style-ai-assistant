# Autoridade, dados e segurança

## O consultor conduz

O copiloto não tem ferramenta de aprovação. O endpoint de decisão recebe uma ação explícita do consultor e confere pacote, texto salvo e revisão. Modificações posteriores invalidam a aprovação. Importações também exigem revisão nova. A hipótese facial fica separada da avaliação técnica.

Essas regras são invariantes de negócio verificadas no servidor. Não são uma autenticação: no piloto local, quem consegue acessar a API tem o mesmo papel de consultor. A identidade do usuário deve ser autenticada e registrada antes de uso compartilhado.

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

O SQLite não está cifrado, não há login, isolamento entre usuários, política de retenção, rate limit global ou backup automatizado. CORS não é autenticação. Não expor a API em `0.0.0.0` ou publicar o serviço desta versão para dados reais.

## Evolução para aplicação real

1. OIDC/OAuth e identidade por consultor; sessões autenticadas no servidor web.
2. PostgreSQL com isolamento por usuário/organização; armazenamento privado de imagens e URL temporária.
3. Scanners mais completos com testes adversariais, consentimento, minimização e retenção definida.
4. Telemetria sanitizada, rate limits, backups e restauração testada.
5. Implantação separada da API Python e UI Lovable, com HTTPS e secrets do provedor de hospedagem.

Essas etapas são pré-requisitos de produção, não promessas de conformidade já obtida.
