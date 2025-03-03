import cv2

def extract_roi(image, bbox):
    """
    Extracts the region of interest (ROI) from an image based on a bounding box.

    Args:
        image (numpy array): Input image.
        bbox (tuple): Bounding box coordinates (x1, y1, x2, y2).

    Returns:
        numpy array: Cropped image (ROI).
    """
    x1, y1, x2, y2 = bbox
    return image[y1:y2, x1:x2].copy()
