from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import CLAUSES_PATH, INCONSISTENCIES_PATH, REVIEW_FEEDBACK_PATH, SIMILARITY_PATH
from src.pipeline import run_pipeline
from src.query_assistant import answer_question, save_review_feedback, semantic_search_clauses


st.set_page_config(page_title="Engineering Document Assistant", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.14), transparent 28%),
            radial-gradient(circle at top right, rgba(34, 197, 94, 0.10), transparent 26%),
            radial-gradient(circle at bottom center, rgba(99, 102, 241, 0.12), transparent 24%),
            #050816;
        color: #e2e8f0;
    }
    .hero-card, .soft-card {
        background: rgba(8, 15, 32, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 20px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.36);
        backdrop-filter: blur(12px);
    }
    .hero-card h1 {
        margin: 0 0 0.3rem 0;
        font-size: 2rem;
        color: #f8fafc;
    }
    .hero-card p, .soft-card p {
        margin: 0;
        color: #cbd5e1;
    }
    .pill-row {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    .pill {
        background: rgba(37, 99, 235, 0.18);
        color: #bfdbfe;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        font-size: 0.92rem;
        font-weight: 600;
        border: 1px solid rgba(96, 165, 250, 0.18);
    }
    [data-testid="stMetric"] {
        background: rgba(8, 15, 32, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 18px;
        padding: 0.9rem 1rem;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: #e2e8f0;
    }
    [data-testid="stTabs"] button[role="tab"] {
        background: rgba(15, 23, 42, 0.75);
        border-radius: 999px;
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.14);
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.30), rgba(16, 185, 129, 0.22));
        color: #f8fafc;
    }
    [data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {
        background: rgba(8, 15, 32, 0.82);
        border-radius: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <h1>Engineering Document Assistant</h1>
        <p>Consulte documentos, encontre cláusulas parecidas e revise conflitos de forma guiada, sem precisar navegar por relatórios técnicos brutos.</p>
        <div class="pill-row">
            <div class="pill">Consulta em linguagem natural</div>
            <div class="pill">Busca semântica</div>
            <div class="pill">Revisão humana</div>
            <div class="pill">Análise de inconsistências</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([1, 2])
with top_left:
    if st.button("Atualizar documentos e análise", use_container_width=True):
        run_pipeline()
with top_right:
    st.markdown(
        """
        <div class="soft-card">
            <p>Esta demonstração pública usa documentos sintéticos de engenharia para reproduzir um fluxo integrado de ingestão, extração de cláusulas, comparação entre documentos e revisão assistida.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

try:
    clauses = pd.read_csv(CLAUSES_PATH)
    pairs = pd.read_csv(SIMILARITY_PATH)
    inconsistencies = pd.read_csv(INCONSISTENCIES_PATH)
except FileNotFoundError:
    st.warning("Os artefatos ainda não foram gerados. Clique em 'Atualizar documentos e análise'.")
    st.stop()

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Documentos disponíveis", clauses["document_name"].nunique())
metric_2.metric("Cláusulas encontradas", len(clauses))
metric_3.metric("Trechos comparáveis", len(pairs))
metric_4.metric("Conflitos potenciais", len(inconsistencies))

tab_assistant, tab_conflicts, tab_documents, tab_search, tab_review, tab_technical = st.tabs(
    [
        "Assistente",
        "Conflitos Encontrados",
        "Documentos",
        "Buscar Trechos",
        "Revisão",
        "Detalhes Técnicos",
    ]
)

with tab_assistant:
    st.subheader("Faça uma pergunta sobre os documentos")
    st.caption("Exemplos: 'Quais são os principais conflitos de prazo?' ou 'Quem é responsável pela verificação de qualidade?'")

    example_col1, example_col2, example_col3 = st.columns(3)
    if example_col1.button("Prazos críticos", use_container_width=True):
        st.session_state["doc_question"] = "Quais são os principais conflitos de prazo?"
    if example_col2.button("Responsabilidades", use_container_width=True):
        st.session_state["doc_question"] = "Quem é responsável pela verificação de qualidade?"
    if example_col3.button("Padrões técnicos", use_container_width=True):
        st.session_state["doc_question"] = "Existe conflito de padrão técnico?"

    question = st.text_input(
        "Sua pergunta",
        value=st.session_state.get("doc_question", "Quais são os principais conflitos de prazo?"),
        key="doc_question",
    )

    if question.strip():
        qa_result = answer_question(question, clauses, inconsistencies)
        st.markdown("### Resposta")
        st.write(qa_result["answer"])
        if isinstance(qa_result["evidence"], pd.DataFrame) and not qa_result["evidence"].empty:
            st.markdown("### Evidências mais relevantes")
            st.dataframe(qa_result["evidence"], use_container_width=True, hide_index=True)

with tab_conflicts:
    st.subheader("Resumo dos conflitos detectados")
    if not inconsistencies.empty:
        count_df = inconsistencies["issue_type"].value_counts().rename_axis("issue_type").reset_index(name="count")
        st.plotly_chart(
            px.bar(
                count_df,
                x="issue_type",
                y="count",
                labels={"issue_type": "Tipo de conflito", "count": "Quantidade"},
                color="issue_type",
            ),
            use_container_width=True,
        )

        selected_type = st.selectbox("Filtrar por tipo de conflito", ["Todos"] + sorted(inconsistencies["issue_type"].unique().tolist()))
        view = inconsistencies if selected_type == "Todos" else inconsistencies[inconsistencies["issue_type"] == selected_type]
        view = view.copy()
        view["resumo"] = view["left_document"] + "  x  " + view["right_document"]
        st.dataframe(
            view[["resumo", "left_clause_id", "right_clause_id", "issue_type", "left_value", "right_value", "explanation"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("Nenhum conflito potencial foi identificado.")

with tab_documents:
    st.subheader("Documentos e cláusulas")
    document_names = sorted(clauses["document_name"].unique().tolist())
    selected_document = st.selectbox("Escolha um documento", document_names)
    document_clauses = clauses[clauses["document_name"] == selected_document].copy()

    summary_cols = st.columns(3)
    summary_cols[0].metric("Cláusulas no documento", len(document_clauses))
    summary_cols[1].metric("Primeira página", int(document_clauses["page_number"].min()))
    summary_cols[2].metric("Última página", int(document_clauses["page_number"].max()))

    for row in document_clauses.itertuples():
        with st.container(border=True):
            st.markdown(f"**Cláusula {row.clause_id}**")
            st.write(row.clause_text)

with tab_search:
    st.subheader("Buscar trechos parecidos")
    query = st.text_input("O que você quer localizar nos documentos?", value="delivery deadline for 3D model revision")
    top_k = st.slider("Quantidade de resultados", min_value=3, max_value=10, value=5)
    if query.strip():
        search_results = semantic_search_clauses(clauses, query, top_k=top_k)
        if search_results.empty:
            st.info("Nenhum trecho relevante foi encontrado.")
        else:
            for row in search_results.itertuples():
                with st.container(border=True):
                    st.markdown(f"**{row.document_name} | cláusula {row.clause_id}**")
                    st.write(row.clause_text)
                    st.caption(f"Similaridade: {row.similarity:.3f}")

with tab_review:
    st.subheader("Validação humana")
    st.caption("Use esta área para confirmar se o conflito encontrado faz sentido do ponto de vista do negócio.")

    review_options = [
        f"{row.left_document}::{row.left_clause_id} <> {row.right_document}::{row.right_clause_id} [{row.issue_type}]"
        for row in inconsistencies.itertuples()
    ]

    if review_options:
        selected_issue = st.selectbox("Selecione um conflito para revisar", review_options)
        selected_idx = review_options.index(selected_issue)
        finding = inconsistencies.iloc[selected_idx]

        issue_col1, issue_col2 = st.columns(2)
        with issue_col1:
            st.markdown("**Documento A**")
            st.write(finding["left_document"])
            st.write(f"Cláusula: {finding['left_clause_id']}")
            st.write(f"Valor detectado: {finding['left_value']}")
        with issue_col2:
            st.markdown("**Documento B**")
            st.write(finding["right_document"])
            st.write(f"Cláusula: {finding['right_clause_id']}")
            st.write(f"Valor detectado: {finding['right_value']}")

        st.info(finding["explanation"])

        verdict = st.radio(
            "Como você avalia esse achado?",
            options=["approved", "rejected", "needs_review"],
            format_func=lambda value: {
                "approved": "👍 Faz sentido",
                "rejected": "👎 Não faz sentido",
                "needs_review": "🕵️ Precisa de análise adicional",
            }[value],
            horizontal=True,
        )
        notes = st.text_area("Comentário ou justificativa", height=120)
        if st.button("Salvar avaliação"):
            item_id = f"{finding['left_document']}::{finding['left_clause_id']}::{finding['right_document']}::{finding['right_clause_id']}"
            save_review_feedback("inconsistency", item_id, verdict, notes)
            st.success("Avaliação salva com sucesso.")
    else:
        st.info("Não há conflitos para revisar no momento.")

    if REVIEW_FEEDBACK_PATH.exists():
        with st.expander("Ver histórico de avaliações"):
            st.dataframe(pd.read_csv(REVIEW_FEEDBACK_PATH).tail(20), use_container_width=True, hide_index=True)

with tab_technical:
    st.subheader("Detalhes técnicos")
    st.caption("Esta aba mantém a rastreabilidade técnica, mas fica separada da experiência principal do usuário.")
    tech_col1, tech_col2 = st.columns(2)
    with tech_col1:
        st.markdown("**Pares semanticamente semelhantes**")
        st.dataframe(pairs.head(20), use_container_width=True, hide_index=True)
    with tech_col2:
        st.markdown("**Base completa de inconsistências**")
        st.dataframe(inconsistencies, use_container_width=True, hide_index=True)
