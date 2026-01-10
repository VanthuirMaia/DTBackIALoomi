"""
Script para importar dados do CSV para a tabela paints.

Uso: python scripts/import_csv.py

Idempotente: não duplica registros se executado múltiplas vezes.
"""

import csv
import sys
from pathlib import Path

# Bootstrap: adiciona o diretório backend ao path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.paint import Paint


def import_csv():
    csv_path = backend_dir / "data" / "Base_de_Dados_de_Tintas_Suvinil.csv"

    if not csv_path.exists():
        print(f"Erro: Arquivo não encontrado: {csv_path}")
        sys.exit(1)

    session = SessionLocal()
    inserted = 0
    skipped = 0

    try:
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Idempotência: verifica se já existe pelo nome
                existing = session.query(Paint).filter(
                    Paint.nome == row["nome"]
                ).first()

                if existing:
                    skipped += 1
                    continue

                paint = Paint(
                    nome=row["nome"],
                    cor=row["cor"],
                    tipo_superficie=row["tipo_superficie"],
                    ambiente=row["ambiente"],
                    acabamento=row["acabamento"],
                    features=row["features"],
                    linha=row["linha"],
                )
                session.add(paint)
                inserted += 1

        session.commit()
        print(f"Importação concluída!")
        print(f"  - Registros inseridos: {inserted}")
        print(f"  - Registros ignorados (já existiam): {skipped}")
        print(f"  - Total no CSV: {inserted + skipped}")

    except Exception as e:
        session.rollback()
        print(f"Erro durante importação: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    import_csv()
