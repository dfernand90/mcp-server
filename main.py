"""
MCP Server - Placeholder Implementation
A basic Model Context Protocol server that can be extended with custom functionality.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json
import sys
import os
from datetime import datetime
import base64
import mimetypes
from pathlib import Path
from model import castellonian

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("main")

@dataclass
class MCPRequest:
    """Represents an MCP request"""
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

@dataclass
class MCPResponse:
    """Represents an MCP response"""
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class MCPServer:
    """
    Placeholder MCP Server implementation
    
    This server provides a basic structure for implementing MCP functionality.
    You can extend this class to add your own tools and capabilities.
    """
    
    def __init__(self):
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        self.uploaded_files = {}  # Store uploaded PDF files
        self._setup_default_tools()
        self._setup_default_resources()
    
    def _setup_default_tools(self):
        """Setup default placeholder tools"""
        self.tools = {
            "echo": {
                "name": "echo",
                "description": "Echo back the input message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            },
            "get_time": {
                "name": "get_time",
                "description": "Get current server time",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "add_numbers": {
                "name": "add_numbers",
                "description": "Add two floating point numbers together",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "First number to add"
                        },
                        "b": {
                            "type": "number",
                            "description": "Second number to add"
                        }
                    },
                    "required": ["a", "b"]
                }
            },
            "multiply_numbers": {
                "name": "multiply_numbers",
                "description": "Multiply two floating point numbers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "First number to multiply"
                        },
                        "b": {
                            "type": "number",
                            "description": "Second number to multiply"
                        }
                    },
                    "required": ["a", "b"]
                }
            },
            "upload_pdf": {
                "name": "upload_pdf",
                "description": "Upload a PDF file for processing (validates PDF format)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the PDF file"
                        },
                        "content": {
                            "type": "string",
                            "description": "Base64 encoded PDF content"
                        }
                    },
                    "required": ["filename", "content"]
                }
            },
            "castellonian_tool": {
                "name": "castellonian_tool",
                "description": "use this function to calculate the castellonian value of a floating point number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "floating point number to calculate the castellonian value of"
                        }
                    },
                    "required": ["a"]
                }
            },
            "placeholder_tool": {
                "name": "placeholder_tool",
                "description": "A placeholder tool for your custom implementation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input parameter for your custom tool"
                        }
                    },
                    "required": ["input"]
                }
            }
        }
    
    def _setup_default_resources(self):
        """Setup default resources including PDF files"""
        self.resources = {
            "fixed_pdf": {
                "uri": "file://documents/sample.pdf",
                "name": "Sample PDF Document",
                "description": "A fixed PDF file included with the server",
                "mimeType": "application/pdf"
            },
            "uploaded_pdfs": {
                "uri": "uploaded://pdfs",
                "name": "Uploaded PDF Files",
                "description": "User-uploaded PDF files (validated format)",
                "mimeType": "application/pdf"
            }
        }
    
    def _validate_pdf(self, content: bytes) -> bool:
        """Validate that the content is a valid PDF file"""
        try:
            # Check PDF header
            if content.startswith(b'%PDF-'):
                return True
            return False
        except Exception:
            return False
    
    def _get_fixed_pdf_path(self) -> Path:
        """Get path to the fixed PDF file"""
        # Look for sample.pdf in documents folder relative to server
        current_dir = Path(__file__).parent
        pdf_path = current_dir / "documents" / "sample.pdf"
        return pdf_path
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP requests"""
        if request.id is None:
            # It's a notification — do not respond
            return None
        try:
            logger.info(f"Handling request: {request.method}")
            
            if request.method == "initialize":
                return await self._handle_initialize(request)
            elif request.method == "tools":
                return await self._handle_tools_list(request)
            elif request.method == "tools/list":
                return await self._handle_tools_list(request)
            elif request.method == "tools/call":
                return await self._handle_tools_call(request)
            elif request.method == "resources/list":
                return await self._handle_resources_list(request)
            elif request.method == "resources/read":
                return await self._handle_resources_read(request)
            elif request.method == "prompts/list":
                return await self._handle_prompts_list(request)
            elif request.method == "ping":
                return await self._handle_ping(request)
            else:
                return MCPResponse(
                    error={"code": -32601, "message": f"Method not found: {request.method}"},
                    id=request.id
                )
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return MCPResponse(
                error={"code": -32603, "message": f"Internal error: {str(e)}"},
                id=request.id
            )
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialize request"""
        return MCPResponse(
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                },
                "serverInfo": {
                    "name": "mcp-castellonian-server",
                    "version": "1.0.0"
                }
            },
            id=request.id
        )
    
    async def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools list request"""
        return MCPResponse(
            result={"tools":list(self.tools.values())},
            id=request.id
        )
    
    async def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools call request"""
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if tool_name not in self.tools:
            return MCPResponse(
                error={"code": -32602, "message": f"Tool not found: {tool_name}"},
                id=request.id
            )
        
        # Execute the tool
        result = await self._execute_tool(tool_name, arguments)
        
        return MCPResponse(
            result={"content": [{"type": "text", "text": result}]},
            id=request.id
        )
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool with given arguments"""
        if tool_name == "echo":
            return f"Echo: {arguments.get('message', '')}"
        
        elif tool_name == "get_time":
            return f"Current server time: {datetime.now().isoformat()}"
        
        elif tool_name == "add_numbers":
            try:
                a = float(arguments.get('a', 0))
                b = float(arguments.get('b', 0))
                result = a + b
                return f"Addition result: {a} + {b} = {result}"
            except (ValueError, TypeError) as e:
                return f"Error: Invalid number format - {str(e)}"
        
        elif tool_name == "multiply_numbers":
            try:
                a = float(arguments.get('a', 0))
                b = float(arguments.get('b', 0))
                result = a * b
                return f"Multiplication result: {a} × {b} = {result}"
            except (ValueError, TypeError) as e:
                return f"Error: Invalid number format - {str(e)}"
        
        elif tool_name == "castellonian_tool":
            try:
                a = float(arguments.get('a', 0))
                
                result = castellonian(a)
                return f"the castellonian of {a} is {result}"
            except (ValueError, TypeError) as e:
                return f"Error: Invalid number format - {str(e)}"

        elif tool_name == "upload_pdf":
            try:
                filename = arguments.get('filename', '')
                content_b64 = arguments.get('content', '')
                
                # Validate filename
                if not filename.lower().endswith('.pdf'):
                    return "Error: File must have .pdf extension"
                
                # Decode base64 content
                try:
                    content_bytes = base64.b64decode(content_b64)
                except Exception as e:
                    return f"Error: Invalid base64 content - {str(e)}"
                
                # Validate PDF format
                if not self._validate_pdf(content_bytes):
                    return "Error: File is not a valid PDF format"
                
                # Store the uploaded file
                file_id = f"uploaded_{len(self.uploaded_files) + 1}"
                self.uploaded_files[file_id] = {
                    "filename": filename,
                    "content": content_bytes,
                    "size": len(content_bytes),
                    "uploaded_at": datetime.now().isoformat()
                }
                
                return f"PDF uploaded successfully: {filename} (ID: {file_id}, Size: {len(content_bytes)} bytes)"
                
            except Exception as e:
                return f"Error uploading PDF: {str(e)}"
        
        elif tool_name == "placeholder_tool":
            # TODO: Implement your custom tool logic here
            input_value = arguments.get('input', '')
            return f"Placeholder tool executed with input: {input_value}"
        
        else:
            return f"Tool {tool_name} not implemented"
    
    async def _handle_resources_read(self, request: MCPRequest) -> MCPResponse:
        """Handle resource read request"""
        try:
            uri = request.params.get("uri")
            if not uri:
                return MCPResponse(
                    error={"code": -32602, "message": "Missing required parameter: uri"},
                    id=request.id
                )
            
            if uri == "file://documents/sample.pdf":
                # Read the fixed PDF file
                pdf_path = self._get_fixed_pdf_path()
                if pdf_path.exists():
                    with open(pdf_path, "rb") as f:
                        content = f.read()
                    
                    # Return as base64 encoded content
                    content_b64 = base64.b64encode(content).decode('utf-8')
                    return MCPResponse(
                        result={
                            "contents": [{
                                "uri": uri,
                                "mimeType": "application/pdf",
                                "text": f"PDF file content (base64): {content_b64[:100]}..." if len(content_b64) > 100 else content_b64
                            }]
                        },
                        id=request.id
                    )
                else:
                    return MCPResponse(
                        error={"code": -32602, "message": f"Fixed PDF file not found at: {pdf_path}"},
                        id=request.id
                    )
            
            elif uri.startswith("uploaded://pdfs/"):
                # Handle uploaded PDF files
                file_id = uri.split("/")[-1]
                if file_id in self.uploaded_files:
                    file_info = self.uploaded_files[file_id]
                    content_b64 = base64.b64encode(file_info["content"]).decode('utf-8')
                    
                    return MCPResponse(
                        result={
                            "contents": [{
                                "uri": uri,
                                "mimeType": "application/pdf",
                                "text": f"Uploaded PDF: {file_info['filename']} (Size: {file_info['size']} bytes, Uploaded: {file_info['uploaded_at']})"
                            }]
                        },
                        id=request.id
                    )
                else:
                    return MCPResponse(
                        error={"code": -32602, "message": f"Uploaded file not found: {file_id}"},
                        id=request.id
                    )
            
            else:
                return MCPResponse(
                    error={"code": -32602, "message": f"Resource not found: {uri}"},
                    id=request.id
                )
                
        except Exception as e:
            logger.error(f"Error reading resource: {str(e)}")
            return MCPResponse(
                error={"code": -32603, "message": f"Error reading resource: {str(e)}"},
                id=request.id
            )
    
    async def _handle_resources_list(self, request: MCPRequest) -> MCPResponse:
        """Handle resources list request"""
        # Add uploaded files to resources list
        resources = list(self.resources.values())
        
        # Add uploaded PDF files as individual resources
        for file_id, file_info in self.uploaded_files.items():
            resources.append({
                "uri": f"uploaded://pdfs/{file_id}",
                "name": file_info["filename"],
                "description": f"Uploaded PDF file (Size: {file_info['size']} bytes)",
                "mimeType": "application/pdf"
            })
        
        return MCPResponse(
            result={"resources": resources},
            id=request.id
        )
        """Handle prompts list request"""
        return MCPResponse(
            result={"prompts": list(self.prompts.values())},
            id=request.id
        )
    
    async def _handle_ping(self, request: MCPRequest) -> MCPResponse:
        """Handle ping request"""
        return MCPResponse(
            result={"pong": True},
            id=request.id
        )

class MCPStdioTransport:
    """STDIO transport for MCP server"""
    
    def __init__(self, server: MCPServer):
        self.server = server
    
    async def start(self):
        """Start the STDIO transport"""
        logger.info("Starting MCP server with STDIO transport")
        
        try:
            while True:
                # Read from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                try:
                    # Parse JSON-RPC request
                    request_data = json.loads(line.strip())
                    request = MCPRequest(
                        method=request_data.get("method"),
                        params=request_data.get("params", {}),
                        id=request_data.get("id")
                    )
                    
                    # Handle request
                    response = await self.server.handle_request(request)
                    
                    # Send response
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": response.id
                    }
                    
                    if response.result is not None:
                        response_data["result"] = response.result
                    if response.error is not None:
                        response_data["error"] = response.error
                    
                    print(json.dumps(response_data), flush=True)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        except Exception as e:
            logger.error(f"Server error: {e}")

async def main():
    """Main entry point"""
    server = MCPServer()
    transport = MCPStdioTransport(server)
    await transport.start()

if __name__ == "__main__":
    asyncio.run(main())
