"""Avalia recall de fonte; NÃO mede faithfulness ou qualidade da resposta LLM.

Execute `python -m evaluation.retrieval`. Gera evidências locais reais.
"""
import json
from pathlib import Path
from backend.intelligence import retrieve
from backend.guards import check_input

ROOT = Path(__file__).resolve().parents[1]


def main():
    items = json.loads((ROOT / "evaluation" / "golden.json").read_text(encoding="utf-8"))
    results = []
    for item in items:
        if item["tipo"] == "metodologia":
            passages, mode = retrieve(item["pergunta"])
            found = [p["fonte"] for p in passages]
            results.append({"id": item["id"], "tipo": "source_recall_at_4", "passou": item["fonte"] in found, "fontes": found, "modo": mode})
        elif item["tipo"] == "bloqueio":
            blocked = False
            try:
                check_input(item["pergunta"])
            except ValueError:
                blocked = True
            results.append({"id": item["id"], "tipo": "guardrail", "passou": blocked})
    path = ROOT / "runtime" / "evaluation-retrieval.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"resultados": results, "passaram": sum(r["passou"] for r in results), "total": len(results)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f'{sum(r["passou"] for r in results)}/{len(results)} verificações; relatório: {path}')


if __name__ == "__main__":
    main()
