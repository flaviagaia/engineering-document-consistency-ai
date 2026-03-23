from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import CLAUSES_PATH, INCONSISTENCIES_PATH, SIMILARITY_PATH
from src.pipeline import run_pipeline


st.set_page_config(page_title="Engineering Document Consistency AI", layout="wide")
st.title("Engineering Document Consistency AI")
st.caption("Reprodução pública de um pipeline para extração de cláusulas, busca semântica e detecção de inconsistências em documentos de engenharia.")

if st.button("Gerar / atualizar análise"):
    run_pipeline()

try:
    clauses = pd.read_csv(CLAUSES_PATH)
    pairs = pd.read_csv(SIMILARITY_PATH)
    inconsistencies = pd.read_csv(INCONSISTENCIES_PATH)
except FileNotFoundError:
    st.warning("Os artefatos ainda não foram gerados. Clique em 'Gerar / atualizar análise'.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Documentos", clauses["document_name"].nunique())
col2.metric("Cláusulas", len(clauses))
col3.metric("Inconsistências", len(inconsistencies))

st.subheader("Tipos de inconsistência")
if not inconsistencies.empty:
    chart = px.bar(
        inconsistencies["issue_type"].value_counts().reset_index(),
        x="issue_type",
        y="count",
        labels={"issue_type": "Tipo", "count": "Quantidade"},
    )
    st.plotly_chart(chart, use_container_width=True)

st.subheader("Cláusulas extraídas")
st.dataframe(clauses, use_container_width=True, hide_index=True)

st.subheader("Pares semanticamente semelhantes")
st.dataframe(pairs.head(20), use_container_width=True, hide_index=True)

st.subheader("Achados de inconsistência")
st.dataframe(inconsistencies, use_container_width=True, hide_index=True)

