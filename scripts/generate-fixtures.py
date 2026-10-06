"""Regenera a prévia React apenas dos CSVs fictícios e resumos próprios."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.store import seeds
from academic import pacotes, knowledge_index

packages = [{"id": k, "nome": pacotes.nome(k), "formato": v[1], "paginas": list(pacotes.paginas(k))}
            for k, v in pacotes.PACOTES.items()]
documents = [{"arquivo": p.name, "titulo": p.stem[3:].replace("_", " "), "conteudo": p.read_text(encoding="utf-8")}
             for p in sorted(knowledge_index.KNOWLEDGE.glob("[0-9][0-9]_*.md"))]
target = ROOT / "src" / "features" / "consultoria" / "fixtures.ts"
target.write_text('import type { Session, Package } from "./types";\n'
                  + "export const sampleSessions: Session[] = " + json.dumps(seeds(), ensure_ascii=False, indent=2) + ";\n"
                  + "export const packages: Package[] = " + json.dumps(packages, ensure_ascii=False, indent=2) + ";\n"
                  + "export const knowledge = " + json.dumps(documents, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
print("Prévia regenerada. Formate fixtures.ts com Prettier antes do commit.")
