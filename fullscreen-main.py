import cv2
import numpy as np
import math
from screeninfo import get_monitors

class BallVolumeMeasurement:
    def __init__(self):
        self.calibration_ratio = None  # pixels per mm
        self.real_diameter = None      # mm
        self.cap = cv2.VideoCapture(2)
        
        # Get primary monitor resolution
        monitor = get_monitors()[0]
        self.screen_width = monitor.width
        self.screen_height = monitor.height
        
        # Set camera resolution to maximum available
        resolutions = [
            (1920, 1080),  # Full HD
            (1280, 720),   # HD
            (800, 600),    # SVGA
            (640, 480)     # VGA
        ]
        
        # Try setting resolution from highest to lowest until one works
        for width, height in resolutions:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if actual_width == width and actual_height == height:
                print(f"Camera resolution set to: {width}x{height}")
                break
        
    def detect_ball(self, frame):
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
    
    def calibrate(self, pixel_diameter, real_diameter):
        self.calibration_ratio = pixel_diameter / real_diameter
        self.real_diameter = real_diameter
        
    def calculate_volume(self, pixel_diameter):
        if self.calibration_ratio is None:
            return None
        diameter_mm = pixel_diameter / self.calibration_ratio
        radius_cm = (diameter_mm / 2) / 10
        volume = (4/3) * math.pi * (radius_cm ** 3)
        return volume
        
    def run(self):
        calibration_done = False
        cv2.namedWindow('Ball Volume Measurement', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Ball Volume Measurement', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Resize frame to fill screen while maintaining aspect ratio
            frame_height, frame_width = frame.shape[:2]
            screen_ratio = self.screen_width / self.screen_height
            frame_ratio = frame_width / frame_height
            
            if frame_ratio > screen_ratio:
                new_width = self.screen_width
                new_height = int(new_width / frame_ratio)
            else:
                new_height = self.screen_height
                new_width = int(new_height * frame_ratio)
                
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Create black background of screen size
            background = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
            
            # Calculate position to center the frame
            y_offset = (self.screen_height - new_height) // 2
            x_offset = (self.screen_width - new_width) // 2
            
            # Place the frame in the center of the background
            background[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = frame
            
            frame = background  # Use the centered frame
                
            circle = self.detect_ball(frame)
            
            if circle is not None:
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
                    cv2.putText(frame, f"Calibration: {self.calibration_ratio:.2f} px = 1mm", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    
                    volume = self.calculate_volume(r * 2)
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
                self.calibrate(2 * circle[2], real_diameter)
                calibration_done = True
                print("Calibration complete!")
                print(f"Calibration ratio: {self.calibration_ratio:.2f} pixels = 1mm")
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    measurement = BallVolumeMeasurement()
    measurement.run()