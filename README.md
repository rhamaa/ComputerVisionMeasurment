# Pengukuran Volume Bola menggunakan Computer Vision

Program Python ini menggunakan computer vision untuk mengukur volume benda berbentuk bola secara real-time menggunakan webcam. Program ini pertama-tama melakukan langkah kalibrasi menggunakan bola referensi dengan diameter yang sudah diketahui, kemudian dapat mengukur volume benda berbentuk bola lainnya.

## Fitur

- Deteksi bola secara real-time menggunakan webcam
- Sistem kalibrasi menggunakan objek referensi
- Tampilan langsung dari:
  - Radius bola dalam piksel
  - Rasio kalibrasi (piksel ke milimeter)
  - Diameter saat ini dalam piksel dan milimeter
  - Volume yang dihitung dalam sentimeter kubik (cm³)
- Deteksi objek tunggal untuk menghindari kebingungan
- Proses kalibrasi interaktif

## Prasyarat

Sebelum menjalankan program ini, pastikan Anda telah menginstal:

```bash
- Python 3.8 atau lebih tinggi
- OpenCV (cv2)
- NumPy
```

## Instalasi

1. Clone repository ini atau unduh kode sumber:

```bash
git clone [repository-url]
cd pengukuran-volume-bola
```

2. Buat dan aktifkan virtual environment (direkomendasikan):

```bash
python -m venv venv
source venv/bin/activate  # Untuk Linux/Mac
# atau
.\venv\Scripts\activate  # Untuk Windows
```

3. Instal paket yang diperlukan:

```bash
pip install opencv-python numpy
```

## Cara Penggunaan

1. Jalankan program:

```bash
python main.py
```

2. Ketika jendela kamera terbuka:
   - Letakkan bola referensi Anda (dengan diameter yang diketahui) di depan kamera
   - Pastikan bola terlihat jelas dan lingkaran hijau mendeteksinya dengan baik
   - Tekan 'c' untuk masuk mode kalibrasi
   - Masukkan diameter sebenarnya dari bola referensi Anda dalam milimeter ketika diminta

3. Setelah kalibrasi:
   - Program akan menunjukkan rasio kalibrasi (piksel per milimeter)
   - Anda sekarang dapat mengukur objek berbentuk bola lainnya
   - Pengukuran akan ditampilkan secara real-time di layar

4. Kontrol:
   - Tekan 'c' selama keadaan belum terkalibrasi untuk melakukan kalibrasi
   - Tekan 'q' untuk keluar dari program

## Penyelesaian Masalah

### Masalah Qt/Wayland
Jika Anda mengalami error terkait Qt/Wayland, coba salah satu solusi berikut:

1. Install qt5-wayland:

```bash
sudo apt-get install qt5-wayland
```

2. Atau atur variabel lingkungan QT platform:

```bash
export QT_QPA_PLATFORM=xcb
python main.py
```

### Masalah Umum

1. **Bola tidak terdeteksi:**
   - Pastikan kondisi pencahayaan yang baik
   - Jaga jarak bola pada jarak yang wajar dari kamera
   - Pastikan bola memiliki kontras yang baik dengan latar belakang

2. **Pengukuran tidak akurat:**
   - Kalibrasi ulang menggunakan objek referensi dengan dimensi yang diketahui
   - Jaga jarak bola sama seperti saat kalibrasi
   - Pastikan bola terlihat sepenuhnya dalam frame

## Detail Teknis

Program ini menggunakan teknik computer vision berikut:
- Transformasi Lingkaran Hough untuk deteksi bola
- Gaussian blur untuk pengurangan noise
- Pemrosesan frame real-time dari feed webcam

Perhitungan volume didasarkan pada rumus volume bola: V = (4/3)πr³

## Keterbatasan

- Bekerja paling baik dengan objek berbentuk bola
- Membutuhkan kondisi pencahayaan yang baik
- Akurasi tergantung pada kualitas kalibrasi awal
- Hanya deteksi satu objek
