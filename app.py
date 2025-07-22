"""
FastAPI wrapper for MCP Server deployment to Azure Web App
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import PlainTextResponse
from starlette.responses import StreamingResponse
import io

from main import MCPServer, MCPRequest, MCPResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP server instance
mcp_server = MCPServer()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MCP Server is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp (POST)",
            "tools": "/tools",
            "websocket": "/ws"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Azure"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/tools")
async def get_tools():
    """Get available tools"""
    request = MCPRequest(method="tools/list", params={})
    response = await mcp_server.handle_request(request)
    
    if response.error:
        raise HTTPException(status_code=400, detail=response.error)
    
    return response.result

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP requests via HTTP POST"""
    try:
        body = await request.json()
        
        mcp_request = MCPRequest(
            method=body.get("method"),
            params=body.get("params", {}),
            id=body.get("id")
        )
        logger.info("Received MCP request:\n%s", json.dumps(body, indent=2))
        response = await mcp_server.handle_request(mcp_request)
        if mcp_request.id is None:
            # Notification: do not respond with a full JSON-RPC response
            logger.info("Received notification (no response will be sent).")
            return None

        response_data = {
            "jsonrpc": "2.0",
            "id": response.id
        }
        
        if response.result is not None:
            response_data["result"] = response.result
        if response.error is not None:
            response_data["error"] = response.error        
        def stream_response():
            sse_message = f"event: message\ndata: {json.dumps(response_data)}\n\n"
            logger.info("Streaming response:\n%s", sse_message)
            yield sse_message

        return StreamingResponse(stream_response(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        error_payload = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": None
        }
        def error_stream():
            sse_message = f"event: message\ndata: {json.dumps(error_payload)}\n\n"
            logger.error("Streaming error response:\n%s", sse_message)
            yield sse_message

        return StreamingResponse(error_stream(), media_type="text/event-stream", status_code=200)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP communication"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                request_data = json.loads(data)
                
                mcp_request = MCPRequest(
                    method=request_data.get("method"),
                    params=request_data.get("params", {}),
                    id=request_data.get("id")
                )
                
                response = await mcp_server.handle_request(mcp_request)
                
                response_data = {
                    "jsonrpc": "2.0",
                    "id": str(response.id)
                }
                
                if response.result is not None:
                    response_data["result"] = response.result
                if response.error is not None:
                    response_data["error"] = response.error
                
                await websocket.send_text(json.dumps(response_data))
                
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }
                await websocket.send_text(json.dumps(error_response))
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.post("/tools/call")
async def call_tool(request: Request):
    """Call a specific tool"""
    try:
        body = await request.json()
        tool_name = body.get("name")
        arguments = body.get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")
        
        mcp_request = MCPRequest(
            method="tools/call",
            params={"name": tool_name, "arguments": arguments}
        )
        
        response = await mcp_server.handle_request(mcp_request)
        
        if response.error:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.result
        
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# For Azure Web App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
