import cv2
import numpy as np

def detect_traffic_light_color(image_path):
    """
    Detects whether the traffic light is showing a 'walk' (white) or 'stop' (red) signal.

    Args:
        image_path (str): Path to the traffic light image.
    
    Returns:
        str: 'walk' if white is dominant, 'stop' if red is dominant, 'unknown' otherwise.
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not load image. Check the file path.")

    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color ranges
    red_lower1 = np.array([0, 100, 100])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 100, 100])
    red_upper2 = np.array([180, 255, 255])
    
    white_lower = np.array([0, 0, 200])
    white_upper = np.array([180, 50, 255])

    # Create masks
    red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    red_mask = red_mask1 + red_mask2  # Combine both red ranges

    white_mask = cv2.inRange(hsv, white_lower, white_upper)

    # Count pixels in each mask
    red_pixels = np.sum(red_mask > 0)
    white_pixels = np.sum(white_mask > 0)

    # Decide based on dominant color
    if red_pixels > white_pixels:
        return "stop"
    elif white_pixels > red_pixels:
        return "walk"
    else:
        return "unknown"

# Example usage:
if __name__ == "__main__":
    image_path = "/mmfs1/gscratch/krishna/zylim/echovision/test_images/intersection-1.png"  # TODO: put path here
    result = detect_traffic_light_color(image_path)
    print(f"Detected signal: {result}")
