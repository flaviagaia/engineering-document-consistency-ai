from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CONTRACTS_DIR = DATA_DIR / "contracts"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

CLAUSES_PATH = ARTIFACTS_DIR / "clauses.csv"
SIMILARITY_PATH = ARTIFACTS_DIR / "similar_clause_pairs.csv"
INCONSISTENCIES_PATH = ARTIFACTS_DIR / "inconsistencies.csv"

