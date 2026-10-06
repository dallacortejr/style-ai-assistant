"""Atribuição administrativa explícita. Sem --apply apenas informa contagens."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from backend import auth, library


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    # Inicializa somente o schema, sem criar registros ou treinar modelos.
    with library.connect():
        pass
    with auth.connect() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT id,name FROM consultants WHERE email=?", (auth.email(args.email),)).fetchone()
        if not row:
            raise SystemExit("Conta não encontrada. Cadastre o destinatário na interface primeiro.")
        counts = {table: con.execute(f"SELECT COUNT(*) FROM {table} WHERE consultant_id IS NULL").fetchone()[0] for table in ("sessions", "editorial")}
        print(f"Destino: {row[1]}. Atendimentos antigos: {counts['sessions']}; padrões: {counts['editorial']}.")
        if args.apply:
            for table in counts:
                con.execute(f"UPDATE {table} SET consultant_id=? WHERE consultant_id IS NULL", (row[0],))
            print("Transferência aplicada. Treine novamente a biblioteca editorial na conta destinatária.")
        else:
            print("Somente conferência. Faça backup antes de aplicar a transferência com --apply.")


if __name__ == "__main__":
    main()
