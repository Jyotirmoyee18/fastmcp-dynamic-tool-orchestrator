import asyncio
from langchain_mcp_adapters.tools import load_mcp_tools 
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client 

async def main():
    #Configure the server subprocess connection
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            #Initiate the session
            await session.initialize()

            #Automatically load tools exposed by the FirstMCP
            tools = await load_mcp_tools(session)
            print(f"Loaded tools: {[t.name for t in tools]}")

            #Bind tools to a tool-capable LLM 
            llm = ChatOllama(model="qwen3.5:4b", temperature=0)
            llm_with_tools = llm.bind_tools(tools)

            #Run a prompt that requires calling MCP tools
            query = "What is the current time and what is 150 multiplied by by 4.5 using our metrics tool?"
            print(f"\nUser Query: {query}\n")

            messages = [HumanMessage(Content=query)]
            response = await llm_with_tools.ainvoke(messages)

            #Handle tool calls if required 
            messages.append(response)
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    selected_tool = next(t for t in tools if t.name == tool_call["name"])
                    tool_result = await selected_tool.ainvoke(tool_call["args"])
                    messages.append(tool_result)

                    # Get final response from LLM incorporating tool outputs
                final_response = await llm_with_tools.ainvoke(messages)
                print(f"Agent Response:\n{final_response.content}")
            else:
                print(f"Agent Response:\n{response.content}")

if __name__ == "__main__":
    asyncio.run(main())