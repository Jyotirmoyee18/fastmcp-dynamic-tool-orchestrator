# System Architecture & Technical Documentation

## 1. High-Level Overview

This system decouples **tool execution** from **LLM orchestration** using the Model Context Protocol (MCP). Instead of hardcoding Python functions directly inside the agent script, tools live in an isolated **FastMCP Server** and are dynamically discovered and invoked by an **MCP Client Agent** over standard input/output (`stdio`).

```
+-------------------------------------------------------------------+
|                        Host Process (agent.py)                    |
|                                                                   |
|  +-----------------------+       +-----------------------------+  |
|  |   LangChain Agent     | <---> |  langchain-mcp-adapters     |  |
|  |  (ChatOllama / LLM)   |       |  (Schema & Tool Converter)  |  |
|  +-----------------------+       +--------------+--------------+  |
|                                                 |                 |
|                                  +--------------v--------------+  |
|                                  |     MCP ClientSession       |  |
|                                  +--------------+--------------+  |
+-------------------------------------------------|-----------------+
                                                  | JSON-RPC 2.0
                                                  | over STDIO Pipes
+-------------------------------------------------|-----------------+
|                    Subprocess (mcp_server.py)   |                 |
|                                  +--------------v--------------+  |
|                                  |       FastMCP Server        |  |
|                                  +--------------+--------------+  |
|                                                 |                 |
|                          +----------------------+--------------+  |
|                          |                                     |  |
|                 +--------v--------+                   +--------v--------+
|                 |  current_time() |                   |calculate_metrics|
|                 +-----------------+                   +-----------------+
+-------------------------------------------------------------------+
```
## 2. Sequence Flow


```

User            agent.py (Client)         FastMCP (Server)           LLM (Ollama)
 |                     |                         |                        |
 |-- Run Script ------>|                         |                        |
 |                     |-- Spawn Subprocess ---->|                        |
 |                     |-- initialize() -------->|                        |
 |                     |<-- Capabilities --------|                        |
 |                     |-- tools/list ---------->|                        |
 |                     |<-- Tool Schemas --------|                        |
 |                     |                         |                        |
 |                     |-- Prompt + Schemas ----------------------------->|
 |                     |<-- tool_calls (name, args) ----------------------|
 |                     |                         |                        |
 |                     |-- tools/call (args) --->|                        |
 |                     |                         |-- Execute Python Fn    |
 |                     |<-- Tool Result ---------|                        |
 |                     |                         |                        |
 |                     |-- Prompt + Tool Result ------------------------->|
 |                     |<-- Final Response -------------------------------|
 |<-- Print Output ----|                         |                        |
 ```