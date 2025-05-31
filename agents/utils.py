from starlette.responses import JSONResponse
from langchain_core.messages import convert_to_messages
from rag_utils.utils import read_pdf
from langsmith import traceable
from agents.executor import supervisor


@traceable
def process_pdf_and_with_summary(pdf_path):
    text = read_pdf(pdf_path)

    plan_prompt = f"""
    You are a legal document analyzer agent. Your task is to process and summarize the legal document provided below. Follow these steps carefully:

    1. Split the document into semantically meaningful chunks using the `chunk_agent`.
    2. Embed the chunks and store them in a vector database using the 'embed_agent'.
    3. Query the vector database using the question below.
    4. Provide a precise, information-rich response based strictly on the document's content.

    ### Question:
    Analyze the document and answer the following:
    - What type of legal document is this (e.g., NDA, employment contract, service agreement)?
    - Is there an expiration date mentioned? If yes, what is it?

    ### Constraints:
    - Do **not** start your response with generic phrases like "This is the summarized document."
    - Respond in the **same language** as the document.
    - Your response should be **brief**, **factual**, and **clearly formatted** using bullet points if helpful.

    ### Document
    {text}
    """

    last_response = None
    for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": plan_prompt
                    }
                ]
            }
    ):
        last_response = pretty_print_messages(chunk, last_message=True)
    return JSONResponse(content={"summary": last_response.content})


@traceable
def process_pdf_and_with_key_points(pdf_path):
    text = read_pdf(pdf_path)

    hardcoded_question = (
        "You are analyzing a legal document. Summarize the key points using the following format:\n"
        "- [Key Point Title]: [Short Description]\n\n"
        "you have to remove the brackets ([]) from the actual key point title"
        "If the document is an NDA or similar, be sure to include:\n"
        "- Confidentiality Obligations\n"
        "- Term and Termination\n"
        "- Permitted Disclosures\n"
        "- Restrictions on Use\n"
        "- Consequences of Breach\n\n"
        "Respond in the same language as the document. Do not add introductory or concluding phrases such as "
        "'Here are the key points summarized from the legal document.' or 'In summary.' Only return the bullet points."
    )

    plan_prompt = f"""
    You are a legal document analyzer agent. Your task is to:

    1. Split the document into semantically meaningful chunks using the `chunk_agent`.
    2. Embed the chunks and store them in a vector database using the 'embed_agent'.
    3. Query the vector database using the question below.
    4. Provide a precise, information-rich response based strictly on the document's content.

    Document (truncated to fit context limits):
    {text}

    Question:
    {hardcoded_question}
    """

    last_response = None
    for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": plan_prompt
                    }
                ]
            }
    ):
        last_response = pretty_print_messages(chunk, last_message=True)
    return JSONResponse(content={"summary": last_response.content})




def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)

def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0:
            return None  # skip root graph updates
        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:\n")
        is_subgraph = True

    result_message = None

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label + "\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]  # keep only the last message

        result_message = messages[-1] if messages else None

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")

    return result_message
