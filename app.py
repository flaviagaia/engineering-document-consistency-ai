from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import CLAUSES_PATH, INCONSISTENCIES_PATH, REVIEW_FEEDBACK_PATH, SIMILARITY_PATH
from src.pipeline import run_pipeline
from src.query_assistant import answer_question, save_review_feedback, semantic_search_clauses


st.set_page_config(page_title="Engineering Document Consistency AI", layout="wide")
st.title("Engineering Document Consistency AI")
st.caption(
    "Hub único para ingestão de documentos, extração de cláusulas, busca semântica, detecção de inconsistências e revisão humana."
)

top_a, top_b = st.columns([1, 3])
with top_a:
    if st.button("Gerar / atualizar base", use_container_width=True):
        run_pipeline()
with top_b:
    st.info(
        "Esta versão pública reproduz a lógica de uma plataforma integrada de documentos de engenharia usando PDFs sintéticos, TF-IDF, similaridade semântica e revisão humana."
    )

try:
    clauses = pd.read_csv(CLAUSES_PATH)
    pairs = pd.read_csv(SIMILARITY_PATH)
    inconsistencies = pd.read_csv(INCONSISTENCIES_PATH)
except FileNotFoundError:
    st.warning("Os artefatos ainda não foram gerados. Clique em 'Gerar / atualizar base'.")
    st.stop()

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Documentos", clauses["document_name"].nunique())
metric_2.metric("Cláusulas", len(clauses))
metric_3.metric("Pares similares", len(pairs))
metric_4.metric("Inconsistências", len(inconsistencies))

tab_ingestion, tab_clauses, tab_search, tab_consistency, tab_review, tab_qa = st.tabs(
    [
        "Ingestão",
        "Cláusulas",
        "Busca Semântica",
        "Consistência",
        "Revisão Humana",
        "Pergunte aos Documentos",
    ]
)

with tab_ingestion:
    st.subheader("Documentos ingeridos")
    ingest_summary = clauses.groupby("document_name").agg(
        clauses=("clause_id", "count"),
        first_page=("page_number", "min"),
        last_page=("page_number", "max"),
    ).reset_index()
    st.dataframe(ingest_summary, use_container_width=True, hide_index=True)
    st.caption("Os PDFs são sintéticos, mas foram construídos para simular memoriais, anexos e instruções técnicas com conflitos reais de engenharia.")

with tab_clauses:
    st.subheader("Cláusulas extraídas")
    selected_document = st.selectbox("Filtrar documento", ["Todos"] + sorted(clauses["document_name"].unique().tolist()))
    clauses_view = clauses if selected_document == "Todos" else clauses[clauses["document_name"] == selected_document]
    st.dataframe(clauses_view, use_container_width=True, hide_index=True)

with tab_search:
    st.subheader("Busca semântica entre cláusulas")
    query = st.text_input("Consulta", value="delivery deadline for 3D model revision")
    top_k = st.slider("Top K", min_value=3, max_value=10, value=5)
    if query.strip():
        search_results = semantic_search_clauses(clauses, query, top_k=top_k)
        st.dataframe(search_results, use_container_width=True, hide_index=True)

with tab_consistency:
    st.subheader("Análise de inconsistência")
    if not inconsistencies.empty:
        count_df = inconsistencies["issue_type"].value_counts().rename_axis("issue_type").reset_index(name="count")
        st.plotly_chart(
            px.bar(count_df, x="issue_type", y="count", labels={"issue_type": "Tipo", "count": "Quantidade"}),
            use_container_width=True,
        )
    st.dataframe(inconsistencies, use_container_width=True, hide_index=True)
    st.caption("A detecção atual usa similaridade semântica para recuperar pares de cláusulas comparáveis e regras para identificar conflito objetivo.")

with tab_review:
    st.subheader("Revisão humana dos achados")
    review_options = [
        f"{row.left_document}::{row.left_clause_id} <> {row.right_document}::{row.right_clause_id} [{row.issue_type}]"
        for row in inconsistencies.itertuples()
    ]
    if review_options:
        selected_issue = st.selectbox("Selecione um achado", review_options)
        selected_idx = review_options.index(selected_issue)
        finding = inconsistencies.iloc[selected_idx]
        st.markdown(f"**Resumo:** {finding['explanation']}")
        verdict = st.radio(
            "O achado faz sentido?",
            options=["approved", "rejected", "needs_review"],
            format_func=lambda value: {
                "approved": "👍 Confirmado",
                "rejected": "👎 Rejeitado",
                "needs_review": "🕵️ Precisa de análise",
            }[value],
            horizontal=True,
        )
        notes = st.text_area("Justificativa / observações", height=120)
        if st.button("Salvar revisão"):
            item_id = f"{finding['left_document']}::{finding['left_clause_id']}::{finding['right_document']}::{finding['right_clause_id']}"
            save_review_feedback("inconsistency", item_id, verdict, notes)
            st.success("Revisão salva.")
    else:
        st.info("Nenhum achado disponível para revisão.")

    if REVIEW_FEEDBACK_PATH.exists():
        st.markdown("**Histórico recente**")
        st.dataframe(pd.read_csv(REVIEW_FEEDBACK_PATH).tail(20), use_container_width=True, hide_index=True)

with tab_qa:
    st.subheader("Pergunte aos documentos")
    question = st.text_input("Pergunta", value="Quais são os principais conflitos de prazo?")
    if question.strip():
        qa_result = answer_question(question, clauses, inconsistencies)
        st.write(qa_result["answer"])
        if isinstance(qa_result["evidence"], pd.DataFrame) and not qa_result["evidence"].empty:
            st.markdown("**Evidências**")
            st.dataframe(qa_result["evidence"], use_container_width=True, hide_index=True)
