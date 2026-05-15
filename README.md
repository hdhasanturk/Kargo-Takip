# Kargo-Takip

Kargo takip ve yonetim uygulamasi (Flet + SQLite).

## Ozellikler
- Personel girisi ve kayit
- Kargo olusturma, listeleme, guncelleme
- Takip sorgu (gonderici/alici)
- Guzergah ve fiyat hesaplama

## Gereksinimler
- Python 3.10+
- Windows PowerShell (veya baska bir terminal)

## Kurulum (Windows)
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Calistirma
```
python main.py
```

## Gercek takip (Ship24)
- `.env` dosyasina API anahtarini ekleyin:
```
SHIP24_API_KEY=your_ship24_api_key_here
```
- API cevap vermezse uygulama mock veriyi kullanir.
- En iyi sonuc icin kargo eklerken "Gercek Takip No" ve "Courier Code" alanlarini doldurun.
- Ship24 loglari `logs/ship24.log` altina yazilir.

## Uygulama loglari
- Genel uygulama loglari `logs/app.log` altina yazilir.

## Varsayilan admin
- Kullanici adi: admin
- Sifre: 123456

## Konum verisi
- Uygulama `data/turkiye_locations.db` dosyasini otomatik olusturur (Yeni Kargo Ekle ekraninda).
- Elle yuklemek isterseniz:
```
python import_location_data.py
```
- Alternatif olarak:
```
python create_locations_db.py
```

## Notlar
- Ana uygulama veritabani: `kargo_takip.db`
- Konum JSON kaynagi: `turkiye-city-county-district-neighborhood-main/data.json`

## Manuel test araclari
```
python test_location.py
python test_dropdown.py
```
