import sys
import re

def parse_output(output):
    """
    Parses the output from the YOLO and DINO detection system.
    
    Args:
        output (str): The raw output string from the detection system.
    
    Returns:
        str: A formatted string describing the scene, warnings, and signals.
    """
    detected_objects = {}

    # Regex to extract object detection results
    detection_pattern = re.compile(r"\d+: \d+x\d+\s([\d\s\w,]+)")
    
    match = detection_pattern.search(output)
    if match:
        detections = match.group(1).split(', ')
        for detection in detections:
            parts = detection.split(' ', 1)  # Split at the first space to keep multi-word object names
            if len(parts) == 2:
                count, obj = parts
                if count.isdigit():
                    detected_objects[obj] = int(count)

    # Extract close warnings
    warning_pattern = re.compile(r"Warning: (.+)")  
    close_warnings = warning_pattern.findall(output)

    # Ensure warnings influence the scene description
    warning_mentions_person = any("person" in w for w in close_warnings)
    warning_mentions_car = any("car" in w for w in close_warnings)

    people_count = detected_objects.get("persons", 0)
    car_count = detected_objects.get("cars", 0)
    light_count = detected_objects.get("traffic lights", 0)
    handbag_count = detected_objects.get("handbag", 0)

    # Update scene description to avoid contradictions
    if people_count or warning_mentions_person:
        if car_count or warning_mentions_car:
            scene_description = "You're on a busy street with several people walking and cars passing by."
        else:
            scene_description = "You're in an area with people walking around."
    elif car_count or warning_mentions_car:
        scene_description = "There are cars moving nearby."
    else:
        scene_description = "It's quiet around you, with no people or vehicles in sight."

    if light_count:
        scene_description += " You're near an intersection with traffic lights."

    if handbag_count:
        scene_description += " Someone nearby is carrying a bag."

    # Format warning message
    if close_warnings:
        warning_count = len(close_warnings)
        warning_plural = "warnings" if warning_count > 1 else "warning"
        warnings_str = f"{warning_count} {warning_plural}: " + " ".join(
            warning.strip() + "!" if not warning.endswith("!") else warning for warning in close_warnings
        )
    else:
        warnings_str = ""

    # Extract detected signals
    signal_pattern = re.compile(r"✅ Signal Detected: (\w+)")
    signals = signal_pattern.findall(output)

    if "STOP" in signals:
        signal_message = "The walk sign is off. Wait for a moment."
    elif "WALK" in signals:
        signal_message = "The walk sign is on. You can proceed."
    else:
        signal_message = "No traffic signal detected."

    # Combine all parts into a final response
    final_output = warnings_str if warnings_str else ""
    final_output += f" {scene_description}" if scene_description else ""
    final_output += f" {signal_message}" if signal_message else ""

    return final_output

if __name__ == "__main__":
    # Read YOLO model output from stdin
    input_text = sys.stdin.read()
    parsed_result = parse_output(input_text)
    print(parsed_result)
