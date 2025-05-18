import logging
from jsonrpcserver import serve, method, Success, Error
from utils import chunk_text, get_vector_store, load_vector_store, get_top_chunks
from typing import Dict, Any
import os

logging.basicConfig(level=logging.INFO)


@method
def listTools():
    logging.info("→ listTools called")
    return Success([{
        "name": "chunk_pdf_text",
        "description": "Splits the input text into smaller chunks.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"}
            },
            "required": ["text"]
        }
    }, {
        "name": "embed_and_store_single_input",
        "description": "Embeds text and stores it in the vector store.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "store_path": {"type": "string"}
            },
            "required": ["text", "store_path"]
        }
    }, {
        "name": "qa_from_store",
        "description": "Retrieves chunks relevant to a question from a stored vector database.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "store_path": {"type": "string"}
            },
            "required": ["question", "store_path"]
        }
    }])


@method
def callTool(tool: str, args: Dict[str, Any]):
    logging.info(f"→ callTool called with tool={tool!r}, args={args!r}")

    try:
        if tool == "chunk_pdf_text":
            text = args["text"]
            chunks = chunk_text(text)
            return Success("\n---\n".join(chunks[:5]))

        elif tool == "embed_and_store_single_input":
            text = args["text"]
            store_path = args["store_path"]
            os.makedirs(os.path.dirname(store_path), exist_ok=True)
            chunks = chunk_text(text)
            get_vector_store(chunks, store_path)
            return Success(f"Successfully embedded and stored vectors at {store_path}.")

        elif tool == "qa_from_store":
            question = args["question"]
            store_path = args["store_path"]
            vectordb = load_vector_store(store_path)
            results = get_top_chunks(question, vectordb)
            return Success("\n".join([doc.page_content for doc in results]))

        else:
            return Error(1, f"Unsupported tool {tool!r}")

    except Exception as e:
        logging.exception(f"Tool {tool} execution failed")
        return Error(2, f"Tool execution failed: {str(e)}")


print("Document Analyzer MCP server listening on http://localhost:4001")
serve(port=4001)