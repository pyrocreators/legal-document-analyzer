from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from dotenv import load_dotenv
from agent_utils import process_pdf_and_respond_with_agent

load_dotenv()

app = FastAPI()

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    response_text = await process_pdf_and_respond_with_agent(file_location)
    return JSONResponse(content={
        "filename": file.filename,
        "message": "PDF uploaded and processed successfully.",
        "response": response_text
    })