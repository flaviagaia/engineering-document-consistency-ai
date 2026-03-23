from __future__ import annotations

import re

import pandas as pd
from pypdf import PdfReader

from .config import CLAUSES_PATH, CONTRACTS_DIR, ARTIFACTS_DIR


CLAUSE_PATTERN = re.compile(r"^(?P<clause_id>\d+(?:\.\d+)*)\s*-\s*(?P<content>.+)$")


def extract_clauses_from_pdf(path) -> list[dict]:
    reader = PdfReader(str(path))
    rows = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for raw_line in text.splitlines():
            line = " ".join(raw_line.split())
            match = CLAUSE_PATTERN.match(line)
            if not match:
                continue
            rows.append(
                {
                    "document_name": path.name,
                    "page_number": page_number,
                    "clause_id": match.group("clause_id"),
                    "clause_text": match.group("content").strip(),
                }
            )
    return rows


def extract_all_clauses() -> pd.DataFrame:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for pdf_path in sorted(CONTRACTS_DIR.glob("*.pdf")):
        all_rows.extend(extract_clauses_from_pdf(pdf_path))
    df = pd.DataFrame(all_rows)
    df.to_csv(CLAUSES_PATH, index=False)
    return df

