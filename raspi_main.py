"""
Program Pengukuran Volume dan Berat Bola Menggunakan Computer Vision
----------------------------------------------------------------
Program ini menggunakan kamera untuk mendeteksi bola dan menghitung volumenya secara real-time.
Cara kerja:
1. Menangkap gambar dari kamera
2. Mendeteksi bola menggunakan algoritma Hough Circle Transform
3. Menggunakan rasio kalibrasi statis (3.14 piksel = 1mm)
4. Menghitung volume bola
5. Mengkonversi volume ke berat menggunakan faktor konversi

Penggunaan:
1. Jalankan program
2. Tunjukkan bola ke kamera
3. Tekan 'q' untuk keluar

Dependencies:
- OpenCV (cv2)
- NumPy
- Math
- rpi_lcd (untuk LCD I2C)
"""

import cv2
import numpy as np
import math
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

class BallVolumeMeasurement:
    """
    Kelas utama untuk mengukur volume bola menggunakan computer vision.

    Attributes:
        calibration_ratio: Rasio piksel ke milimeter (static: 3.14 piksel = 1mm)
        cap: Object untuk mengakses kamera
        conversion_factor: Faktor konversi untuk menghitung berat (g/cm³)
        lcd: Object untuk mengakses LCD I2C
    """

    def __init__(self):
        """
        Inisialisasi kelas dengan nilai default.
        Rasio kalibrasi diatur statis: 3.14 piksel = 1mm.
        """
        self.calibration_ratio = 3.14  # Rasio kalibrasi statis
        self.cap = cv2.VideoCapture(0)  # Buka kamera
        self.conversion_factor = 9.0  # Faktor konversi g/cm³ (tetap 9 g/cm³)
        self.lcd = LCD()  # Inisialisasi LCD I2C

        # Tampilkan notifikasi "Start App" di LCD
        self.lcd.text("Start App...", 1)
        self.lcd.text("Tunggu...", 2)

    def detect_ball(self, frame):
        """
        Mendeteksi bola dalam frame menggunakan Hough Circle Transform.

        Args:
            frame: Frame gambar dari kamera (numpy array)

        Returns:
            tuple: (x, y, r) koordinat pusat dan radius bola dalam piksel
            None: Jika tidak ada bola terdeteksi
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=50,
            param2=30,
            minRadius=20,
            maxRadius=300
        )

        if circles is not None:
            strongest_circle = circles[0][0]
            x, y, r = strongest_circle
            return (int(x), int(y), int(r))
        return None

    def calculate_volume(self, pixel_diameter):
        """
        Menghitung volume bola dalam sentimeter kubik (cm³).

        Args:
            pixel_diameter: Diameter bola dalam piksel

        Returns:
            float: Volume bola dalam cm³
        """
        # Konversi diameter piksel ke milimeter
        diameter_mm = pixel_diameter / self.calibration_ratio
        # Hitung radius dalam sentimeter
        radius_cm = (diameter_mm / 2) / 10
        # Hitung volume menggunakan rumus bola
        volume = (4/3) * math.pi * (radius_cm ** 3)
        return volume

    def calculate_volumetric_weight(self, volume):
        """
        Menghitung berat volumetrik berdasarkan faktor konversi.

        Args:
            volume: Volume bola dalam cm³

        Returns:
            float: Berat dalam gram
        """
        return volume * self.conversion_factor

    def run(self):
        """
        Fungsi utama yang menjalankan program secara real-time.

        Kontrol:
        - 'q': Keluar dari program
        """
        while True:
            # Ambil frame dari kamera
            ret, frame = self.cap.read()
            if not ret:
                print("Gagal mengambil frame")
                break

            # Deteksi bola dalam frame
            circle = self.detect_ball(frame)

            if circle is not None:
                # Dapatkan parameter lingkaran
                x, y, r = circle

                # Gambar lingkaran terdeteksi
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

                # Tampilkan radius dalam piksel
                radius_text = f"R: {r}px"
                text_size = cv2.getTextSize(radius_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                text_x = x - text_size[0] // 2
                text_y = y
                cv2.putText(frame, radius_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Hitung diameter dalam piksel dan milimeter
                diameter_px = 2 * r
                diameter_mm = diameter_px / self.calibration_ratio

                # Hitung volume dan berat
                volume = self.calculate_volume(diameter_px)
                volumetric_weight = self.calculate_volumetric_weight(volume)

                # Tampilkan informasi di frame OpenCV
                cv2.putText(frame, f"Kalibrasi: {self.calibration_ratio:.2f} px = 1mm", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                cv2.putText(frame, f"Diameter (px): {diameter_px:.1f} px", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"Diameter (mm): {diameter_mm:.1f} mm", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"Volume: {volume:.2f} cm³", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"Berat: {volumetric_weight:.2f} g", (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # Tampilkan data di LCD (hanya Volume dan Berat)
                self.lcd.text(f"Vol: {volume:.2f} cm3", 1)
                self.lcd.text(f"Berat: {volumetric_weight:.2f} g", 2)

            # Tampilkan frame
            cv2.imshow('Pengukuran Volume Bola', frame)

            # Handle input keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Keluar dari program
                break

        # Bersihkan resources
        self.cap.release()
        cv2.destroyAllWindows()
        self.lcd.clear()  # Bersihkan LCD saat program selesai


if __name__ == "__main__":
    """
    Entry point program.
    Membuat instance BallVolumeMeasurement dan menjalankannya.
    """
    measurement = BallVolumeMeasurement()
    measurement.run()