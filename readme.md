# MCP Server - Placeholder Implementation

A Model Context Protocol (MCP) server implementation in Python, ready for deployment to Azure Web App via GitHub Actions.

## Features

- **MCP Protocol Support**: Implements the Model Context Protocol specification
- **Placeholder Tools**: Includes sample tools that you can replace with your own implementations
- **Azure Web App Ready**: Configured for deployment to Azure Web App
- **GitHub Actions CI/CD**: Automated testing and deployment
- **Multiple Interfaces**: 
  - STDIO for local development
  - HTTP REST API for web access
  - WebSocket for real-time communication
- **Docker Support**: Containerized deployment option
- **Health Checks**: Built-in health monitoring for Azure

## Project Structure

```
mcp-server/
├── main.py                 # Core MCP server implementation
├── app.py                  # FastAPI wrapper for web deployment
├── requirements.txt        # Python dependencies
├── startup.sh             # Azure startup script
├── web.config             # Azure Web App configuration
├── Dockerfile             # Container configuration
├── test_mcp_server.py     # Unit tests
├── .github/workflows/     # GitHub Actions CI/CD
└── README.md              # This file
```

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server locally**
   ```bash
   # STDIO mode (for MCP clients)
   python main.py
   
   # Web mode (for HTTP access)
   python app.py
   ```

4. **Test the server**
   ```bash
   python -m pytest test_mcp_server.py -v
   ```

### Azure Deployment

1. **Create Azure Web App**
   - Go to Azure Portal
   - Create a new Web App with Python runtime
   - Note the app name and get the publish profile

2. **Configure GitHub Secrets**
   - `AZURE_WEBAPP_NAME`: Your Azure Web App name
   - `AZURE_WEBAPP_PUBLISH_PROFILE`: Download from Azure Portal

3. **Deploy**
   - Push to main branch
   - GitHub Actions will automatically build and deploy

## Available Tools (Placeholders)

The server includes three placeholder tools that you can replace with your own implementations:

### 1. Echo Tool
- **Name**: `echo`
- **Description**: Echo back the input message
- **Parameters**: `message` (string)

### 2. Get Time Tool
- **Name**: `get_time`
- **Description**: Get current server time
- **Parameters**: None

### 3. Placeholder Tool
- **Name**: `placeholder_tool`
- **Description**: A placeholder for your custom implementation
- **Parameters**: `input` (string)

## API Endpoints

When deployed as a web app, the server provides these endpoints:

- `GET /` - Server information
- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /mcp` - MCP protocol requests
- `POST /tools/call` - Direct tool execution
- `WebSocket /ws` - Real-time MCP communication

## Customization

### Adding Your Own Tools

1. **Update `_setup_default_tools()` in `main.py`**:
   ```python
   def _setup_default_tools(self):
       self.tools = {
           "your_tool": {
               "name": "your_tool",
               "description": "Description of your tool",
               "inputSchema": {
                   "type": "object",
                   "properties": {
                       "param1": {
                           "type": "string",
                           "description": "Parameter description"
                       }
                   },
                   "required": ["param1"]
               }
           }
       }
   ```

2. **Implement tool logic in `_execute_tool()` method**:
   ```python
   async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
       if tool_name == "your_tool":
           # Your custom implementation here
           param1 = arguments.get('param1')
           result = your_custom_logic(param1)
           return f"Result: {result}"
   ```

### Adding Resources

Resources are static or dynamic content that tools can access:

```python
def __init__(self):
    self.resources = {
        "your_resource": {
            "uri": "resource://your_resource",
            "name": "Your Resource",
            "description": "Description of your resource",
            "mimeType": "text/plain"
        }
    }
```

### Adding Prompts

Prompts are reusable templates for AI interactions:

```python
def __init__(self):
    self.prompts = {
        "your_prompt": {
            "name": "your_prompt",
            "description": "Description of your prompt",
            "arguments": [
                {
                    "name": "context",
                    "description": "Context for the prompt",
                    "required": True
                }
            ]
        }
    }
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest test_mcp_server.py -v

# Run specific test
python -m pytest test_mcp_server.py::TestMCPServer::test_echo_tool -v

# Run with coverage
pip install pytest-cov
python -m pytest test_mcp_server.py --cov=main --cov-report=html
```

## Environment Variables

Configure these environment variables for deployment:

- `PORT`: Server port (default: 8000)
- `PYTHONUNBUFFERED`: Set to 1 for Azure
- `PYTHONDONTWRITEBYTECODE`: Set to 1 for Azure

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t mcp-server .

# Run container
docker run -p 8000:8000 mcp-server

# Run with environment variables
docker run -p 8000:8000 -e PORT=8000 mcp-server
```

## Monitoring and Logging

The server includes comprehensive logging:

- **Application logs**: All requests and responses
- **Error logs**: Detailed error information
- **Health checks**: Available at `/health` endpoint
- **Azure logs**: Check Azure portal for deployment logs

## Security Considerations

- **CORS**: Configured for web deployment
- **Input validation**: Validate all tool parameters
- **Error handling**: Graceful error responses
- **Rate limiting**: Consider implementing for production
- **Authentication**: Add authentication for sensitive operations

## Performance Optimization

For production deployment:

1. **Use Gunicorn**: Pre-configured in startup script
2. **Configure workers**: Adjust based on your needs
3. **Enable caching**: Implement caching for expensive operations
4. **Monitor resources**: Use Azure Application Insights
5. **Scale horizontally**: Use Azure App Service scaling

## Troubleshooting

### Common Issues

1. **Deployment fails**:
   - Check Azure publish profile
   - Verify GitHub secrets
   - Review deployment logs

2. **Tools not responding**:
   - Check tool implementation
   - Verify parameter schemas
   - Review server logs

3. **Performance issues**:
   - Check worker configuration
   - Monitor memory usage
   - Review database connections

### Debug Mode

Enable debug mode for development:

```python
# In app.py
app = FastAPI(debug=True)

# In main.py
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your implementation
4. Write tests
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review Azure Web App documentation
- Open an issue on GitHub

## Next Steps

1. **Replace placeholder tools** with your actual implementations
2. **Add authentication** if needed
3. **Implement caching** for better performance
4. **Add monitoring** and alerting
5. **Scale** based on usage patterns

---

**Note**: This is a placeholder implementation. Replace the example tools with your actual business logic and add proper error handling, validation, and security measures for production use.
