#!/usr/bin/env python3
"""
Test script for MCP server
"""

import asyncio
import json
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server with the JAMA article URL"""
    
    # Test URL
    test_url = "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2837260?resultClick=1"
    
    print("Testing MCP Server...")
    print(f"URL: {test_url}")
    print("-" * 50)
    
    try:
        # Connect to the MCP server
        async with stdio_client() as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # List available tools
                tools = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools.tools]}")
                
                # Call the generate_graphical_abstract tool
                result = await session.call_tool("generate_graphical_abstract", {"url": test_url})
                
                print("RESULT:")
                print(json.dumps(result, indent=2))
                print("-" * 50)
                
                if "HATA" in result.content[0].text:
                    print("❌ Test failed - Error occurred")
                    return False
                else:
                    print("✅ Test successful - Tool executed successfully")
                    return True
                    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
