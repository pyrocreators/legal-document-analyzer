from langchain.tools import tool
from utils import chunk_text, get_vector_store, load_vector_store, get_top_chunks

@tool
def chunk_pdf_text(text: str) -> str:
    """Splits the input text into smaller chunks."""
    chunks = chunk_text(text)
    return "\n---\n".join(chunks[:5])  # Return a sample of chunks for brevity

@tool
def embed_and_store_single_input(input: str) -> str:
    """
    Embeds text and stores it in the vector store.
    Input format: <text>::<store_path>
    """
    try:
        text, store_path = input.split("::")
        chunks = chunk_text(text)
        get_vector_store(chunks, store_path)
        return f"Successfully embedded and stored vectors at {store_path}."
    except Exception as e:
        return f"Error: {e}"

@tool
def qa_from_store(input: str) -> str:
    """
    Retrieves chunks relevant to a question from a stored vector database and returns them.
    Input format: <question>::<store_path>
    """
    try:
        question, store_path = input.split("::")
        vectordb = load_vector_store(store_path)
        results = get_top_chunks(question, vectordb)
        return "\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Error: {e}"
