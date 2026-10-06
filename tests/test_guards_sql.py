import pytest
from backend.guards import anonymize, check_input, check_output
from backend import intelligence


def test_pii_redaction():
    redacted = anonymize("CPF 123.456.789-00 e contato teste@example.com")
    assert "123.456" not in redacted and "teste@example.com" not in redacted


def test_normal_domain_question_not_blocked():
    assert check_input("Como explicar contraste de coloração para Cliente A?")


def test_output_cannot_auto_approve():
    with pytest.raises(ValueError):
        check_output("Este texto está automaticamente aprovado.")


@pytest.mark.parametrize("sql", ["SELECT * FROM read_csv_auto('C:/secret.csv')", "SELECT * FROM sqlite_master", "DELETE FROM clientes", "SELECT 1; SELECT 2", "SELECT * FROM range(1000000000)"])
def test_sql_cannot_access_external_sources(monkeypatch, sql):
    monkeypatch.setattr(intelligence, "llm", lambda _: (sql, {}))
    with pytest.raises(ValueError):
        intelligence.query_demo("Listar dados")


def test_relational_query_works(monkeypatch):
    sql = "SELECT c.identificador, s.pacote FROM clientes c JOIN sessoes s ON c.cliente_id = s.cliente_id"
    monkeypatch.setattr(intelligence, "llm", lambda _: (sql, {}))
    data, _ = intelligence.query_demo("Listar clientes e pacotes")
    assert len(data["linhas"]) == 8
