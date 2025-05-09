# Ball Volume Measurement using Computer Vision

This Python program uses computer vision to measure the volume of spherical objects in real-time using a webcam. The program first performs a calibration step using a reference ball with a known diameter, then it can measure the volume of other spherical objects.

## Features

- Real-time ball detection using a webcam
- Calibration system using a reference object
- Live display of:
  - Ball radius in pixels
  - Calibration ratio (pixels to millimeters)
  - Current diameter in pixels and millimeters
  - Calculated volume in cubic centimeters (cm³)
- Single object detection to avoid confusion
- Interactive calibration process

## Prerequisites

Before running this program, make sure you have installed:

```bash
- Python 3.8 or higher
- OpenCV (cv2)
- NumPy
```

## Installation

1. Clone this repository or download the source code:

```bash
git clone [repository-url]
cd ball-volume-measurement
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
.\venv\Scripts\activate  # For Windows
```

3. Install the required packages:

```bash
pip install opencv-python numpy
```

## Usage

1. Run the program:

```bash
python main.py
```

2. When the camera window opens:
   - Place your reference ball (with a known diameter) in front of the camera
   - Ensure the ball is clearly visible and the green circle detects it well
   - Press 'c' to enter calibration mode
   - Enter the actual diameter of your reference ball in millimeters when prompted

3. After calibration:
   - The program will display the calibration ratio (pixels per millimeter)
   - You can now measure other spherical objects
   - Measurements will be displayed in real-time on the screen

4. Controls:
   - Press 'c' while uncalibrated to perform calibration
   - Press 'q' to exit the program

## Troubleshooting

### Qt/Wayland Issues
If you encounter errors related to Qt/Wayland, try one of the following solutions:

1. Install qt5-wayland:

```bash
sudo apt-get install qt5-wayland
```

2. Or set the QT platform environment variable:

```bash
export QT_QPA_PLATFORM=xcb
python main.py
```

### Common Issues

1. **Ball not detected:**
   - Ensure good lighting conditions
   - Keep the ball at a reasonable distance from the camera
   - Ensure the ball has good contrast with the background

2. **Inaccurate measurements:**
   - Recalibrate using a reference object with known dimensions
   - Keep the ball at the same distance as during calibration
   - Ensure the ball is fully visible in the frame

## Technical Details

This program uses the following computer vision techniques:
- Hough Circle Transform for ball detection
- Gaussian blur for noise reduction
- Real-time frame processing from the webcam feed

Volume calculation is based on the formula for the volume of a sphere: V = (4/3)πr³

## Limitations

- Works best with spherical objects
- Requires good lighting conditions
- Accuracy depends on the quality of the initial calibration
- Detects only one object

## Auto Start with Systemd

### Create a service file in /etc/systemd/system/ball_volume.service

```bash
sudo nano /etc/systemd/system/ball_volume.service
Fill the service file with the following configuration:
```

```ini
[Unit]
Description=Ball Volume Measurement Service
After=network.target

[Service]
User=nuurr
WorkingDirectory=/home/nuurr/Documents/ComputerVisionMeasurment
ExecStart=/home/nuurr/Documents/ComputerVisionMeasurment/venv/bin/python /home/nuurr/Documents/ComputerVisionMeasurment/raspi_main.py
Restart=always
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/nuurr/.Xauthority

[Install]
WantedBy=multi-user.target
```

### Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable ball_volume.service
sudo systemctl start ball_volume.service
```

### Verify service status

```bash
sudo systemctl status ball_volume.service
```

## NOTE
For the Raspberry Pi 4 version (`raspi_main.py`), ensure the distance between the webcam and the reading surface is 30 cm for better reading accuracy.
