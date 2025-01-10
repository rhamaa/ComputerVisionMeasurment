import cv2
import numpy as np
import math

class BallVolumeMeasurement:
    def __init__(self):
        self.calibration_ratio = None  # pixels per mm
        self.real_diameter = None      # mm
        self.cap = cv2.VideoCapture(2)
        
    def detect_ball(self, frame):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Blur the image
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        # Detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,  # Increased to avoid multiple detections
            param1=50,
            param2=30,
            minRadius=20,
            maxRadius=300
        )
        
        if circles is not None:
            # Only take the strongest circle detection
            strongest_circle = circles[0][0]
            # Convert coordinates and radius to integers
            x, y, r = strongest_circle
            return (int(x), int(y), int(r))
        return None
    
    def calibrate(self, pixel_diameter, real_diameter):
        """Calculate the ratio of pixels to millimeters"""
        self.calibration_ratio = pixel_diameter / real_diameter
        self.real_diameter = real_diameter
        
    def calculate_volume(self, pixel_diameter):
        """Calculate volume in cubic centimeters (cm³)"""
        if self.calibration_ratio is None:
            return None
            
        # Convert pixel diameter to millimeters
        diameter_mm = pixel_diameter / self.calibration_ratio
        # Calculate radius in centimeters
        radius_cm = (diameter_mm / 2) / 10
        # Calculate volume using sphere formula: V = (4/3)πr³
        volume = (4/3) * math.pi * (radius_cm ** 3)
        return volume
        
    def run(self):
        calibration_done = False
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            circle = self.detect_ball(frame)
            
            if circle is not None:
                # Get circle parameters (already converted to integers in detect_ball)
                x, y, r = circle
                
                # Draw the detected circle
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                
                # Display radius in pixels inside the circle
                radius_text = f"R: {r}px"
                text_size = cv2.getTextSize(radius_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                text_x = x - text_size[0] // 2
                text_y = y
                cv2.putText(frame, radius_text, (text_x, text_y),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                if not calibration_done:
                    cv2.putText(frame, "Press 'c' to calibrate", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    # Display calibration ratio
                    cv2.putText(frame, f"Calibration: {self.calibration_ratio:.2f} px = 1mm", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    
                    # Display current measurements
                    volume = self.calculate_volume(r * 2)  # diameter = 2 * radius
                    if volume is not None:
                        cv2.putText(frame, f"Volume: {volume:.2f} cm³", (10, 60),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Current Diameter: {2*r:.1f} px", (10, 90),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Current Diameter: {(2*r/self.calibration_ratio):.1f} mm", (10, 120),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.imshow('Ball Volume Measurement', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c') and circle is not None and not calibration_done:
                real_diameter = float(input("Enter the real diameter of the ball (in mm): "))
                self.calibrate(2 * circle[2], real_diameter)  # 2 * radius = diameter
                calibration_done = True
                print("Calibration complete!")
                print(f"Calibration ratio: {self.calibration_ratio:.2f} pixels = 1mm")
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    measurement = BallVolumeMeasurement()
    measurement.run()