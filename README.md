# Musica Pro Omnibus

Musica Pro Omnibus, DJ performansları ve stüdyo üretimine yönelik açık kaynaklı bir araç takımıdır. Proje ilk olarak bir hayal olarak başlasa da, kod altyapısının büyük kısmı Codex tarafından geliştirildi. Amacı, yaraticilara esnek, modüler ve yapay zeka destekli bir ses ortamı sunmaktır.

## Öne Çıkan Özellikler

- **Dört Deck'li Mikser**: Aynı anda birden fazla parçayı çalıp miksleyin.
- **Düşük Gecikmeli Ses Motoru**: `sounddevice` tabanlı zincir mikro gecikme ile çalışır.
- **Gerçek Zamanlı Stem Ayrıştırma**: Vokal ve enstrümantali anında ayırma desteği.
- **Bulut Tabanlı Ses Üretimi**: Hugging Face MusicGen API ile metinden sese.
- **Yapay Zeka Araçları**: GrooveAssistant, SampleRecommender ve AIRemixer gibi modüller yaratıcılığı besler.
- **Eklenti Sistemi**: Python tabanlı efektleri dinamik olarak yüklenir.
- **Üretim Araçları**: Piyano rulosu, zaman çizelgesi, otomasyon ve temel bir synthesizer.
- **Bulut Senkronizasyonu ve Uzak Kontrol**: Projeleri senkronize edin, Flask‑SocketIO ile uzaktan erişin.

## Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/<kullanici>/<repo>.git
   cd <repo>
   ```
2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   ```bash
   python main.py
   ```

### Exe olarak paketleme

Uygulamayı tek dosya olarak dağıtmak için PyInstaller kullanılabilir:

```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

Oluşan çalıştırılabilir `dist/main` içinde yer alacaktır ve Python kurulumu olmayan
sistemlerde de çalışabilir.

PyQt5, seste geri çalma ve GUI için gereklidir; bazı AI özellikleri `librosa` ve `spleeter` gibi ek paketler ister.

## Testler

Projede yer alan birim testlerini çalıştırmak için:
```bash
pytest -q
```

## Katkı ve Lisans

Musica Pro Omnibus MIT lisansı altında sunulur. Proje geliştirme şu an dış katkilara kapalıdır.

