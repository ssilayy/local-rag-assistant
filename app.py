"""Minimal Streamlit-based Q&A interface for the Local RAG Assistant."""

import html

import streamlit as st

from db import get_source_names
from rag import answer_query

ALL_SOURCES_LABEL = "All sources"

st.set_page_config(
    page_title="Local RAG Assistant",
    page_icon="📚",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
    }
    h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
        margin-bottom: 0.2rem !important;
    }
    .subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 0.6rem 0.8rem;
    }
    div[data-testid="stSelectbox"] > label,
    div[data-testid="stTextInput"] > label {
        font-weight: 600;
        color: #374151;
    }
    .stButton > button,
    .stFormSubmitButton > button {
        background-color: #4f46e5;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #4338ca;
        color: white;
    }
    .history-heading {
        margin-top: 2rem;
        margin-bottom: 0.75rem;
        color: #374151;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .answer-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    .answer-card .question-line {
        font-weight: 700;
        color: #1f2937;
        font-size: 1.05rem;
        margin-bottom: 0.3rem;
    }
    .answer-card .source-tag {
        display: inline-block;
        background-color: #eef2ff;
        color: #4338ca;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 999px;
        padding: 0.15rem 0.6rem;
        margin-bottom: 0.8rem;
    }
    .answer-card h3 {
        margin-top: 0;
        color: #1f2937;
        font-size: 1.1rem;
    }
    .answer-text {
        font-size: 1rem;
        line-height: 1.6;
        color: #111827;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 Local RAG Assistant")
st.markdown(
    '<div class="subtitle">Ask questions about your local documents.</div>',
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

source_names = get_source_names()
source_options = [ALL_SOURCES_LABEL] + source_names

with st.form("qa_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        question = st.text_input(
            "Your question:", placeholder="e.g. What is the return policy?"
        )
    with col2:
        selected_source = st.selectbox("Source:", source_options)

    ask_clicked = st.form_submit_button("Ask")

if ask_clicked:
    if question.strip():
        source_filter = None if selected_source == ALL_SOURCES_LABEL else selected_source
        with st.spinner("Generating answer..."):
            answer = answer_query(question, source_filter=source_filter)
        st.session_state.history.insert(
            0,
            {
                "question": question,
                "answer": answer,
                "source": selected_source,
            },
        )
    else:
        st.warning("Please enter a question.")

if st.session_state.history:
    st.markdown('<div class="history-heading">Conversation history</div>', unsafe_allow_html=True)
    for entry in st.session_state.history:
        st.markdown(
            f"""
            <div class="answer-card">
                <div class="question-line">Q: {html.escape(entry['question'])}</div>
                <div class="source-tag">{html.escape(entry['source'])}</div>
                <h3>Answer</h3>
                <div class="answer-text">{html.escape(entry['answer'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
