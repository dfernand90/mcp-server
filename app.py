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

from main import tool_video_maker,tool_brochure_maker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Initialize FastAPI app
app = FastAPI(
    title="tilbud_oppsumering",
    description="opportunity summarizer",
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fast api is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "video": "/video (POST)",
            "brochure": "/brochure (POST)",
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Azure"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
# delete this

@app.post("/video")
async def handle_video_request(request: Request):
    """Handle MCP requests via HTTP POST"""
    try:
        body = await request.json()
        project_name = body.get("project")
        underlag = body.get("underlag")
        kg = body.get("kg") # konkuransegrunlag
        logger.info("Received Video request for project:\n%s", json.dumps(body, indent=2))
        response = tool_video_maker(project_name,underlag,kg)
        agentname = (
            body.get("params", {})
                .get("clientInfo", {})
                .get("agentName", None)
        )
        if response.get("id") is not str and agentname == "CastellonianMCPPythontest2":
            logger.warning("Response ID is not a string, converting to string.")
            response["id"]= str(response.get("id"))
        response_data = {
            "jsonrpc": "2.0",
            "id": response.get("id")
        }        
        if response.get("result") is not None:
            response_data["result"] = response.get("result")
        if response.get("error") is not None:
            response_data["error"] = response.get("error") 
        logger.info("Send video response:\n%s", json.dumps(response_data, indent=2))
        return response_data        
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
        logger.error("Send video response:\n%s", json.dumps(error_payload, indent=2))
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": None
            },
            status_code=500
        )

@app.get("/brochure")
async def handle_brochure_request(request: Request):
    """Handle MCP requests via HTTP POST"""
    try:
        body = await request.json()
        project_name = body.get("project")
        underlag = body.get("underlag")
        kg = body.get("kg") # konkuransegrunlag
        logger.info("Received brochure request for project:\n%s", json.dumps(body, indent=2))
        response = tool_brochure_maker(project_name,underlag,kg)
        logger.info("Made brochure request for project:\n%s", json.dumps(body, indent=2))
        agentname = (
            body.get("params", {})
                .get("clientInfo", {})
                .get("agentName", None)
        )
        if response.get("id") is not str and agentname == "CastellonianMCPPythontest2":
            logger.warning("Response ID is not a string, converting to string.")
            response["id"]= str(response.get("id"))
        logger.info("id fixed:\n%s", json.dumps(body, indent=2))
        response_data = {
            "jsonrpc": "2.0",
            "id": response.get("id")
        } 
        logger.info("extracting result fixed:\n%s", json.dumps(body, indent=2))       
        if response.get("result") is not None:
            response_data["result"] = response.get("result")
        if response.get("error") is not None:
            response_data["error"] = response.get("error") 
        logger.info("Send brochure response:\n%s", json.dumps(response_data, indent=2))
        return response_data        
    except Exception as e:
        logger.error(f"Error handling brochure request: {e}")
        error_payload = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": None
        }
        logger.error("Send brochure response:\n%s", json.dumps(error_payload, indent=2))
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": None
            },
            status_code=500
        )
       


# For Azure Web App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
