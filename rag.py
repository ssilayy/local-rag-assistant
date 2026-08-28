import time

import openai
from foundry_local_sdk import Configuration, FoundryLocalManager

from retrieval import get_top_chunks

CHAT_MODEL_ALIAS = "phi-3.5-mini"

SYSTEM_PROMPT = (
    "Sen bir soru-cevap asistanısın. Sadece verilen bağlamı kullanarak soruyu cevapla. "
    "Önce sorunun tam ve açık cevabını yaz. "
    "Bağlamda cevap yoksa sadece 'Bu bilgi elimde yok' yaz. "
    "Cevabının en sonuna, yeni bir satırda, kullandığın bilginin kaynağını "
    "'(Kaynak: dosya_adi.txt)' formatında ekle."
)

_chat_client = None
_chat_model_id = None


def _get_chat_client():
    """Foundry Local chat modelini yükleyip OpenAI uyumlu istemciyi önbelleğe alır."""
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
            f"\rModel indiriliyor: {progress:.2f}%", end="", flush=True
        )
    )
    print()
    model.load()

    manager.start_web_service()
    base_url = f"{manager.urls[0]}/v1"

    _chat_client = openai.OpenAI(base_url=base_url, api_key="none")
    _chat_model_id = model.id
    return _chat_client, _chat_model_id


def answer_query(question, k=3):
    """İlgili bağlamı bulup Foundry Local LLM'den kaynaklı bir cevap üretir."""
    retrieval_start = time.perf_counter()
    chunks = get_top_chunks(question, k=k)
    retrieval_time = time.perf_counter() - retrieval_start

    context = "\n\n".join(
        f"(Kaynak: {source_name})\n{content}"
        for content, _score, source_name in chunks
    )

    client, model_id = _get_chat_client()

    generation_start = time.perf_counter()
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nBağlam:\n{context}"},
            {"role": "user", "content": question},
        ],
    )
    generation_time = time.perf_counter() - generation_start

    total_time = retrieval_time + generation_time
    print(
        f"[timing] retrieval (toplam): {retrieval_time:.3f}s, "
        f"llm üretim: {generation_time:.3f}s, toplam: {total_time:.3f}s"
    )

    return response.choices[0].message.content
