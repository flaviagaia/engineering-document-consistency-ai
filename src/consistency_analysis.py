from __future__ import annotations

import re
from itertools import combinations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import ARTIFACTS_DIR, INCONSISTENCIES_PATH, SIMILARITY_PATH


RESPONSIBLE_PATTERN = re.compile(r"\b(contractor|client)\b", re.IGNORECASE)
DAYS_PATTERN = re.compile(r"\b(\d+)\s+(calendar|business)\s+days\b", re.IGNORECASE)
MEASUREMENT_PATTERN = re.compile(r"based on approved ([a-z ]+)", re.IGNORECASE)
STANDARD_PATTERN = re.compile(r"standard ([A-Z0-9-]+)", re.IGNORECASE)


def _extract_signature(text: str) -> dict[str, str]:
    lowered = text.lower()
    responsible = RESPONSIBLE_PATTERN.search(lowered)
    days = DAYS_PATTERN.search(lowered)
    measurement = MEASUREMENT_PATTERN.search(lowered)
    standard = STANDARD_PATTERN.search(text)
    return {
        "responsible_party": responsible.group(1).lower() if responsible else "",
        "time_window": f"{days.group(1)} {days.group(2).lower()} days" if days else "",
        "measurement_basis": measurement.group(1).strip().lower() if measurement else "",
        "technical_standard": standard.group(1).strip().upper() if standard else "",
    }


def build_similarity_pairs(clauses_df: pd.DataFrame, similarity_threshold: float = 0.45) -> pd.DataFrame:
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(clauses_df["clause_text"])
    sims = cosine_similarity(matrix)
    rows = []
    for i, j in combinations(range(len(clauses_df)), 2):
        left = clauses_df.iloc[i]
        right = clauses_df.iloc[j]
        if left["document_name"] == right["document_name"]:
            continue
        if left["clause_id"] != right["clause_id"] and sims[i, j] < similarity_threshold:
            continue
        rows.append(
            {
                "left_document": left["document_name"],
                "left_clause_id": left["clause_id"],
                "left_text": left["clause_text"],
                "right_document": right["document_name"],
                "right_clause_id": right["clause_id"],
                "right_text": right["clause_text"],
                "similarity": round(float(sims[i, j]), 4),
            }
        )
    pairs_df = pd.DataFrame(rows).sort_values(["similarity", "left_clause_id"], ascending=[False, True]).reset_index(drop=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    pairs_df.to_csv(SIMILARITY_PATH, index=False)
    return pairs_df


def detect_inconsistencies(pairs_df: pd.DataFrame) -> pd.DataFrame:
    findings = []
    for _, row in pairs_df.iterrows():
        left_sig = _extract_signature(row["left_text"])
        right_sig = _extract_signature(row["right_text"])
        for field, label in [
            ("responsible_party", "responsibility mismatch"),
            ("time_window", "deadline mismatch"),
            ("measurement_basis", "measurement mismatch"),
            ("technical_standard", "technical standard mismatch"),
        ]:
            left_value = left_sig[field]
            right_value = right_sig[field]
            if left_value and right_value and left_value != right_value:
                findings.append(
                    {
                        "left_document": row["left_document"],
                        "left_clause_id": row["left_clause_id"],
                        "right_document": row["right_document"],
                        "right_clause_id": row["right_clause_id"],
                        "issue_type": label,
                        "left_value": left_value,
                        "right_value": right_value,
                        "similarity": row["similarity"],
                        "explanation": (
                            f"Potential {label}: '{row['left_document']}' says '{left_value}' "
                            f"while '{row['right_document']}' says '{right_value}'."
                        ),
                    }
                )
    inconsistencies_df = pd.DataFrame(findings).drop_duplicates().reset_index(drop=True)
    inconsistencies_df.to_csv(INCONSISTENCIES_PATH, index=False)
    return inconsistencies_df

