# Local RAG Assistant

I built this project during a Summer program as a way to actually understand how Retrieval-Augmented Generation (RAG) works under the hood, instead of just using an API that does it for me.

It's a document Q&A assistant that runs 100% offline, on your own machine, using Foundry Local. You drop your own `.txt` or `.pdf` files into a folder, it chunks and embeds them, and then you can ask questions in plain language and get answers grounded in your documents — no cloud calls, no API keys, nothing leaves your computer.

## Why offline

I wanted to try building a RAG pipeline where the data genuinely never leaves the machine — no OpenAI calls, no external embedding API. Foundry Local lets you run both the embedding model and the chat model locally, so this felt like a good project to learn the full pipeline end to end: chunking, embedding, similarity search, and prompting an LLM with retrieved context.

## How it works

There are two flows: one for loading documents into the database, and one for answering questions.

```
Ingest:
  documents/*.txt --(chunk into paragraphs)--> embed each chunk --> save to SQLite (documents.db)

Query:
  main.py (CLI) or app.py (Streamlit)
        │
        ▼
  rag.py: answer_query(question)
        │
        ▼
  retrieval.py: embed the question, compare against all stored chunk
  embeddings with cosine similarity, return the top k matches
        │
        ▼
  rag.py: stuff those chunks into the prompt as context
        │
        ▼
  Foundry Local LLM (phi-3.5-mini) generates the answer
        │
        ▼
  Answer + source file name returned to the user
```

Project layout:

```
local-rag-assistant/
├── main.py, db.py, ingest.py, retrieval.py, rag.py, app.py   # main app files
├── documents/                                                 # your .txt / .pdf files go here
├── documents.db                                                # SQLite database
└── tests/                                                      # test scripts and helpers
    ├── embeddings_demo.py   # embed_texts() lives here, used by ingest.py and retrieval.py
    ├── setup_check.py
    ├── test_db.py, test_foundry.py, test_retrieval.py, test_runner.py
    └── test_queries.json
```

What each file does:

- **`db.py`** — manages the `documents` table in SQLite (`init_db`, `insert_document`, `get_all_documents`). Embeddings are stored as JSON strings.
- **`tests/embeddings_demo.py`** — loads the Foundry Local embedding model (`qwen3-embedding-0.6b`) and exposes `embed_texts(texts)`. It's technically in `tests/`, but `ingest.py` and `retrieval.py` both depend on it directly.
- **`ingest.py`** — reads the `.txt` files in `documents/`, splits them into paragraphs, embeds them, and saves everything to SQLite. It skips chunks that were already embedded so you're not recomputing everything on every run.
- **`retrieval.py`** — embeds a query and finds the top `k` most similar chunks in the database using cosine similarity (`get_top_chunks`). Logs timing for embedding and search.
- **`rag.py`** — takes the retrieved chunks, builds a prompt, and calls the Foundry Local chat API (`phi-3.5-mini`) to generate an answer (`answer_query`). Also logs timing.
- **`main.py`** — a small CLI loop for asking questions from the terminal.
- **`app.py`** — a Streamlit web UI for the same thing.

## Models

Everything runs locally through Foundry Local — models get downloaded and cached automatically the first time you use them.

| Purpose | Model | Used in |
|---|---|---|
| Generating answers | `phi-3.5-mini` | `rag.py` |
| Embeddings | `qwen3-embedding-0.6b` | `embeddings_demo.py` |

## Setup

You need Python 3.11 or newer.

### macOS

```bash
git clone <this-repo>
cd local-rag-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` includes `foundry-local-sdk`, which also installs the Foundry Local runtime — no separate app install needed on macOS.

### Windows

```powershell
git clone <this-repo>
cd local-rag-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If you want hardware-accelerated inference on Windows (Windows ML), swap the package after installing:

```powershell
pip uninstall foundry-local-sdk
pip install foundry-local-sdk-winml
```

The regular `foundry-local-sdk` package works fine on Windows too, just without the extra acceleration.

## Running it

1. **Check your setup is working:**
   ```bash
   python tests/setup_check.py
   ```

2. **Load your documents into the database** (first run downloads the models, so it takes a bit):
   ```bash
   python ingest.py
   ```
   Add your own `.txt` files to `documents/` and re-run this whenever you add or change something — it only embeds new/changed chunks.

3. **Ask questions from the terminal:**
   ```bash
   python main.py
   ```
   Type `exit` to quit.

4. **Or use the web UI:**
   ```bash
   streamlit run app.py
   ```
   Type your question in the box and hit "Ask".

5. **Test scripts** (in `tests/`):
   ```bash
   python tests/test_foundry.py      # basic connectivity check for the chat API
   python tests/test_db.py           # tests db.py functions
   python tests/test_retrieval.py    # sample queries for get_top_chunks()
   python tests/test_runner.py       # end-to-end accuracy check using test_queries.json
   ```

## What I'd still improve

Things I noticed while building this that I'd fix with more time:

- **The small model doesn't always follow instructions.** `phi-3.5-mini` is fast but sometimes ignores the "only use the context, say you don't know otherwise" instruction and makes up an answer (and even a fake source name) for out-of-context questions. I saw this happen a few times in `test_runner.py` output.
- **No similarity threshold.** `get_top_chunks` always returns the top `k` results no matter how irrelevant they are, so even a completely unrelated question gets fed some context. Adding a minimum similarity cutoff would probably help.
- **Chunking is very basic.** Documents are split on blank lines only — no handling for very long paragraphs or overlapping windows.
- **Single user, single machine.** SQLite is file-based, so this isn't built for concurrent access.
- **Not fast.** On CPU, a full query (embedding + retrieval + generation) can take 10-25 seconds depending on your hardware. `rag.py` and `retrieval.py` log the timing so you can see where it goes.
- **Answers aren't deterministic.** No `temperature` setting, so the same question can come back worded differently (or with different accuracy) across runs.
