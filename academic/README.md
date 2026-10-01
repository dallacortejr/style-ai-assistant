# Dados fictícios para a Etapa 1

Os CSVs em `data/` formam uma demonstração sintética: um perfil genérico de consultor(a), oito clientes identificados apenas por letras, sessões do Pacote 1 e análises de temperamento, visagismo, medidas e coloração. **Nenhuma linha deriva dos dossiês reais.** Nomes, datas, medidas, objetivos, diagnósticos e combinações foram inventados exclusivamente para testar o funcionamento. Não são orientação clínica nem diagnósticos reais.

## Carregar o DuckDB

```bash
pip install duckdb
python academic/init_db.py
```

O comando gera `academic/demonstracao.duckdb` localmente a partir dos CSVs. O arquivo gerado não precisa ir ao GitHub; os CSVs são a fonte reproduzível. Também é possível passar outro caminho como argumento. Execute novamente para recarregar o mesmo banco.

## Relações e exemplos de consulta

`consultores` → `clientes` → `sessoes` → (`medidas`, `temperamento`, `visagismo`, `teste_coloracao`, `coloracao`). Cada análise se liga a uma sessão por `sessao_id`; várias sessões futuras podem pertencer à mesma pessoa.

```sql
-- Quantos atendimentos têm cartela Inverno Frio confirmada?
SELECT count(*) AS total
FROM sessoes s JOIN coloracao c ON c.sessao_id = s.sessao_id
WHERE c.cartela = 'inverno_frio' AND c.confirmada_pelo_consultor = 'sim';

-- Medidas da Cliente A e a classificação confirmada pelo consultor(a)
SELECT cl.identificador, m.ombro_cm, m.cintura_cm, m.quadril_cm,
       m.biotipo_confirmado
FROM clientes cl
JOIN sessoes s ON s.cliente_id = cl.cliente_id
JOIN medidas m ON m.sessao_id = s.sessao_id
WHERE cl.identificador = 'Cliente A';

-- Diagnósticos pendentes de aprovação, agrupados por cartela
SELECT c.cartela, count(*) AS total
FROM coloracao c
JOIN sessoes s ON s.sessao_id = c.sessao_id
WHERE c.confirmada_pelo_consultor = 'nao'
GROUP BY c.cartela ORDER BY c.cartela;
```

Campos vazios em medidas são **não aplicáveis**, não zeros (por exemplo, tórax no modo feminino). A cartela é um registro de teste e `confirmada_pelo_consultor` distingue proposta de aprovação humana. Imagens e recomendações de produtos não fazem parte deste conjunto inicial; quando adicionadas, serão exemplos gerais separados dos registros editáveis de cada atendimento.

## Busca de conhecimento (Etapa 1)

Os oito resumos aprovados em `knowledge/` são a única fonte do índice; apostilas e livros originais não são indexados. As seções são divididas em trechos de até 350 palavras, com nome do resumo, tema, nível e seção como referência. A busca prioriza termos precisos da pergunta além da semelhança semântica.

```bash
pip install -r academic/requirements.txt
python academic/knowledge_index.py --rebuild
python academic/knowledge_index.py --ask "Como avaliar o contraste pessoal?"
```

O primeiro comando de indexação baixa um modelo multilíngue gratuito e grava `academic/chroma_store/` localmente. Execute-o novamente se algum resumo for atualizado. O módulo `academic/rag.py` combina a busca com o Gemini, citando fontes; sem `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`), retorna somente os trechos encontrados e avisa que a resposta ainda não foi gerada. **A geração Gemini não foi testada sem uma chave de API.** Nunca publique a chave no repositório.