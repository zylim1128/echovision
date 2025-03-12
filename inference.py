import cv2
import os
import argparse
import re

from ultralytics import YOLO

def make_dir(dir_path):
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to create '{dir_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_files_in_dir(dir_path):
  """
  Gets all files under the given directory and returns them as an array of strings.

    Args:
        dir_path: The path to the directory.

    Returns:
        An array of strings, where each string is the absolute path to a file.
        Returns an empty array if the directory does not exist or if it's empty.
  """
  if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
    return []

  return [f for f in dir_path if f.endswith(('.jpg', '.png', '.jpeg'))]
#   file_list = []
#   for root, _, files in os.walk(dir_path):
#     for file in files:
#       file_path = os.path.join(root, file)
#       file_list.append(file_path)
#   return file_list

parser = argparse.ArgumentParser()
parser.add_argument('model_path')
parser.add_argument('-i', '--input_path', default='test_images')
parser.add_argument('-o', '--output_path', default='model_output')

args = parser.parse_args()
model_path, in_path, out_path = args.model_path, args.input_path, args.output_path
image_outputs = os.path.join(out_path, 'images')
label_outputs = os.path.join(out_path, 'labels')

make_dir(out_path)
make_dir(image_outputs)
make_dir(label_outputs)

# Load trained model
model_path = os.path.join(model_path, 'weights', 'best.pt')
model = YOLO(model_path) 

# Run batched inference on a list of images
results = model(get_files_in_dir(in_path))  # return a list of Results objects

# Process results list
for result in results:
    # Regular expression to get the file name without the ".jpg" extension
    pattern = r'([^/]+)(?=\.[^.]+$)'
    image_id = re.search(pattern, result.path).group(1)
    result.save(filename=os.path.join(image_outputs, f'{image_id}.jpg'))
    result.save_txt(txt_file=os.path.join(label_outputs, f'{image_id}.txt'))

