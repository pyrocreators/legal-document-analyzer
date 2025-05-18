from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import json
import aiohttp
import uuid


class MCPAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)
        self.mcp_url = "http://localhost:4001"
        self._tools = None

    async def _rpc_call(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.mcp_url, json=payload) as response:
                return await response.json()

    async def load_tools(self):
        if self._tools is None:
            response = await self._rpc_call("listTools")
            self._tools = response.get("result", [])

    async def execute_tool(self, tool_name, args):
        response = await self._rpc_call("callTool", {"tool": tool_name, "args": args})
        return response.get("result")

    async def process_prompt(self, prompt):
        await self.load_tools()

        # First LLM call
        messages = [
            SystemMessage(content="You are a document analysis assistant that can call tools via MCP."),
            HumanMessage(content=prompt)
        ]

        if self._tools:
            response = await self.llm.agenerate([messages])
            message = response.generations[0][0].message

            if hasattr(message, "function_call"):
                tool_name = message.function_call["name"]
                tool_args = json.loads(message.function_call["arguments"])

                # Execute tool
                tool_result = await self.execute_tool(tool_name, tool_args)

                # Second LLM call with tool result
                follow_up_messages = messages + [
                    message,
                    {
                        "role": "function",
                        "name": tool_name,
                        "content": json.dumps(tool_result)
                    }
                ]
                follow_up = await self.llm.agenerate([follow_up_messages])
                return follow_up.generations[0][0].message.content

            return message.content
        else:
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].message.content


# Initialize the agent
agent = MCPAgent()