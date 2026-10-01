"""Consulta ao DuckDB em linguagem natural, somente leitura."""

import re
from pathlib import Path

import duckdb

from rag import generate

ROOT = Path(__file__).resolve().parent
DB = ROOT / "demonstracao.duckdb"

SCHEMA_DOC = """Tabelas (DuckDB, dados fictícios):
consultores(consultor_id, nome_exibicao)
clientes(cliente_id, consultor_id, identificador ['Cliente A'..'Cliente H'], modo ['feminino'|'masculino'], objetivo_imagem)
sessoes(sessao_id, cliente_id, data_sessao DATE, pacote, status ['rascunho'|'em_revisao'|'aprovado'])
medidas(sessao_id, altura_cm, peso_kg, ombro_cm, busto_cm, torax_cm, cintura_cm, quadril_cm, tronco_cm, pernas_cm, biotipo_confirmado)
temperamento(sessao_id, primario, secundario, sanguineo_pct, colerico_pct, melancolico_pct, fleumatico_pct)
visagismo(sessao_id, formato_rosto, posicao_pele, posicao_cabelo, contraste_graus, contraste_faixa ['baixo'|'medio'|'alto'])
teste_coloracao(sessao_id, temperatura, intensidade, profundidade, vermelhos, contraste_observado)
coloracao(sessao_id, cartela [ex.: 'inverno_frio','outono_escuro','verao_suave'], confirmada_pelo_consultor ['sim'|'nao'])
Relações: clientes.cliente_id -> sessoes.cliente_id; sessoes.sessao_id -> demais tabelas."""

SQL_SYSTEM = f"""Você converte perguntas de um(a) consultor(a) de imagem em UMA consulta SQL DuckDB.
{SCHEMA_DOC}
Regras: apenas SELECT (ou WITH ... SELECT); nunca altere dados; valores em minúsculas
com underscore; inclua clientes.identificador quando listar pessoas; LIMIT 50.
Responda só com o SQL, sem explicações nem crases."""

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|copy|attach|install|load|pragma|export|call|set)\b", re.I)


def ensure_db() -> None:
    if not DB.exists():
        import init_db
        init_db.main()


def to_sql(question: str) -> str:
    sql = generate(f"Pergunta: {question}", SQL_SYSTEM, temperature=0)
    sql = re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.M).strip().rstrip(";")
    if not re.match(r"^(select|with)\b", sql, re.I) or FORBIDDEN.search(sql) or ";" in sql:
        raise ValueError("A consulta gerada não é uma leitura segura e foi bloqueada.")
    return sql


def run(sql: str):
    ensure_db()
    con = duckdb.connect(str(DB), read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()


def summarize(question: str, sql: str, table_md: str) -> str:
    return generate(
        f"Pergunta: {question}\nSQL: {sql}\nResultado:\n{table_md}",
        "Explique o resultado em 1–3 frases em português, para um(a) consultor(a). "
        "Não invente dados além da tabela. Lembre que são dados fictícios.",
    )
