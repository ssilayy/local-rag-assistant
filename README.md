# Local RAG Assistant

Local RAG Assistant, Foundry Local üzerinde çalışan, tamamen offline bir döküman tabanlı soru-cevap asistanıdır. Kullanıcıların kendi belgelerini yükleyerek bu belgeler üzerinden doğal dilde sorular sorabilmesini sağlar; herhangi bir bulut servisine veya internet bağlantısına ihtiyaç duymadan, verilerin tamamen yerel makinede kalmasını hedefler.

Proje, Retrieval-Augmented Generation (RAG) yaklaşımını kullanarak ilgili belge parçalarını bulur ve bunları yerel dil modeline bağlam olarak sunarak daha doğru ve kaynağa dayalı cevaplar üretir. Bu sayede gizlilik gerektiren veya offline çalışması gereken senaryolarda güvenilir bir soru-cevap deneyimi sunmayı amaçlar.

## Mimari

Proje iki ayrı akıştan oluşur: belgeleri veritabanına kazandıran **ingest** akışı ve kullanıcı sorularını yanıtlayan **sorgu** akışı.

```
Ingest akışı:
  documents/*.txt --(chunk_text)--> paragraf parçaları --(embed_texts)--> vektörler --(insert_document)--> SQLite (documents.db)

Sorgu akışı:
  İstemci (main.py CLI / app.py Streamlit)
        │
        ▼
  rag.py: answer_query(question)
        │
        ▼
  retrieval.py: get_top_chunks(query, k)
        │  1) soruyu embed et (embeddings_demo.embed_texts, qwen3-embedding-0.6b)
        │  2) SQLite'daki tüm chunk embedding'leriyle cosine similarity hesapla
        │  3) en alakalı k chunk'ı (içerik + skor + kaynak dosya adı) döndür
        ▼
  SQLite (documents.db) — documents tablosu: id, content, embedding (JSON), source_name
        │
        ▼
  rag.py: alınan chunk'ları bağlam (context) olarak system prompt'a ekler
        │
        ▼
  Foundry Local LLM (phi-3.5-mini, OpenAI-uyumlu chat completion API)
        │
        ▼
  Kaynak belirtilmiş cevap → istemciye döner
```

Katmanların sorumlulukları:

- **`db.py`** — SQLite üzerinde `documents` tablosunu yönetir (`init_db`, `insert_document`, `get_all_documents`). Embedding vektörleri JSON string olarak saklanır.
- **`embeddings_demo.py`** — Foundry Local'in embedding modelini (`qwen3-embedding-0.6b`) yükler ve `embed_texts(texts)` fonksiyonuyla metinleri vektöre çevirir.
- **`ingest.py`** — `documents/` klasöründeki `.txt` dosyalarını okur, paragraflara böler, embed eder ve SQLite'a kaydeder. Daha önce embed edilmiş chunk'ları atlayarak gereksiz yeniden hesaplamayı önler.
- **`retrieval.py`** — Bir sorguyu embed edip veritabanındaki tüm chunk'larla cosine similarity üzerinden en alakalı `k` tanesini bulur (`get_top_chunks`). Embed ve arama sürelerini loglar.
- **`rag.py`** — Retrieval sonucunu bağlam olarak kullanıp Foundry Local'in chat completion API'si (`phi-3.5-mini`) üzerinden cevap üretir (`answer_query`). Retrieval ve LLM üretim sürelerini loglar.
- **`main.py`** — Konsoldan sürekli soru alan basit bir CLI arayüzü.
- **`app.py`** — Streamlit tabanlı minimal web arayüzü.

## Kullanılan modeller

Modeller Foundry Local üzerinden, tamamen yerel makinede çalıştırılır; ilk kullanımda otomatik olarak indirilip önbelleğe alınır.

| Amaç | Model | Kullanıldığı yer |
|---|---|---|
| Metin üretimi (chat completion) | `phi-3.5-mini` | `rag.py` |
| Embedding (vektöre çevirme) | `qwen3-embedding-0.6b` | `embeddings_demo.py` |

