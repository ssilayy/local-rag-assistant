# Demo Script — Local RAG Assistant

## Canlı demoda sorulacak 3 örnek soru

### 1. Normal cevap (dökümanlardan doğrudan yanıtlanabilir)

**Soru:** "SQLite nedir?"

**Beklenen davranış:** Model, `veritabanlari_giris.txt` içeriğini kullanarak SQLite'ın sunucu gerektirmeyen, dosya tabanlı hafif bir ilişkisel veritabanı motoru olduğunu net ve kısa şekilde açıklar.

---

### 2. Kaynak gösteren cevap

**Soru:** "Embedding vektörlerinin benzerliği nasıl ölçülür?"

**Beklenen davranış:** Model, cosine similarity tanımını verir ve cevabın sonunda `(Kaynak: sss_embedding_nedir.txt)` şeklinde kaynağı açıkça belirtir. Bu soru, sistemin kaynak atıf mekanizmasını göstermek için özellikle seçildi — tek ve net bir kaynaktan geldiği için demo'da okunması kolay bir örnek.

---

### 3. "Bilmiyorum" cevabı (dökümanlarda olmayan bilgi)

**Soru:** "2024 yılında en çok izlenen film hangisiydi?"

**Beklenen davranış:** Bu bilgi hiçbir dökümanda yer almadığından model "Bu bilgi elimde yok" demelidir. Bu soru, asistanın bağlam dışı sorularda uydurma (halüsinasyon) yapmak yerine dürüstçe reddetmesini göstermek için seçildi.

> **Not (sunum öncesi mutlaka okuyun):** Kullanılan model (Phi-3.5-mini) küçük ve yerel çalışan bir model olduğu için talimat takibi %100 tutarlı değil — `test_runner.py` sonuçlarında bu tür sorularda bazen doğru reddettiği, bazen de uydurma bir kaynak adı ürettiği gözlemlendi (bkz. README "Bilinen sınırlamalar"). Demo öncesi bu soruyu bir kez deneyip o anki çalıştırmada nasıl davrandığını kontrol edin; beklenmedik bir cevap gelirse bunu "küçük modellerin sınırlaması" olarak açıklamak, canlı demo'nun en öğretici anlarından biri olabilir.

---

## Öğrenilen dersler (sunumda değinilecek 3 madde)

1. **Küçük, yerel modellerin talimat takibi güvenilmez olabilir.** "Sadece bağlamı kullan, yoksa bilmiyorum de" gibi net bir sistem talimatına rağmen Phi-3.5-mini zaman zaman bağlam dışı sorularda halüsinasyon yapıp uydurma kaynak adı üretebiliyor. Prompt mühendisliği tek başına yeterli değil; production bir sistemde ek bir doğrulama katmanı (ör. benzerlik eşiği, cevap sonrası kontrol) gerekir.

2. **Retrieval kalitesi, chunking ve eşik stratejisi kadar iyidir.** Basit paragraf tabanlı bölme ve sabit `k` sonuç döndüren retrieval, alakasız sorularda bile düşük skorlu chunk'ları bağlama sokarak modelin yanlış yönlendirilmesine katkıda bulunuyor. Bir minimum benzerlik eşiği eklemek, "bilmiyorum" davranışını daha güvenilir hale getirebilirdi.

3. **Tamamen offline bir RAG hattı pratik olarak mümkün, ama bedelleri var.** Foundry Local ile internet bağlantısı olmadan uçtan uca (embedding + retrieval + LLM üretimi) çalışan bir sistem kurulabiliyor; ancak CPU üzerinde sorgu başına 10-25 saniyelik gecikme ve deterministik olmayan cevaplar, bulut tabanlı büyük modellere kıyasla kabul edilmesi gereken belirgin ödünler.
