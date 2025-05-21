from starlette.responses import JSONResponse
from langchain_core.messages import convert_to_messages
from utils import read_pdf
from langsmith import traceable
from agent_executor import supervisor


@traceable
def process_pdf_and_with_summary(pdf_path):
    text = read_pdf(pdf_path)

    hardcoded_question = (
        "Analyze the document and provide a brief summary that includes only:\n"
        "1. The type of document (e.g., NDA, employment contract, service agreement).\n"
        "2. The expiration date, if mentioned.\n"
        "Respond in the same language as the document."
    )

    plan_prompt = f"""
You are a legal document analyzer agent. Please:
1. chunk pdf document using chunk_agent
2. Embed and store this text in a vector store.
3. querying the stored vector database.
4. Then, answer the question based on the stored data.


Question: {hardcoded_question}

Here is the document content:
{text[:4000]}  # truncated for token limit
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
            "If the document is an NDA or similar, be sure to include:\n"
            "- Confidentiality Obligations\n"
            "- Term and Termination\n"
            "- Permitted Disclosures\n"
            "- Restrictions on Use\n"
            "- Consequences of Breach\n\n"
            "Respond in the same language as the document. Avoid generic statements like 'The task has been completed.'"
    )

    plan_prompt = f"""
    You are a legal document analyzer agent. Your task is to:

    1. Use chunk_agent to split the document.
    2. Store the chunks in a vector store.
    3. Query the vector store to answer the user's question.
    4. Respond in a structured bullet-point format based only on the document content.

    Document (truncated to fit context limits):
    {text[:4000]}

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
