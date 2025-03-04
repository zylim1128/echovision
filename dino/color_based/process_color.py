import cv2
import numpy as np

def detect_traffic_light_color(image):
    """
    Detects the color of a traffic light in the given image.

    Args:
        image (numpy array or str): Input image (either a file path or an image array).

    Returns:
        str: "walk" if the light is white, "stop" if the light is red, else "unknown".
    """
    # Load image if a file path is provided
    if isinstance(image, str):
        image = cv2.imread(image)
    
    if image is None:
        print("Error: Could not load image")
        return "unknown"

    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color ranges for detection (adjust as needed)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])

    # Create masks
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    # Count pixels in each mask
    red_pixels = cv2.countNonZero(red_mask)
    white_pixels = cv2.countNonZero(white_mask)

    # Determine signal
    if white_pixels > red_pixels:
        return "walk"
    elif red_pixels > white_pixels:
        return "stop"
    else:
        return "unknown"
