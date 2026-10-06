# Contas de consultores — primeira base SaaS

## O que muda para o profissional

Ao abrir a aplicação, escolha **Criar conta**, informe nome profissional, e-mail e uma senha exclusiva com 12 a 128 caracteres. O cadastro também oferece uploads opcionais de **foto do consultor** e **logo do estúdio**, com prévia e opção de remoção. O cadastro abre um estúdio vazio. **Novo atendimento** inicia o fluxo habitual; **Experimentar com dados fictícios** carrega os oito exemplos acadêmicos somente nesta conta. O nome no estúdio passa a vir do cadastro. Clique no nome ou avatar para editar seu perfil, consultar a situação do plano e sair.

O consultor é cliente da plataforma. As pessoas atendidas são clientes da consultoria, representadas por atendimentos pertencentes ao consultor. Não possuem login nesta versão. Permanece a exigência acadêmica de identificadores fictícios para os atendimentos. Cada página do dossiê depende da revisão e aprovação explícitas do profissional.

## Fronteira de dados

`consultants` contém identidade e hash da senha. `auth_sessions` contém hash do token opaco, consultor, token CSRF e validade absoluta de oito horas. `sessions.consultant_id` e `editorial.consultant_id` delimitam todas as leituras e escritas. `editorial_models` contém um snapshot por consultor. A biblioteca não mistura padrões de contas diferentes, mesmo quando seus temas ou textos são semelhantes. Traces ficam em `runtime/tenants/<consultant_id>/traces.jsonl`. Os CSVs acadêmicos e a metodologia autoral continuam fontes comuns explicitamente fictícias, não registros reais de outros usuários.

A identidade vem exclusivamente da sessão validada no middleware ASGI e acompanha os trabalhos executados em threads, inclusive streaming. O cliente não escolhe seu proprietário nas requisições. Identificadores de outras contas retornam 404. A falta de autenticação retorna 401; alterações sem CSRF ou com origem indevida retornam 403. Respostas privadas usam `Cache-Control: no-store`. Expiração remove o espaço de trabalho da tela.

As senhas usam scrypt (`N=131072`, `r=8`, `p=1`) com salt aleatório de 16 bytes. O cookie é `HttpOnly`, `SameSite=Strict`, com `Secure` controlado por `COOKIE_SECURE`. Tokens de autenticação não ficam em localStorage nem são devolvidos em JSON. O token CSRF fica somente em memória e é renovado ao entrar. Login troca e revoga a sessão anterior do mesmo navegador; sair revoga a sessão atual. Cadastro e login têm limite conjunto de 15 tentativas por IP em 15 minutos, persistido em SQLite. Não se confia em `X-Forwarded-For` sem uma futura configuração explícita de proxy.

## Mensalidade

O plano contém `status=pilot`, `cycle=monthly`, provedor e preço ainda indefinidos. **Nenhuma cobrança é realizada.** O endpoint de checkout responde 503 até existir uma integração. O usuário não pode promover sua assinatura a `active` pelo cadastro ou perfil.

`SAAS_ENFORCE_SUBSCRIPTION=false` mantém acesso ao piloto. Com `true`, contas sem assinatura ativa recebem 402 nas funcionalidades de consultoria, mas continuam podendo acessar perfil e sair. Não ativar essa opção antes de implementar o checkout e os webhooks verificados do provedor. A futura integração deve definir preço, cancelamento, falha de pagamento, eventos idempotentes e confirmação de assinatura no servidor. Esta base não inclui uma integração de pagamento pronta.

## Dados salvos antes das contas

A migração de schema acrescenta o proprietário aos registros antigos sem alterar seu conteúdo. Registros anteriores ficam sem proprietário e não são expostos a cadastros novos. O modelo editorial global anterior permanece histórico; modelos de contas precisam de novo treinamento.

Depois de criar a conta destinatária, o administrador local pode conferir a transferência com:

```powershell
.\.venv\Scripts\python.exe .\scripts\migrate-legacy.py --email "email-do-consultor"
```

O comando acima apenas mostra contagens. Para atribuir os registros antigos a essa conta, faça backup do banco e repita com `--apply`. A transferência é uma operação administrativa local, sem endpoint de reivindicação pública. Não há transferência automática para o primeiro cadastro. Traces antigos continuam sem atribuição e não são expostos. O script não transfere dados já atribuídos a outra conta.

## Execução local e implantação futura

Use `scripts/start.ps1` como antes. Na primeira abertura, cadastre sua própria senha na interface; não há usuário nem senha padrão. UI e API devem usar o mesmo hostname (`127.0.0.1` em ambos ou `localhost` em ambos). `VITE_API_URL` substitui a detecção local; ajuste-a quando necessário. CORS deve permitir somente origens explícitas, nunca `*` com credenciais.

Na nuvem, usar HTTPS com `COOKIE_SECURE=true` e UI/API no mesmo site, preferencialmente API sob proxy no domínio da UI. O cookie Strict não funciona entre domínios independentes; definir a hospedagem antes de desenhar essa topologia. Esta entrega é um piloto local: recuperação de senha, verificação de e-mail, pagamento real, políticas de retenção, backups automatizados, limite global de tráfego e infraestrutura de produção ainda não estão implementados. SQLite não está cifrado. Não publicar dados reais apenas porque o login já existe.

Referências técnicas: [OWASP Password Storage — scrypt](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

## Foto e logo por consultor

As imagens são opcionais no cadastro e podem ser incluídas, trocadas ou removidas em **Meu perfil e assinatura**. PNG/JPEG, até 3 MB por arquivo. A foto aparece no avatar do cabeçalho e do perfil na barra lateral após login. A logo aparece na identificação do estúdio e no cabeçalho móvel. Sem imagens, a identidade usa a inicial do nome.

A API aceita `photo` e `logo` como data URLs nos corpos de cadastro e edição de perfil. Os campos correspondentes são devolvidos no perfil da conta autenticada, inclusive no login. Valores `null` na edição removem a imagem; campos omitidos preservam a imagem atual, mantendo compatibilidade com a edição apenas do nome. Imagens inválidas rejeitam a operação inteira, sem salvar parcialmente o nome ou os outros campos.

O servidor valida os bytes e os limites de resolução, aplica a orientação EXIF e reencoda os pixels sem metadados. Foto: JPEG com maior dimensão de até 512 pixels. Logo: PNG com maior dimensão de até 768 pixels e transparência preservada. Os arquivos originais do consultor não são modificados. A gravação acontece somente após o envio do cadastro ou **Salvar perfil**; escolher o arquivo mostra uma prévia local. Enquanto a leitura está em andamento, o envio é bloqueado. Alterações de perfil não salvas também protegem a navegação.

As colunas opcionais `consultants.photo` e `consultants.logo` são acrescentadas aos bancos anteriores, sem alterar nome, senha ou assinatura. As imagens ficam no SQLite local da conta, sem endpoint público por identificador e sem entrar no RAG, na biblioteca ML ou nos traces. Na implantação em nuvem, o armazenamento privado de mídia e a política de retenção precisam acompanhar a infraestrutura de produção.
