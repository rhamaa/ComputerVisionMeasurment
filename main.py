"""
Program Pengukuran Volume dan Berat Bola Menggunakan Computer Vision
----------------------------------------------------------------
Program ini menggunakan kamera untuk mendeteksi bola dan menghitung volumenya secara real-time.
Cara kerja:
1. Menangkap gambar dari kamera
2. Mendeteksi bola menggunakan algoritma Hough Circle Transform
3. Melakukan kalibrasi untuk mengkonversi piksel ke milimeter
4. Menghitung volume bola
5. Mengkonversi volume ke berat menggunakan faktor konversi

Penggunaan:
1. Jalankan program
2. Tunjukkan bola ke kamera
3. Tekan 'c' untuk kalibrasi dengan memasukkan diameter bola sebenarnya
4. Tekan 'd' untuk memasukkan faktor konversi
5. Tekan 'q' untuk keluar

Dependencies:
- OpenCV (cv2)
- NumPy
- Math
"""

import cv2
import numpy as np
import math


class BallVolumeMeasurement:
    """
    Kelas utama untuk mengukur volume bola menggunakan computer vision.

    Attributes:
        calibration_ratio: Rasio piksel ke milimeter
        real_diameter: Diameter bola sebenarnya dalam milimeter
        cap: Object untuk mengakses kamera
        conversion_factor: Faktor konversi untuk menghitung berat (g/cm³)
    """

    def __init__(self):
        """
        Inisialisasi kelas dengan nilai default.
        Semua nilai awal diset None karena memerlukan kalibrasi dan input pengguna.
        Membuka koneksi ke kamera default (index 0).
        """
        self.calibration_ratio = None  # Rasio piksel ke milimeter
        self.real_diameter = None      # Diameter sebenarnya dalam mm
        self.cap = cv2.VideoCapture(0)  # Buka kamera
        self.conversion_factor = None  # Faktor konversi g/cm³

    def detect_ball(self, frame):
        """
        Mendeteksi bola dalam frame menggunakan Hough Circle Transform.

        Proses:
        1. Konversi frame ke grayscale
        2. Aplikasikan Gaussian Blur untuk mengurangi noise
        3. Deteksi lingkaran menggunakan HoughCircles

        Args:
            frame: Frame gambar dari kamera (numpy array)

        Returns:
            tuple: (x, y, r) koordinat pusat dan radius bola dalam piksel
            None: Jika tidak ada bola terdeteksi
        """
        # Konversi ke grayscale untuk pemrosesan
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Blur gambar untuk mengurangi noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        # Deteksi lingkaran menggunakan Hough Circle Transform
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,                # Resolusi akumulator
            minDist=100,         # Jarak minimal antar lingkaran
            param1=50,           # Parameter untuk edge detection
            param2=30,           # Parameter untuk deteksi lingkaran
            minRadius=20,        # Radius minimal lingkaran
            maxRadius=300        # Radius maksimal lingkaran
        )

        if circles is not None:
            # Ambil deteksi lingkaran terkuat
            strongest_circle = circles[0][0]
            # Konversi koordinat dan radius ke integer
            x, y, r = strongest_circle
            return (int(x), int(y), int(r))
        return None

    def calibrate(self, pixel_diameter, real_diameter):
        """
        Melakukan kalibrasi untuk menentukan rasio piksel ke milimeter.

        Args:
            pixel_diameter: Diameter bola dalam piksel
            real_diameter: Diameter bola sebenarnya dalam milimeter

        Hasil kalibrasi disimpan dalam self.calibration_ratio
        """
        self.calibration_ratio = pixel_diameter / real_diameter
        self.real_diameter = real_diameter

    def calculate_volume(self, pixel_diameter):
        """
        Menghitung volume bola dalam sentimeter kubik (cm³).

        Proses:
        1. Konversi diameter dari piksel ke milimeter menggunakan rasio kalibrasi
        2. Konversi ke sentimeter
        3. Hitung volume menggunakan rumus bola: V = (4/3)πr³

        Args:
            pixel_diameter: Diameter bola dalam piksel

        Returns:
            float: Volume bola dalam cm³
            None: Jika belum dikalibrasi
        """
        if self.calibration_ratio is None:
            return None

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
            None: Jika volume None atau belum ada faktor konversi
        """
        if volume is None or self.conversion_factor is None:
            return None
        return volume * self.conversion_factor

    def run(self):
        """
        Fungsi utama yang menjalankan program secara real-time.

        Proses:
        1. Capture frame dari kamera
        2. Deteksi bola
        3. Tampilkan visualisasi dan perhitungan
        4. Handle input pengguna untuk kalibrasi dan pengaturan

        Kontrol:
        - 'c': Kalibrasi dengan memasukkan diameter sebenarnya
        - 'd': Set faktor konversi
        - 'q': Keluar dari program
        """
        calibration_done = False  # Flag untuk status kalibrasi
        factor_set = False       # Flag untuk status faktor konversi

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
                # Lingkaran luar (hijau)
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255),
                           3)       # Titik pusat (merah)

                # Tampilkan radius dalam piksel
                radius_text = f"R: {r}px"
                text_size = cv2.getTextSize(
                    radius_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                text_x = x - text_size[0] // 2
                text_y = y
                cv2.putText(frame, radius_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Tampilkan instruksi dan informasi sesuai status
                if not calibration_done:
                    cv2.putText(frame, "Tekan 'c' untuk kalibrasi", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif not factor_set:
                    cv2.putText(frame, "Tekan 'd' untuk set faktor konversi", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    # Tampilkan semua pengukuran
                    cv2.putText(frame, f"Kalibrasi: {self.calibration_ratio:.2f} px = 1mm", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    cv2.putText(frame, f"Faktor Konversi: {self.conversion_factor:.2f} g/cm³", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

                    # Hitung dan tampilkan volume dan berat
                    volume = self.calculate_volume(
                        r * 2)  # diameter = 2 * radius
                    if volume is not None:
                        volumetric_weight = self.calculate_volumetric_weight(
                            volume)

                        cv2.putText(frame, f"Volume: {int(round(volume))} cm³", (10, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Berat: {int(round(volumetric_weight))} g", (10, 120),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Diameter (px): {2*r:.1f} px", (10, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Diameter (mm): {(2*r/self.calibration_ratio):.1f} mm", (10, 180),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Tampilkan frame
            cv2.imshow('Pengukuran Volume Bola', frame)

            # Handle input keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Keluar dari program
                break
            elif key == ord('c') and circle is not None and not calibration_done:
                # Proses kalibrasi
                real_diameter = float(
                    input("Masukkan diameter bola sebenarnya (dalam mm): "))
                # 2 * radius = diameter
                self.calibrate(2 * circle[2], real_diameter)
                calibration_done = True
                print("Kalibrasi selesai!")
                print(f"Rasio kalibrasi: {self.calibration_ratio:.2f} piksel = 1mm")
            elif key == ord('d') and calibration_done and not factor_set:
                # Set faktor konversi
                self.conversion_factor = float(
                    input("Masukkan faktor konversi (dalam g/cm³): "))
                factor_set = True
                print("Pengaturan faktor konversi selesai!")
                print(f"Faktor konversi: {self.conversion_factor:.2f} g/cm³")

        # Bersihkan resources
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    """
    Entry point program.
    Membuat instance BallVolumeMeasurement dan menjalankannya.
    """
    measurement = BallVolumeMeasurement()
    measurement.run()
