import time

import openai
from foundry_local_sdk import Configuration, FoundryLocalManager

from retrieval import get_top_chunks

CHAT_MODEL_ALIAS = "phi-3.5-mini"

SYSTEM_PROMPT = (
    "You are a Q&A assistant. Answer the question using only the given context. "
    "First write a full, clear answer to the question. "
    "If the context doesn't contain the answer, just say 'I don't have this information'. "
    "At the very end of your answer, on a new line, add the source you used "
    "in the format '(Source: file_name.txt)'."
)

_chat_client = None
_chat_model_id = None


def _get_chat_client():
    """Load the Foundry Local chat model and cache an OpenAI-compatible client."""
    global _chat_client, _chat_model_id
    if _chat_client is not None:
        return _chat_client, _chat_model_id

    if FoundryLocalManager.instance is None:
        config = Configuration(app_name="local_rag_assistant")
        FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    manager.download_and_register_eps()

    model = manager.catalog.get_model(CHAT_MODEL_ALIAS)
    model.download(
        lambda progress: print(
            f"\rDownloading model: {progress:.2f}%", end="", flush=True
        )
    )
    print()
    model.load()

    manager.start_web_service()
    base_url = f"{manager.urls[0]}/v1"

    _chat_client = openai.OpenAI(base_url=base_url, api_key="none")
    _chat_model_id = model.id
    return _chat_client, _chat_model_id


def answer_query(question, k=3, source_filter=None):
    """Find relevant context and get a sourced answer from the Foundry Local LLM."""
    retrieval_start = time.perf_counter()
    chunks = get_top_chunks(question, k=k, source_filter=source_filter)
    retrieval_time = time.perf_counter() - retrieval_start

    context = "\n\n".join(
        f"(Source: {source_name})\n{content}"
        for content, _score, source_name in chunks
    )

    client, model_id = _get_chat_client()

    generation_start = time.perf_counter()
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext:\n{context}"},
            {"role": "user", "content": question},
        ],
    )
    generation_time = time.perf_counter() - generation_start

    total_time = retrieval_time + generation_time
    print(
        f"[timing] retrieval (total): {retrieval_time:.3f}s, "
        f"llm generation: {generation_time:.3f}s, total: {total_time:.3f}s"
    )

    return response.choices[0].message.content
