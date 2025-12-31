import streamlit as st
from maestroia.graphs.marketing_graph import build_marketing_graph

st.title("MaestroIA Marketing Dashboard")

graph = build_marketing_graph()

objetivo = st.text_input("Objetivo da Campanha")
publico = st.text_input("Público-Alvo")
canais = st.multiselect("Canais", ["Instagram", "Google Ads", "Facebook"])
orcamento = st.number_input("Orçamento", min_value=0.0)

if st.button("Executar Campanha"):
    state = {
        "objetivo": objetivo,
        "publico_alvo": publico,
        "canais": canais,
        "orcamento": orcamento
    }
    result = graph.invoke(state)
    st.json(result)