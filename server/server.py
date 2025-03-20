import asyncio
import shutil
import subprocess
import uvicorn
import io
import sys
import os
import contextlib  # redirect stdout
import requests
import base64
import cv2 ##remov elater


from typing import Optional
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from ultralytics import YOLO

# For importing custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dino.process_dino import process_image
from dino.output_parser import parse_output


IMG_DIR = Path("client_images")
IMG_DIR.mkdir(exist_ok=True)



model = YOLO("../runs/detect/train17/weights/best.pt")
app = FastAPI()
lock = asyncio.Lock()   # Async lock to restrict concurrent access to model


@app.get("/")
async def dirp_route():
    return {"message": "Yup, the server's running"}

async def run_prediction(image_path, model):
    """Function to run YOLO in a separate process"""

    # run YOLO and DINO
    async with lock:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):  # Redirect stdout to buffer
            # model(image_path)
            process_image(image_path, model)

            # Store output
            model_output = buffer.getvalue()

    
    # print(f"Captured Output: {model_output}")

    output = parse_output(model_output)

    return output, model_output

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_FOLDER = "uploads_test"

    # Ensure the upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Define the file path
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

@app.post("/detect/")
async def detect(request: Request, file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png"]:
        return JSONResponse(content={"error": "Only JPG and PNG images are allowed"}, status_code=400)

    file_content = await file.read()
    result_image = base64.b64encode(file_content).decode("utf-8")

    UPLOAD_FOLDER = "upload"
    # Ensure the upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)


    result, raw_result = await run_prediction(os.path.abspath(file_path), model)

    Path.unlink(file_path)

    return {"filename": result_image, "result": result, "raw_result": raw_result}

# Define a callback to print host and port when the server starts
def on_starting_callback(server):
    # Get assigned host and port
    host, port = server.sockets[0].getsockname()
    print(f"Server is running on http://{host}:{port}")


if __name__ == "__main__":


    uvicorn.run(app, host=host_ip, port=0, on_starting=[on_starting_callback])



'''
Start running with:
    uvicorn server:app --host 0.0.0.0 --port 8001 
    uvicorn server:app --host 10.19.112.166 --port 8001 

    uvicorn server:app --host $(python3 -c "import socket; print([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith('127.') and not ip.startswith('10.')][0])") --port $(python3 -c "import socket; s = socket.socket(); s.bind(('0.0.0.0', 0)); print(s.getsockname()[1]); s.close()")


    --reload → Enables auto-restart when you make code changes (useful for development).

'''

'''
curl http://localhost:8001/

curl -X POST \
  'http://localhost:8001/detect/' \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_images/intersection-9.png"

curl -X 'POST' 'http://169.254.56.220:51558/upload/' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@test_images/intersection-9.png'

curl -X POST \
  'http://169.254.54.189:8001/detect/' \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_images/intersection-9.png"


uvicorn server:app --reload --host $(python3 -c "import socket; print([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith('127.') and not ip.startswith('10.')][0])") --port $(python3 -c "import socket; s = socket.socket(); s.bind(('0.0.0.0', 0)); print(s.getsockname()[1]); s.close()")

uvicorn server:app --reload --host $(python3 -c "import socket; ips = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if ip not in ('127.0.0.1', '0.0.0.0')]; local_ips = [ip for ip in ips if not (ip.startswith('10.') or ip.startswith('172.') or ip.startswith('192.168.'))]; print(local_ips[0] if local_ips else ips[0])") --port $(python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', 0)); print(s.getsockname()[1]); s.close()")

'''

