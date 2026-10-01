"""Cria o DuckDB de demonstração a partir de CSVs inteiramente fictícios.

Uso: python academic/init_db.py [caminho/para/demonstracao.duckdb]
"""

import csv
import sys
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "demonstracao.duckdb"

# Ordem das dependências: consultor -> cliente -> sessão -> análises.
SCHEMA = {
    "consultores": "consultor_id VARCHAR PRIMARY KEY, nome_exibicao VARCHAR NOT NULL",
    "clientes": "cliente_id VARCHAR PRIMARY KEY, consultor_id VARCHAR NOT NULL REFERENCES consultores(consultor_id), identificador VARCHAR NOT NULL, modo VARCHAR NOT NULL, objetivo_imagem VARCHAR",
    "sessoes": "sessao_id VARCHAR PRIMARY KEY, cliente_id VARCHAR NOT NULL REFERENCES clientes(cliente_id), data_sessao DATE NOT NULL, pacote VARCHAR NOT NULL, status VARCHAR NOT NULL",
    "medidas": "sessao_id VARCHAR PRIMARY KEY REFERENCES sessoes(sessao_id), altura_cm DOUBLE, peso_kg DOUBLE, ombro_cm DOUBLE, busto_cm DOUBLE, torax_cm DOUBLE, cintura_cm DOUBLE, quadril_cm DOUBLE, tronco_cm DOUBLE, pernas_cm DOUBLE, biotipo_confirmado VARCHAR",
    "temperamento": "sessao_id VARCHAR PRIMARY KEY REFERENCES sessoes(sessao_id), primario VARCHAR, secundario VARCHAR, sanguineo_pct INTEGER, colerico_pct INTEGER, melancolico_pct INTEGER, fleumatico_pct INTEGER",
    "visagismo": "sessao_id VARCHAR PRIMARY KEY REFERENCES sessoes(sessao_id), formato_rosto VARCHAR, posicao_pele INTEGER, posicao_cabelo INTEGER, contraste_graus INTEGER, contraste_faixa VARCHAR",
    "teste_coloracao": "sessao_id VARCHAR PRIMARY KEY REFERENCES sessoes(sessao_id), temperatura VARCHAR, intensidade VARCHAR, profundidade VARCHAR, vermelhos VARCHAR, contraste_observado VARCHAR",
    "coloracao": "sessao_id VARCHAR PRIMARY KEY REFERENCES sessoes(sessao_id), cartela VARCHAR, confirmada_pelo_consultor VARCHAR",
}


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(TARGET))
    try:
        for table in reversed(SCHEMA):
            con.execute(f"DROP TABLE IF EXISTS {table}")
        for table, columns in SCHEMA.items():
            con.execute(f"CREATE TABLE {table} ({columns})")
            path = DATA / f"{table}.csv"
            with path.open(encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                fields = reader.fieldnames
                if fields is None:
                    raise ValueError(f"CSV sem cabeçalho: {path}")
                placeholders = ", ".join("?" for _ in fields)
                rows = [[row[field] or None for field in fields] for row in reader]
            if rows:
                con.executemany(
                    f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})",
                    rows,
                )
            print(f"{table}: {len(rows)} registros")
        print(f"Banco criado em: {TARGET}")
    finally:
        con.close()


if __name__ == "__main__":
    main()