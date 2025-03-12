import sys
import re

def parse_output(output):
    """
    Parses the output from the YOLO and DINO detection system.
    
    Args:
        output (str): The raw output string from the detection system.
    
    Returns:
        str: A formatted string describing detected objects and signals.
    """
    detected_objects = {}
    
    # Regex to extract object detection results
    detection_pattern = re.compile(r"\d+: \d+x\d+ ([\d\s\w,]+)")
    
    match = detection_pattern.search(output)
    if match:
        detections = match.group(1).split(', ')
        for detection in detections:
            parts = detection.split(' ', 1)  # Split at the first space to keep multi-word object names
            if len(parts) == 2:
                count, obj = parts
                if count.isdigit():
                    detected_objects[obj] = int(count)
    
    # Generate object list string
    object_list = list(detected_objects.keys())
    if object_list:
        if len(object_list) == 1:
            objects_str = f"There is {object_list[0]}."
        else:
            objects_str = f"There are {', '.join(object_list[:-1])}, and {object_list[-1]}."
    else:
        objects_str = "No objects detected."
    
    # Regex to extract detected signals
    signal_pattern = re.compile(r"✅ Signal Detected: (\w+)")
    signals = signal_pattern.findall(output)
    
    if "STOP" in signals:
        signal_message = "The walk sign is off. Wait for a moment."
    elif "WALK" in signals:
        signal_message = "The walk sign is on. You can proceed."
    else:
        signal_message = "No traffic signal detected."
    
    return f"{objects_str} {signal_message}"


parsed_result = parse_output(sys.stdin.read())
print(parsed_result)