## Kurulum

Ön koşul: Python 3.11 veya üzeri.

### macOS

```bash
git clone <bu-repo>
cd local-rag-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` içindeki `foundry-local-sdk` paketi, Foundry Local çalışma zamanını (native core) da birlikte kurar; macOS'ta ayrı bir uygulama kurulumuna gerek yoktur.

### Windows

```powershell
git clone <bu-repo>
cd local-rag-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Windows'ta donanım hızlandırmalı (Windows ML) çalıştırmak isterseniz `requirements.txt`'teki `foundry-local-sdk` satırını `foundry-local-sdk-winml` ile değiştirip yeniden kurun:

```powershell
pip uninstall foundry-local-sdk
pip install foundry-local-sdk-winml
```

Standart `foundry-local-sdk` paketi Windows'ta da (donanım hızlandırma olmadan) sorunsuz çalışır; `-winml` sürümü sadece daha geniş donanım desteği içindir.

## Çalıştırma talimatları

1. **Kurulumu doğrula:**
   ```bash
   python setup_check.py
   ```

2. **Belgeleri veritabanına işle (ilk çalıştırmada modelleri indirir, biraz sürebilir):**
   ```bash
   python ingest.py
   ```
   `documents/` klasörüne kendi `.txt` dosyalarınızı ekleyip komutu tekrar çalıştırarak veritabanını güncelleyebilirsiniz — sadece yeni/değişen chunk'lar embed edilir.

3. **Konsoldan soru sormak için:**
   ```bash
   python main.py
   ```
   Çıkmak için `exit` yazın.

4. **Web arayüzünden soru sormak için:**
   ```bash
   streamlit run app.py
   ```
   Açılan sayfada metin kutusuna sorunuzu yazıp "Sor" butonuna tıklayın.

5. **Test/doğrulama betikleri:**
   ```bash
   python test_foundry.py      # Chat completion API'sinin temel bağlantı testi
   python test_db.py           # db.py fonksiyonlarının testi
   python test_retrieval.py    # get_top_chunks() için örnek sorgular
   python test_runner.py       # test_queries.json'daki sorularla uçtan uca doğruluk testi
   ```

## Bilinen sınırlamalar

- **Küçük modelin talimat takibi zayıf:** `phi-3.5-mini` küçük ve hızlı bir model olduğu için "sadece bağlamı kullan, yoksa bilmiyorum de" talimatına her zaman uymuyor; bağlam dışı sorularda zaman zaman halüsinasyon yapıp uydurma kaynak adı üretebiliyor (`test_runner.py` çıktısında gözlemlenmiştir).
- **Benzerlik eşiği yok:** `get_top_chunks` her zaman en yakın `k` sonucu döndürür; alakasız bir soruda bile düşük skorlu chunk'lar bağlam olarak modele verilir. Bir minimum benzerlik eşiği eklenmesi bu sorunu azaltabilir.
- **Basit chunking:** Belgeler yalnızca boş satıra göre paragraflara bölünür; çok uzun paragraflar veya örtüşen (overlapping) bağlam pencereleri desteklenmez.
- **Tek kullanıcı / tek makine:** SQLite dosya tabanlı olduğu için eşzamanlı çoklu kullanıcı erişimi veya yazma kilidi yönetimi için tasarlanmamıştır.
- **Performans:** CPU üzerinde yerel çalıştırmada bir sorgunun cevaplanması (embedding + retrieval + LLM üretimi) donanıma bağlı olarak 10-25 saniye sürebilir; `rag.py` ve `retrieval.py` bu süreleri konsola loglar.
- **Deterministik olmayan cevaplar:** `temperature` parametresi ayarlanmadığından aynı soru farklı çalıştırmalarda farklı ifadelerle (hatta farklı doğrulukta) cevaplanabilir.
