"""Avaliação de recuperação ML com consultas independentes, rotuladas pelo consultor.

Não contém corpus/golden artificial apresentado como dado profissional.
"""
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from backend import library, auth, store


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden", required=True)
    parser.add_argument("--consultant-email", required=True, help="Conta proprietária do corpus; operação administrativa local.")
    args = parser.parse_args()
    with auth.connect() as con:
        account = con.execute("SELECT id FROM consultants WHERE email=?", (auth.email(args.consultant_email),)).fetchone()
    if not account:
        raise ValueError("Conta não encontrada.")
    store.tenant.set(account[0])
    queries = json.loads(Path(args.golden).read_text(encoding="utf-8"))
    if not isinstance(queries, list) or len(queries) < 10:
        raise ValueError("Forneça pelo menos dez consultas de teste independentes, revisadas pelo consultor.")
    model = library.status()
    if not model["pronto"]:
        raise ValueError("Autorize os padrões e atualize o modelo antes de avaliar.")
    ids = {r["id"] for r in library.active()}
    results = []
    for query in queries:
        expected = set(query["relevantes"])
        if not expected <= ids:
            raise ValueError("O golden contém referência não autorizada ou retirada.")
        ranked = [r["id"] for r in library.search(query["consulta"])["trechos"]]
        hits = len(set(ranked) & expected)
        precision = hits / min(3, len(ids)) if expected else float(not ranked)
        recall = hits / len(expected) if expected else float(not ranked)
        f1 = 2*precision*recall/(precision+recall) if precision+recall else 0
        reciprocal = next((1/(i+1) for i, rid in enumerate(ranked) if rid in expected), float(not expected and not ranked))
        results.append({"id": query["id"], "recuperados": ranked, "relevantes": sorted(expected),
                        "precision_at_3": precision, "recall_at_3": recall, "f1_at_3": f1,
                        "top1_correto": bool(ranked and ranked[0] in expected) or not ranked and not expected,
                        "reciprocal_rank": reciprocal})
    if not library.status()["pronto"] or library.status()["modelo"]["versao"] != model["modelo"]["versao"]:
        raise RuntimeError("A biblioteca mudou durante a avaliação. Repita com um corpus estável.")
    report = {"modelo": model["modelo"], "consultas": len(results), "k_maximo": 3, "k_efetivo": min(3, len(ids)),
              "limiar": 0.12, "convencao_sem_referencia": "abstenção correta recebe 1 nas métricas por consulta",
              "metricas": {key: sum(float(r[key]) for r in results)/len(results) for key in
                           ("precision_at_3", "recall_at_3", "f1_at_3", "top1_correto", "reciprocal_rank")},
              "resultados": results}
    target = Path(__file__).resolve().parents[1] / "runtime" / "tenants" / store.owner() / "evaluation-editorial.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["metricas"], indent=2))
    print(f"Relatório: {target}")


if __name__ == "__main__":
    main()
