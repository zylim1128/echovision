import asyncio
import shutil
import subprocess
import uvicorn
import io
import sys
import os
import contextlib  # redirect stdout
# import time


from typing import Optional
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO

# For importing custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dino.process_dino import process_image
from output_parser import parse_output


IMG_DIR = Path("client_images")
IMG_DIR.mkdir(exist_ok=True)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     app.state.model = YOLO("yolov8n.pt")  # Load once at startup
#     yield
# app = FastAPI(lifespan=lifespan)

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
            print("\nLOLLLL")

            # Store output
            model_output = buffer.getvalue()

    
    print(f"Captured Output: {model_output}")

    output = parse_output(model_output)
    # try:
    #     process = subprocess.Popen(
    #                 ["python3",  "../output_parser.py"],
    #                 stdin=subprocess.PIPE,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE,
    #                 text=True,
    #             )
    #     output, error = process.communicate(input=model_output)
        
    #     if process.returncode != 0:
    #         raise RuntimeError(f"Subprocess failed with error: {error}")

    #     print("Subprocess Output:", output)

    #     return output, model_output
    # except FileNotFoundError:
    #     print("Error: process_results.py not found!")
    # except PermissionError:
    #     print("Error: Permission denied while executing the script!")
    # except RuntimeError as e:
    #     print(f"Error: {e}")
    # except Exception as e:
    #     print(f"Unexpected error: {e}")

    return output

@app.post("/detect/")
async def detect(file: UploadFile = File(...), ts: Optional[datetime] = None):
    if file.content_type not in ["image/jpeg", "image/png"]:
        return JSONResponse(content={"error": "Only JPG and PNG images are allowed"}, status_code=400)

    # Save the uploaded file
    file_path = IMG_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result, raw_result = await run_prediction(file_path, model)

    # return {"filename": file.filename, "result": result}
    return {"filename": file.filename, "result": result, "raw_result": raw_result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

#  lightning-fast ASGI server designed for running async Python web applications
        # ASGI server
        #     An ASGI (Asynchronous Server Gateway Interface) server is a specification that 
        #     enables asynchronous communication between web applications and web servers in Python. 
        #     It is designed as an evolution of WSGI (Web Server Gateway Interface) to support 
        #     asynchronous frameworks like FastAPI, Starlette, and Django with Django Channels.
    # ✅ Asynchronous: Uses asyncio for high-performance, non-blocking execution.
    # ✅ Lightweight & Fast: Built on uvloop and httptools for low-latency processing.
    # ✅ Production-Ready: Can handle WebSockets, HTTP/2, and background tasks efficiently.
    # ✅ Hot Reloading: With --reload, it automatically restarts on code changes (useful in development).

'''
Start running with:
    uvicorn server:app --host 0.0.0.0 --port 8001 --log-level debug

In production:
    --workers 4

For developement:
    --reload → Enables auto-restart when you make code changes (useful for development).

'''

'''
curl http://localhost:8001/

curl -X POST \
  'http://localhost:8001/detect/' \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_images/intersection-9.png"
'''

# server:app → server.py file and app instance inside it.