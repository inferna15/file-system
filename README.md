# SecureBlock FS

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![Status](https://img.shields.io/badge/status-aktif-brightgreen)

Klasörlerinizi, içeriğini dinamik olarak yönetebileceğiniz, şifreli ve güvenli sanal kasalara dönüştürün.

**SecureBlock FS**, sıradan bir dosya şifreleme aracının ötesinde, verilerinizi yönetilebilir bir sanal dosya sistemi içinde saklayan, Python tabanlı bir masaüstü uygulamasıdır. Bu araçla şifrelenmiş bir "kasa" (vault) dosyası oluşturabilir ve bu kasanın içine tıpkı normal bir klasör gibi yeni dosyalar ekleyebilir, silebilir, yeniden adlandırabilir ve daha fazlasını yapabilirsiniz.

## Proje Hakkında

Bu projenin temel amacı, kullanıcılara verilerini hem güçlü bir şifreleme ile koruma hem de bu şifreli yapı içinde esnek bir şekilde çalışma olanağı sunmaktır. Proje, seçilen bir klasörü ve içeriğini, AES-256 ile şifrelenmiş, blok tabanlı ve **uzantısız tek bir binary dosyaya** dönüştürür. Ayırt edici özelliği, veri bloklarının sırasını rastgele karıştırarak (shuffling) şifrelenmiş veride oluşabilecek desenleri kırması ve böylece ek bir güvenlik katmanı sağlamasıdır.

Oluşturulan şifreli dosya, statik bir arşiv değil, içeriği sonradan değiştirilebilen dinamik bir kasadır.

## Ekran Görüntüleri

*Uygulamanın ana penceresi ve açık bir kasa:*
![Ana Ekran](https://github.com/user-attachments/assets/7e5c1cc3-2b54-48df-ba35-5565a9fd6f69)

*Dosya içeriğini görüntüleme:*
![Dosya Görüntüleme](https://github.com/user-attachments/assets/1d2120cc-8fef-4827-a343-6b76e45ede76)

## Özellikler

### Güvenlik Özellikleri
-   **AES-256 Şifreleme:** Verileriniz, endüstri standardı olan güçlü bir şifreleme algoritması ile korunur.
-   **Rastgele Blok Sıralaması (Shuffling):** Şifreleme öncesi veri bloklarının sırası karıştırılarak kriptografik analizlere karşı dayanıklılık artırılır.
-   **PIN Koruması:** Basit ve hızlı erişim için 4 haneli PIN kullanılır.
-   **Güvenli Anahtar Türetme:** Girilen PIN, PBKDF2 gibi standart bir anahtar türetme fonksiyonu ile güçlü bir şifreleme anahtarına dönüştürülür.

### Dinamik Kasa Yönetimi
-   **Dosya/Klasör Ekleme:** Şifreli kasanın içine sonradan yeni dosyalar ve klasörler eklenebilir.
-   **Dosya/Klasör Silme:** Kasa içindeki veriler güvenli bir şekilde silinebilir.
-   **Yeniden Adlandırma:** Kasa içindeki dosyaların ve klasörlerin adları değiştirilebilir.
-   **İçerik Görüntüleme ve Değiştirme:** Kasa içindeki dosyaların içeriği görüntülenebilir veya değiştirilebilir.
-   **Optimizasyon:** Silinen verilerin kapladığı alanları temizleyerek kasanın dosya boyutunu küçülten bir optimizasyon aracı içerir.

## Kullanılan Teknolojiler
-   **Programlama Dili:** Python 3
-   **Arayüz (GUI):** Tkinter
-   **Kriptografi Kütüphanesi:** PyCryptodome
-   **Görsel İşlemler:** Pillow (PIL Fork)

## Kurulum

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

1.  **Projeyi klonlayın:**
    ```bash
    git clone [https://github.com/kullanici-adiniz/secureblock-fs.git](https://github.com/kullanici-adiniz/secureblock-fs.git)
    cd secureblock-fs
    ```
    <br>
2.  **Gerekli Kütüphaneleri Yükleyin:**
    Ardından kütüphaneleri yüklemek için şu komutu çalıştırın:
    ```bash
    pip install Pillow pycryptodome
    ```
    <br>
3.  **Uygulamayı çalıştırın:**
    ```bash
    python main.py
    ```

## Kullanım

1.  **Yeni Kasa Oluşturma:** Uygulamayı başlatıp "Yeni Kasa Oluştur" seçeneği ile şifrelemek istediğiniz bir klasörü seçin, bir PIN belirleyin ve oluşturulacak **şifreli dosyanın** adını ve konumunu seçin.
2.  **Mevcut Kasayı Açma:** "Kasayı Aç" seçeneği ile daha önce oluşturduğunuz **şifreli dosyanızı** seçip PIN'inizi girerek içeriğini görüntüleyin.
3.  **Yönetim:** Kasa açıkken arayüzdeki butonları kullanarak dosya ekleyebilir, silebilir, yeniden adlandırabilir ve dışa aktarabilirsiniz.
4.  **Optimizasyon:** Özellikle çok sayıda silme işlemi yaptıktan sonra, "Optimize Et" butonunu kullanarak kasanızın dosya boyutunu küçültebilirsiniz.

## ⚠️ Önemli Güvenlik Notu

Bu proje, kriptografi prensiplerini öğrenmek ve uygulamak için harika bir başlangıçtır. Ancak, kullanılan **4 haneli PIN (sadece 10,000 olası kombinasyon) kaba kuvvet (brute-force) saldırılarına karşı dayanıksızdır.**

Bu nedenle, bu araç **yüksek güvenlik gerektiren kritik veya hassas verileri korumak için profesyonel bir çözüm olarak KULLANILMAMALIDIR.** Proje, kişisel gizlilik ve eğitim amaçlı geliştirilmiştir.

## Gelecek Planları ve Geliştirme Fikirleri

-   [ ] Daha güçlü parola desteği (alfanümerik, uzunluk sınırı olmadan).
-   [ ] Anahtar türetme için Argon2 gibi daha modern bir algoritma entegrasyonu.
-   [ ] Büyük dosya operasyonları için ilerleme çubuğu (progress bar).
-   [ ] Sürükle-bırak ile kasa içine dosya ekleme.
-   [ ] Komut satırı arayüzü (CLI) versiyonu.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.
