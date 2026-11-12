# FastMCP AI Agent

An AI agent implementation using **FastMCP** to expose local Python tools over the Model Context Protocol (MCP) and **LangChain** (`langchain-mcp-adapters`) to dynamically bind those tools to an LLM.

## Project Structure

```text
.
├── mcp_server.py    # FastMCP server exposing custom tools
├── agent.py         # LangChain MCP client & tool-calling agent loop
├── README.md        # Installation and execution guide
├──main.py
└── DOC.md           # System architecture and protocol documentation


Prerequisites:
Python 3.10+

uv (recommended) or pip

Ollama running locally (default model: qwen3.5:4b), or an API key for another tool-capable LLM provider (OpenAI, Gemini, Anthropic).

Installation
1. Clone or navigate to the project directory:
```
cd fastmcp-dynamic-tool-orchestrator
```

2. Create and activate a virtual environment:

```
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
Using uv:
```
uv add fastmcp langchain langchain-core langchain-ollama langchain-mcp-adapters
```

Or using pip:
```
pip install fastmcp langchain langchain-core langchain-ollama langchain-mcp-adapters
```

4. Prepare the local LLM (if using Ollama):
```
ollama pull qwen3.5:4b
```

Usage
1. Test Tools via MCP Inspector (Development Mode)
Before running the full agent, verify your server and test tools interactively in the browser:
```
fastmcp dev mcp_server.py
```
Open the local URL printed in the terminal (e.g., http://127.0.0.1:6274).

Navigate to the Tools tab, select a tool (current_time or calculate_metrics), input test arguments, and click Run Tool.

Press Ctrl + C in the terminal to stop the inspector when finished.

2. Run the Autonomous MCP Agent
Execute the client script, which automatically spawns mcp_server.py as a background subprocess and runs the tool-calling loop:
```
python agent.py
```
3. Optional: Integrate with Desktop MCP Clients
To register your FastMCP server with desktop clients like Claude Desktop:
```
fastmcp install mcp_server.py
```
2. Core Components
A. FastMCP Server (mcp_server.py)
Role: Tool provider and schema generator.

Mechanism: Uses the @mcp.tool() decorator to inspect Python type annotations (float, str) and docstrings. FastMCP automatically compiles these into MCP-compliant JSON Schemas.

Transport: Runs via mcp.run(), defaulting to stdio transport. It listens for JSON-RPC requests on stdin and writes responses to stdout.

B. MCP Client & Transport Layer (agent.py)
Subprocess Lifecycle (stdio_client): When agent.py starts, StdioServerParameters launches python mcp_server.py as a child process and establishes asynchronous read/write byte streams.

Protocol Handshake (ClientSession): await session.initialize() negotiates protocol versions and capabilities between the client and the FastMCP server.

C. Adapter Layer (langchain-mcp-adapters)
Dynamic Discovery (load_mcp_tools): Queries the server's tools/list endpoint and converts each MCP tool definition into a LangChain StructuredTool.

Execution Bridge: When the LLM emits a tool call, the adapter translates the arguments into a JSON-RPC tools/call payload, awaits execution on the server, and wraps the output into a LangChain ToolMessage.

D. Reasoning & Orchestration Layer (ChatOllama)
Tool Binding: llm.bind_tools(tools) injects the converted JSON schemas into the LLM's system context.

Execution Loop:

Prompt Ingestion: Receives HumanMessage from the user.

Intent & Parameter Extraction: The LLM evaluates whether external tools are needed and outputs structured tool_calls (tool name + JSON arguments).

Tool Invocation: The client loop matches each requested tool name, invokes it asynchronously across the stdio pipe, and appends the returned ToolMessage to the conversation history.

Synthesis: The updated message history is passed back to the LLM to generate the final natural-language answer.
Extensibility Guidelines
Adding New Tools: Define standard typed Python functions in mcp_server.py decorated with @mcp.tool(). Always include clear docstrings, as the LLM relies on them to decide when and how to invoke the tool.

Switching Transport to HTTP/SSE: For remote or containerized deployments where the server runs independently of the client, change mcp.run() to mcp.run(transport="sse") (or "streamable-http") and update agent.py to use the corresponding HTTP/SSE MCP client transport.

Swapping LLM Providers: Replace ChatOllama in agent.py with any LangChain chat model supporting .bind_tools() (e.g., ChatOpenAI, ChatGoogleGenerativeAI, or ChatAnthropic) without modifying mcp_server.py.