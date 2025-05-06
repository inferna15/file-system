# Binary Dosya Sistemi Projesi

Bu projenin amacı, seçilen bir dosyayı kök dosya olarak alıp altındaki tüm dosya ve klasörlerle birlikte özel bir binary dosya sistemi oluşturmaktır.

## Projenin Amacı

Geleneksel dosya sistemleri yalnızca şifreleme ile korunmasına rağmen, içerikler belleğe doğrusal olarak yazıldığı için bazı bölümlere bakılarak diğer bölümler tahmin edilebilir. Bu proje, bu güvenlik açığını ortadan kaldırmayı hedeflemektedir.

## Özellikler

- Seçilen kök klasör ve altındaki tüm dosyalar, özel bir binary formatta saklanır.
- Dosya içerikleri sabit boyuttaki (örneğin 1 KB) parçalara bölünür ve bu parçalar karıştırılarak (shuffle edilerek) kaydedilir.
- Dosya sistemi, AES (Advanced Encryption Standard) algoritmasıyla şifrelenmektedir.
- 4 haneli bir şifre ile giriş yapılmaktadır.
- Dosya yapısı ve içeriği doğrudan okunamaz hâle gelir, yalnızca uygulama tarafından çözülebilir.
- Sistem çalışır hâlde ve veri ekleme, çıkarma gibi işlemler başarıyla gerçekleştirilebilmektedir.

## Notlar

- Şifreleme aşaması isteğe bağlı olarak sonradan devreye alınabilir.
- Proje, güvenli ve verimli bir yedekleme / saklama çözümü sağlamayı amaçlamaktadır.
- Özellikle güvenlik, tersine mühendislikten korunma ve veri gizliliği önceliklidir.

[Önceki Versiyon](https://github.com/inferna15/shuffle-files)
