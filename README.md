# ATS Ticari Simülatörü

Türkçe, herkese açık bağlantıyla paylaşılabilecek Streamlit uygulaması.

## Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Yayınlama

1. Bu klasördeki `app.py` ve `requirements.txt` dosyalarını bir GitHub deposuna yükleyin.
2. https://share.streamlit.io adresinden GitHub deposunu seçin; ana dosya `app.py`.
3. Uygulamanın herkese açık olmasını seçin. Üretilen URL'yi paylaşın.

**Dikkat:** Herkese açık sürümde tedarikçi maliyeti ve brüt kârlar görünür. Kullanıcıların ekrandaki değişiklikleri kalıcı olarak saklanmaz.

## Veri güvenilirliği

- Bizim ATS ürününün %N, %S ve saflık analizi doğrulanmamıştır. Başlangıçtaki %98 saflık bir *örnek hammadde senaryosudur*, Avagro ürününe atfedilemez.
- Rakip dozları varsayımdır, üretici etiketi önerisi değildir.
- Alibaba $300–380/ton ilanı, teslim maliyeti veya bağlayıcı fiyat teklifi değildir.
- Ürün fiyatları ilan fiyatlarıdır; KDV dahil/hariç statüsü farklı olabilir. Eşit vergi temeli doğrulanmadan kesin fiyat üstünlüğü sonucu çıkarılmamalıdır.
- Ürünlerin agronomik etkinlik eşdeğerliği kanıtlanmış değildir.
