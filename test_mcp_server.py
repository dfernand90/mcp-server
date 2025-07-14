"""
Basic tests for MCP Server
"""

import pytest
import asyncio
import json
from main import MCPServer, MCPRequest

class TestMCPServer:
    """Test cases for MCP Server"""
    
    @pytest.fixture
    def server(self):
        """Create a server instance for testing"""
        return MCPServer()
    
    @pytest.mark.asyncio
    async def test_initialize(self, server):
        """Test server initialization"""
        request = MCPRequest(method="initialize", params={}, id="test-1")
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert response.result["protocolVersion"] == "2024-11-05"
        assert "capabilities" in response.result
        assert "serverInfo" in response.result
    
    @pytest.mark.asyncio
    async def test_tools_list(self, server):
        """Test tools list endpoint"""
        request = MCPRequest(method="tools/list", params={}, id="test-2")
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert "tools" in response.result
        assert len(response.result["tools"]) > 0
    
    @pytest.mark.asyncio
    async def test_echo_tool(self, server):
        """Test echo tool"""
        request = MCPRequest(
            method="tools/call",
            params={"name": "echo", "arguments": {"message": "Hello World"}},
            id="test-3"
        )
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert "content" in response.result
        assert len(response.result["content"]) > 0
        assert "Hello World" in response.result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_get_time_tool(self, server):
        """Test get_time tool"""
        request = MCPRequest(
            method="tools/call",
            params={"name": "get_time", "arguments": {}},
            id="test-4"
        )
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert "content" in response.result
        assert "Current server time" in response.result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_placeholder_tool(self, server):
        """Test placeholder tool"""
        request = MCPRequest(
            method="tools/call",
            params={"name": "placeholder_tool", "arguments": {"input": "test input"}},
            id="test-5"
        )
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert "content" in response.result
        assert "test input" in response.result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_nonexistent_tool(self, server):
        """Test calling a non-existent tool"""
        request = MCPRequest(
            method="tools/call",
            params={"name": "nonexistent", "arguments": {}},
            id="test-6"
        )
        response = await server.handle_request(request)
        
        assert response.result is None
        assert response.error is not None
        assert response.error["code"] == -32602
    
    @pytest.mark.asyncio
    async def test_ping(self, server):
        """Test ping endpoint"""
        request = MCPRequest(method="ping", params={}, id="test-7")
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert response.result["pong"] is True
    
    @pytest.mark.asyncio
    async def test_unknown_method(self, server):
        """Test unknown method"""
        request = MCPRequest(method="unknown_method", params={}, id="test-8")
        response = await server.handle_request(request)
        
        assert response.result is None
        assert response.error is not None
        assert response.error["code"] == -32601

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
