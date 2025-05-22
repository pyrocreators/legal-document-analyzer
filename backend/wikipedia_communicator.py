import json, openai
from mcp_client import MCPClient

WIKI_SPECS = []
OPENAI_FUNCTIONS = []

wiki_mcp = MCPClient("http://localhost:4001")

def to_openai_functions(toolspecs):
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"]
        }
        for t in toolspecs
    ]

async def init_tools():
    global WIKI_SPECS, OPENAI_FUNCTIONS
    WIKI_SPECS = await wiki_mcp.list_tools()
    OPENAI_FUNCTIONS = to_openai_functions(WIKI_SPECS)


async def chat_with_tools_all(message):
    """Handles questions related strictly to legal terms using available tools via MCP."""
    LEGAL_FILTER_PROMPT = """You are a helpful assistant specialized in legal documents. 
    You only answer questions related to legal terms or legal definitions.
    Ignore any question that is not about a legal term or concept. 
    Do NOT offer generic help or say things like 'If you have a specific question...' or similar.
    Only respond with accurate, concise legal-related answers."""

    chat = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": LEGAL_FILTER_PROMPT},
            {"role": "user", "content": message}
        ],
        functions=OPENAI_FUNCTIONS,
        function_call="auto"
    )
    msg = chat.choices[0].message

    if not msg.content and not msg.function_call:
        return "This assistant only responds to questions about legal terms."

    if msg.function_call:
        fn_name = msg.function_call.name
        fn_args = json.loads(msg.function_call.arguments)

        client = wiki_mcp
        result = await client.call_tool(fn_name, fn_args)
        follow = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Only return the final legal explanation or definition. Do not offer further help or ask for more questions."},
                {"role": "assistant", "content": None, "function_call": msg.function_call},
                {"role": "function", "name": fn_name, "content": json.dumps(result)}
            ]
        )
        return follow.choices[0].message.content

    return msg.content.strip()
