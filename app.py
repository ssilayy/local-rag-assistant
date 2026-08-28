"""Local RAG Assistant için minimal Streamlit tabanlı soru-cevap arayüzü."""

import streamlit as st

from rag import answer_query

st.set_page_config(page_title="Local RAG Assistant")
st.title("Local RAG Assistant")

question = st.text_input("Sorunuzu yazın:")

if st.button("Sor"):
    if question.strip():
        with st.spinner("Cevap oluşturuluyor..."):
            answer = answer_query(question)
        st.text_area("Cevap", value=answer, height=200)
    else:
        st.warning("Lütfen bir soru girin.")
