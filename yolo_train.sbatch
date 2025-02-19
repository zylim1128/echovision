#!/bin/bash
#SBATCH --job-name=yolo_train
#SBATCH --output=yolo_train_%j.log   # Log file (%j expands to job ID)
#SBATCH --error=yolo_train_%j.err    # Error file
#SBATCH --time=24:00:00              # Time limit
#SBATCH --partition=gpu-rtx6k        # GPU partition
#SBATCH --account=cse                # Your account
#SBATCH --gres=gpu:1                 # Number of GPUs
#SBATCH --cpus-per-task=8            # CPU cores
#SBATCH --mem=20G                    # Memory

# Load necessary modules if required (adjust as needed)
module load anaconda3
source activate venv  # Activate your environment if needed

# Run your YOLO training
yolo train model=yolo11n.pt data=yolo11n/datasets/merged_data.yaml epochs=50 imgsz=640

