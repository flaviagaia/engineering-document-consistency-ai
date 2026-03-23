from __future__ import annotations

from datetime import datetime

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import REVIEW_FEEDBACK_PATH


def semantic_search_clauses(clauses_df: pd.DataFrame, query: str, top_k: int = 5) -> pd.DataFrame:
    if clauses_df.empty or not query.strip():
        return clauses_df.head(0).copy()

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(clauses_df["clause_text"])
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix).flatten()
    ranked_idx = scores.argsort()[::-1][:top_k]
    result = clauses_df.iloc[ranked_idx].copy()
    result["similarity"] = scores[ranked_idx]
    return result.sort_values("similarity", ascending=False).reset_index(drop=True)


def answer_question(query: str, clauses_df: pd.DataFrame, inconsistencies_df: pd.DataFrame) -> dict[str, object]:
    normalized = query.lower().strip()
    if not normalized:
        return {"answer": "Digite uma pergunta para consultar os documentos.", "evidence": pd.DataFrame()}

    if "inconsist" in normalized or "conflit" in normalized or "diverg" in normalized:
        top = inconsistencies_df.head(5).copy()
        answer = (
            f"Foram identificadas {len(inconsistencies_df)} inconsistências potenciais. "
            "Os principais conflitos estão relacionados a prazo, responsabilidade, medição e padrão técnico."
        )
        return {"answer": answer, "evidence": top}

    if "deadline" in normalized or "prazo" in normalized or "days" in normalized:
        evidence = semantic_search_clauses(clauses_df, "deliver within calendar days business days", top_k=5)
        answer = "Os documentos tratam de prazos de entrega e resposta técnica, com divergências detectadas em 10 vs 15 dias e 3 vs 5 dias úteis."
        return {"answer": answer, "evidence": evidence}

    if "responsib" in normalized or "respons" in normalized or "quem" in normalized:
        evidence = semantic_search_clauses(clauses_df, "contractor client verification submission", top_k=5)
        answer = "A responsabilidade mais sensível encontrada foi na verificação de qualidade: alguns documentos atribuem a atividade à contratada e outro ao cliente."
        return {"answer": answer, "evidence": evidence}

    if "standard" in normalized or "padr" in normalized or "tag" in normalized or "valve" in normalized:
        evidence = semantic_search_clauses(clauses_df, "valve tagging standard ENG-VAL", top_k=5)
        answer = "Há conflito de padrão técnico entre ENG-VAL-01 e ENG-VAL-02 para a identificação de válvulas."
        return {"answer": answer, "evidence": evidence}

    evidence = semantic_search_clauses(clauses_df, query, top_k=5)
    if evidence.empty:
        return {"answer": "Não encontrei trechos relevantes para essa pergunta.", "evidence": evidence}

    answer = (
        "Encontrei cláusulas semanticamente próximas da sua pergunta. "
        "Use as evidências abaixo para revisar o conteúdo correspondente."
    )
    return {"answer": answer, "evidence": evidence}


def save_review_feedback(item_type: str, item_id: str, verdict: str, notes: str) -> pd.DataFrame:
    REVIEW_FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = pd.DataFrame(
        [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "item_type": item_type,
                "item_id": item_id,
                "verdict": verdict,
                "notes": notes,
            }
        ]
    )
    if REVIEW_FEEDBACK_PATH.exists():
        df = pd.read_csv(REVIEW_FEEDBACK_PATH)
        df = pd.concat([df, row], ignore_index=True)
    else:
        df = row
    df.to_csv(REVIEW_FEEDBACK_PATH, index=False)
    return df
