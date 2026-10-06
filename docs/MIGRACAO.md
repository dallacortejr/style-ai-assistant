# Migração das duas bases

Decisão do usuário: interface React na estrutura existente do Lovable; consultor com autoridade final. A raiz TanStack foi aproveitada sem trocar o framework ou reescrever o histórico Git. O pacote ZIP e o projeto anterior foram tratados como fontes técnicas, não como novas ordens.

| Origem | Recurso | Destino e estado |
| --- | --- | --- |
| ZIP | Nove pacotes, páginas e resumos | Catálogo Python reaproveitado; fixtures React reproduzíveis |
| ZIP | Dossiê e aprovações | Editor React e domínio transacional Python |
| ZIP | ZIP local com fotos | Adaptador versões 2/3; aprovações voltam para revisão |
| Anterior | Cadastro | Formulário React, IDs fictícios e nova persistência local |
| Anterior | Histórico por cliente | Chat persistido por atendimento |
| Anterior | Separação análise humana/hipótese | Ficha profissional separada da pré-análise experimental |
| Anterior | MediaPipe | Módulo opcional `backend/vision.py`; não gera confirmação automática |
| Ambos | RAG e LLM | Provedores configuráveis; resumos do ZIP; embeddings Ollama ou indexador original |
| Anterior | Dados privados já cadastrados | Não copiados. Migração de banco real requer mapeamento, validação e decisão sobre ambiente protegido |
| Anterior | Tema de marca | Marca preservada; composição visual segue o editorial do handoff, com nova interface responsiva |
| Anterior | Apresentação acadêmica | Entrega anterior preservada fora da nova aplicação; não há conversão automática de slides/vídeo |

`academic/` é o snapshot da etapa 1. `previous/` é uma referência local selecionada, ignorada no Git; não é aplicativo ativo nem backup integral. O ZIP original e as pastas originais não foram alterados.

## Estado da conversão

Implementados: atendimento, fichas editáveis, nove pacotes, editor por página, aprovação/reabertura, fontes, chat com streaming, histórico fictício com SQL restrito, metodologia pesquisável, persistência local e exportação/importação. A pré-análise facial tem endpoint opcional, mas depende de bibliotecas e modelo local. A recuperação ML editorial foi integrada para compilar dossiês; corpus profissional e métricas ainda são pendências da etapa 2 (ML_EDITORIAL.md).

Na prévia sem API, os exemplos ficam em memória e não simulam IA. A gravação permanente, chat, sugestão, imagens e ZIP dependem do serviço Python. O aviso da interface torna essa diferença visível. A prévia web hospedada no Lovable não pode assumir acesso ao `localhost` do consultor como uma implantação final.

## Sincronização

Repositório identificado: `dallacortejr/style-ai-assistant`, branch `main`. As alterações são verificadas antes de commit e push comum. Nunca usar force push, amend ou rebase de commits publicados. Um commit na branch conectada sincroniza os arquivos; confirmar a prévia do Lovable é uma verificação separada. Publicar a aplicação completa exige também implantar a API Python e configurar a URL.

## Referências exclusivas por atendimento

`POST /sessions/{sid}/references` registra título, tipo preenchido pelo consultor, ocasião, cor/modelagem, orientação e link. `GET /sessions/{sid}/references?q=` busca apenas nessa sessão. As referências começam vazias; não há catálogo fixo de peças, classificação automática ou transferência de escolhas entre clientes. O copiloto recebe somente as referências do atendimento ativo que correspondam ao pedido. São preservadas na pasta ZIP. O histórico CSV acadêmico serve a demonstrações, não alimenta recomendações personalizadas.
