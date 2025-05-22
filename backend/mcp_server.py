import logging
from jsonrpcserver import serve, method, Success, Error
import wikipedia

logging.basicConfig(level=logging.INFO)

@method
def listTools():
    logging.info("→ listTools called")
    return Success([{
        "name": "search_wikipedia",
        "description": "Search Wikipedia and return the top-k page titles, snippets, and URLs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k":  {"type": "integer", "default": 3}
            },
            "required": ["query"]
        }
    }])

@method
def callTool(tool: str, args: dict):
    logging.info(f"→ callTool called with tool={tool!r}, args={args!r}")
    if tool != "search_wikipedia":
        # MUST use (code:int, message:str)
        return Error(1, f"Unsupported tool {tool!r}")
    # safe to proceed
    q = args.get("query", "")
    k = int(args.get("top_k", 3))
    try:
        titles = wikipedia.search(q, results=k)
    except Exception as e:
        logging.exception("Wikipedia search failed")
        return Error(2, f"Search failed: {e}")
    payload = []
    for title in titles:
        try:
            summary = wikipedia.summary(title, sentences=2, auto_suggest=False)
            page    = wikipedia.page(title, auto_suggest=False)
            payload.append({
                "title":   page.title,
                "summary": summary,
                "url":     page.url
            })
        except Exception as e:
            logging.exception(f"Failed to load page {title}")
            payload.append({"title": title, "error": str(e)})
    logging.info(f"← callTool returning Success(payload of length {len(payload)})")
    logging.debug(f"Payload: {payload}")
    return Success(payload)

print("Wikipedia MCP server listening on http://localhost:4001")
serve(port=4001)