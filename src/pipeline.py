from __future__ import annotations

from .consistency_analysis import build_similarity_pairs, detect_inconsistencies
from .extract_clauses import extract_all_clauses
from .generate_documents import build_sample_contract_pdfs


def run_pipeline() -> dict[str, int]:
    build_sample_contract_pdfs()
    clauses_df = extract_all_clauses()
    pairs_df = build_similarity_pairs(clauses_df)
    inconsistencies_df = detect_inconsistencies(pairs_df)
    return {
        "documents": clauses_df["document_name"].nunique(),
        "clauses": len(clauses_df),
        "similar_pairs": len(pairs_df),
        "inconsistencies": len(inconsistencies_df),
    }

