"""
Program for Measuring Ball Volume and Weight Using Computer Vision
----------------------------------------------------------------
This program uses a camera to detect a ball and calculate its volume in real-time.
How it works:
1. Capture images from the camera
2. Detect the ball using the Hough Circle Transform algorithm
3. Perform calibration to convert pixels to millimeters
4. Calculate the ball's volume
5. Convert the volume to weight using a conversion factor

Usage:
1. Run the program
2. Show the ball to the camera
3. Press 'c' to calibrate by entering the actual diameter of the ball
4. Press 'd' to enter the conversion factor
5. Press 'q' to exit

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
    Main class for measuring the volume of a ball using computer vision.

    Attributes:
        calibration_ratio: Ratio of pixels to millimeters
        real_diameter: Actual diameter of the ball in millimeters
        cap: Object for accessing the camera
        conversion_factor: Conversion factor for calculating weight (g/cm³)
    """

    def __init__(self):
        """
        Initialize the class with default values.
        All initial values are set to None as they require calibration and user input.
        Opens a connection to the default camera (index 0).
        """
        self.calibration_ratio = None  # Ratio of pixels to millimeters
        self.real_diameter = None      # Actual diameter in mm
        self.cap = cv2.VideoCapture("http://192.168.0.106:4747/video")  # Open the camera
        self.conversion_factor = None  # Conversion factor in g/cm³

    def detect_ball(self, frame):
        """
        Detect the ball in a frame using the Hough Circle Transform.

        Process:
        1. Convert the frame to grayscale
        2. Apply Gaussian Blur to reduce noise
        3. Detect circles using HoughCircles

        Args:
            frame: Image frame from the camera (numpy array)

        Returns:
            tuple: (x, y, r) coordinates of the center and radius of the ball in pixels
            None: If no ball is detected
        """
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Blur the image to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        # Detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,                # Accumulator resolution
            minDist=100,         # Minimum distance between circles
            param1=50,           # Parameter for edge detection
            param2=30,           # Parameter for circle detection
            minRadius=20,        # Minimum circle radius
            maxRadius=300        # Maximum circle radius
        )

        if circles is not None:
            # Get the strongest detected circle
            strongest_circle = circles[0][0]
            # Convert coordinates and radius to integers
            x, y, r = strongest_circle
            return (int(x), int(y), int(r))
        return None

    def calibrate(self, pixel_diameter, real_diameter):
        """
        Perform calibration to determine the ratio of pixels to millimeters.

        Args:
            pixel_diameter: Diameter of the ball in pixels
            real_diameter: Actual diameter of the ball in millimeters

        The calibration result is stored in self.calibration_ratio.
        """
        self.calibration_ratio = pixel_diameter / real_diameter
        self.real_diameter = real_diameter

    def calculate_volume(self, pixel_diameter):
        """
        Calculate the volume of the ball in cubic centimeters (cm³).

        Process:
        1. Convert the diameter from pixels to millimeters using the calibration ratio
        2. Convert to centimeters
        3. Calculate the volume using the sphere formula: V = (4/3)πr³

        Args:
            pixel_diameter: Diameter of the ball in pixels

        Returns:
            float: Volume of the ball in cm³
            None: If not calibrated
        """
        if self.calibration_ratio is None:
            return None

        # Convert pixel diameter to millimeters
        diameter_mm = pixel_diameter / self.calibration_ratio
        # Calculate radius in centimeters
        radius_cm = (diameter_mm / 2) / 10
        # Calculate volume using the sphere formula
        volume = (4/3) * math.pi * (radius_cm ** 3)
        return volume

    def calculate_volumetric_weight(self, volume):
        """
        Calculate the volumetric weight based on the conversion factor.

        Args:
            volume: Volume of the ball in cm³

        Returns:
            float: Weight in grams
            None: If volume is None or the conversion factor is not set
        """
        if volume is None or self.conversion_factor is None:
            return None
        return volume * self.conversion_factor

    def run(self):
        """
        Main function that runs the program in real-time.

        Process:
        1. Capture frames from the camera
        2. Detect the ball
        3. Display visualization and calculations
        4. Handle user input for calibration and settings

        Controls:
        - 'c': Calibrate by entering the actual diameter
        - 'd': Set the conversion factor
        - 'q': Exit the program
        """
        calibration_done = False  # Flag for calibration status
        factor_set = False       # Flag for conversion factor status

        while True:
            # Capture frame from the camera
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                break

            # Detect the ball in the frame
            circle = self.detect_ball(frame)

            if circle is not None:
                # Get circle parameters
                x, y, r = circle

                # Draw the detected circle
                # Outer circle (green)
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                # Center point (red)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

                # Display radius in pixels
                radius_text = f"R: {r}px"
                text_size = cv2.getTextSize(
                    radius_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                text_x = x - text_size[0] // 2
                text_y = y
                cv2.putText(frame, radius_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Display instructions and information based on status
                if not calibration_done:
                    cv2.putText(frame, "Press 'c' to calibrate", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif not factor_set:
                    cv2.putText(frame, "Press 'd' to set conversion factor", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    # Display all measurements
                    cv2.putText(frame, f"Calibration: {self.calibration_ratio:.2f} px = 1mm", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    cv2.putText(frame, f"Conversion Factor: {self.conversion_factor:.2f} g/cm³", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

                    # Calculate and display volume and weight
                    volume = self.calculate_volume(r * 2)  # diameter = 2 * radius
                    if volume is not None:
                        volumetric_weight = self.calculate_volumetric_weight(volume)

                        cv2.putText(frame, f"Volume: {int(round(volume))} cm³", (10, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Weight: {int(round(volumetric_weight))} g", (10, 120),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Diameter (px): {2*r:.1f} px", (10, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Diameter (mm): {(2*r/self.calibration_ratio):.1f} mm", (10, 180),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Display the frame
            cv2.imshow('Ball Volume Measurement', frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Exit the program
                break
            elif key == ord('c') and circle is not None and not calibration_done:
                # Calibration process
                real_diameter = float(
                    input("Enter the actual diameter of the ball (in mm): "))
                # 2 * radius = diameter
                self.calibrate(2 * circle[2], real_diameter)
                calibration_done = True
                print("Calibration complete!")
                print(f"Calibration ratio: {self.calibration_ratio:.2f} pixels = 1mm")
            elif key == ord('d') and calibration_done and not factor_set:
                # Set conversion factor
                self.conversion_factor = float(
                    input("Enter the conversion factor (in g/cm³): "))
                factor_set = True
                print("Conversion factor set!")
                print(f"Conversion factor: {self.conversion_factor:.2f} g/cm³")

        # Clean up resources
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    """
    Entry point program.
    Membuat instance BallVolumeMeasurement dan menjalankannya.
    """
    measurement = BallVolumeMeasurement()
    measurement.run()
