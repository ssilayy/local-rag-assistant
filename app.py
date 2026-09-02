"""Minimal Streamlit-based Q&A interface for the Local RAG Assistant."""

import html

import streamlit as st

from db import get_source_names
from rag import answer_query

ALL_SOURCES_LABEL = "All sources"

EXAMPLE_QUESTIONS = [
    "What were the capitals of the Ottoman Empire, in order?",
    "When and how did the Roman Empire fall?",
    "What is Retrieval-Augmented Generation (RAG) and how does it work?",
]


def set_example_question(text):
    st.session_state["question_input"] = text
    st.session_state["run_example"] = True


st.set_page_config(
    page_title="Local RAG Assistant",
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
    div[data-testid="stForm"] {
        margin-bottom: 2.5rem;
    }
    .answer-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    .answer-card .question-line {
        font-weight: 700;
        color: #1f2937;
        font-size: 1.05rem;
        margin-bottom: 0.6rem;
    }
    .answer-card .source-box {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 1rem;
    }
    .answer-card .source-box .source-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        color: #6b7280;
    }
    .answer-card .source-box .source-value {
        font-size: 0.85rem;
        font-weight: 600;
        color: #374151;
    }
    .answer-card h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        color: #1f2937;
        font-size: 1.05rem;
        font-weight: 700;
        border-top: 1px solid #f1f5f9;
        padding-top: 1rem;
    }
    .answer-text {
        font-size: 1rem;
        line-height: 1.6;
        color: #111827;
        white-space: pre-wrap;
    }
    section[data-testid="stSidebar"] .sidebar-heading {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        color: #6b7280;
        margin-bottom: 0.75rem;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background-color: white;
        color: #374151;
        border: 1px solid #d1d5db;
        text-align: left;
        font-weight: 500;
        white-space: normal;
        height: auto;
        margin-bottom: 0.5rem;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #eef2ff;
        color: #4338ca;
        border-color: #c7d2fe;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Local RAG Assistant")
st.markdown(
    '<div class="subtitle">Ask questions about your local documents.</div>',
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

source_names = get_source_names()
source_options = [ALL_SOURCES_LABEL] + source_names

with st.sidebar:
    st.markdown('<div class="sidebar-heading">Example questions</div>', unsafe_allow_html=True)
    for example_question in EXAMPLE_QUESTIONS:
        st.button(
            example_question,
            key=f"example_{example_question}",
            on_click=set_example_question,
            args=(example_question,),
            use_container_width=True,
        )

with st.form("qa_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        question = st.text_input(
            "Your question:",
            placeholder="e.g. What is the return policy?",
            key="question_input",
        )
    with col2:
        selected_source = st.selectbox("Source:", source_options)

    ask_clicked = st.form_submit_button("Ask")

run_flag = ask_clicked or st.session_state.pop("run_example", False)

if run_flag:
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
                <div class="source-box">
                    <span class="source-label">Source</span>
                    <span class="source-value">{html.escape(entry['source'])}</span>
                </div>
                <h3>Answer</h3>
                <div class="answer-text">{html.escape(entry['answer'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
