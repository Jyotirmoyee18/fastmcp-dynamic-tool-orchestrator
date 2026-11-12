from datetime import datetime
from fastmcp import FastMCP

#Initialize the FastMCP server
mcp = FastMCP("My Agent Tools")

@mcp.tool()
def current_time() -> str:
    """Return the current local date and time """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def calculate_metrics(base_value: float, multiplier: float) -> float:
    """Calculate scaled metrics for operational reporting"""
    return base_value * multiplier

#if __name__ ==
if __name__ == "__main__":
    mcp.run()

#Runs over stdio so client processes can seamlessly communicate with it
#mcp.run()