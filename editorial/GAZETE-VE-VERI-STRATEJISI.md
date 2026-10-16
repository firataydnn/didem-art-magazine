# Gazete ve Veri — Ürün Öncelikleri

**Karar tarihi:** 16 Ekim 2026
**Öncelik sırası:** 1. Gazete 2. Veri 3. Editör araçları.

## Ürün
Gazete güncel, bağımsız, özgün ve görsel açıdan güçlü bir sanat yayınıdır. RSS okuyucu değildir. Okurun gördüğü ürün haber, röportaj, eleştiri, sanat piyasası, sergi rehberi ve arşivdir. Kaynak taraması yalnızca üretim altyapısıdır.

## Gazete veri modeli
- `source`: ad, tür, ülke, URL, feed, kullanım/erişim notu
- `event`: olay türü, gerçekleşme tarihi, yer, kurum, ilgili sanatçılar, doğrulama durumu
- `entity`: sanatçı, eser, galeri, müze, fuar, müzayede evi; alternatif adlar ve kalıcı kimlik
- `source_evidence`: iddia, kaynak URL, erişim tarihi, doğrulama notu
- `asset`: görsel URL/dosya, fotoğrafçı, sanatçı, lisans/izin, kredi, alt metin
- `story`: özgün başlık, spot, gövde, kategori, haber tarihi, ilişkili event/entity, editör, durum, kalıcı slug
- `publication`: onay zamanı, yayın zamanı, revizyon geçmişi, düzeltme kaydı

## Editoryal hat
Kaynak tarama → haber olayı oluşturma → birincil kaynak doğrulama → ilgili kişi/eser/kurum bağlantısı → özgün haber yazımı → görsel izin kontrolü → editör onayı → yayın.

## Yayın kapısı
750 farklı, doğrulanmış, görsel hakları kontrol edilmiş ve onaylı makale olmadan lansman yapılmaz. 1000 makale hedefi korunur. Birbiriyle aynı etkinliği tekrar eden kısa notlar ayrı makale olarak sayılmaz.

## Ölçüm
- Ham haber sayısı
- Benzersiz olay sayısı
- Doğrulanmış olay sayısı
- Özgün tam makale sayısı
- Görseli lisanslı makale sayısı
- Yayına onaylı makale sayısı
- Günlük kaynak kapsama ve başarısız feed sayısı

## Sıradaki sprint
1. Kaynak listesini ülke ve kurum türüne göre genişlet, erişimi doğrula.
2. Ham RSS havuzundan benzersiz olay kayıtlarını ayır.
3. Mevcut kısa haber taslaklarını tekrarsız tam makalelere dönüştür.
4. Gerçek görselleri lisanslarıyla ilişkilendir.
5. Gazete ana sayfasını içerik veri modelinden besle; 750 şartı sağlanmadan canlı yayınlama.

## Sınır
Haber toplama otomasyonu yayın yetkisi vermez. Kullanıcı talebi üzerine gazete ve data çalışmalarına ağırlık verilecek; karmaşık editör paneli şimdilik ikincildir.
