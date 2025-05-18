import os
import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

VECTOR_DIR = "vectorstore"
os.makedirs(VECTOR_DIR, exist_ok=True)

def read_pdf(file_path):
    pdf_document = fitz.open(file_path)
    text = ""
    for page in pdf_document:
        text += page.get_text() + '\n'
    pdf_document.close()
    return text

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(text)

def get_vector_store(chunks, store_path):
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_texts(chunks, embeddings)
    vectordb.save_local(store_path)
    return vectordb

def load_vector_store(store_path):
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(store_path, embeddings, allow_dangerous_deserialization=True)

def get_top_chunks(prompt, vectordb, k=4):
    return vectordb.similarity_search(prompt, k=k)

def get_openai_response(prompt: str, system_context: str = None):
    try:
        chat = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.9

        )

        messages = []

        if system_context:
            messages.append(SystemMessage(content=system_context))

        messages.append(HumanMessage(content=prompt))

        response = chat.invoke(messages)

        return response.content

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def process_pdf_and_respond(pdf_path):
    text = read_pdf(pdf_path)

    chunks = chunk_text(text)

    file_id = os.path.splitext(os.path.basename(pdf_path))[0]
    store_path = os.path.join(VECTOR_DIR, file_id)
    vectordb = get_vector_store(chunks, store_path)

    hardcoded_question = "Summarize the content of this document."

    relevant_chunks = get_top_chunks(hardcoded_question, vectordb)
    context = "\n\n".join(doc.page_content for doc in relevant_chunks)

    system_context = "You are a legal assistant. Use only the provided context to answer."
    full_prompt = f"Context:\n{context}\n\nQuestion: {hardcoded_question}"

    return get_openai_response(full_prompt, system_context)
