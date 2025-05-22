from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent_utils import process_pdf_and_with_summary, process_pdf_and_with_key_points
from wikipedia_communicator import chat_with_tools_all, init_tools
from fastapi.responses import JSONResponse


load_dotenv()

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/summary/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    response_text = process_pdf_and_with_summary(file_location)
    return response_text

@app.post("/key-points/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    response_text = process_pdf_and_with_key_points(file_location)
    return response_text

@app.get("/legal-terminology/")
async def legal_terminology_helper(question: str):
    response_text = await chat_with_tools_all(question)

    return JSONResponse(content={
        "response": response_text
    })


@app.on_event("startup")
async def startup_event():
    await init_tools()