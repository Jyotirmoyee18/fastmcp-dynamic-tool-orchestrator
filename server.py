from mcp.server.fastmcp import FastMCP

#create an MCP server
mcp = FastMCP("MCP-RAG-app",
              host="127.0.01",
              port=8080,
              timeout=30)