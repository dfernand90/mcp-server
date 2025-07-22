import requests

response = requests.post(
    "http://localhost:8000/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": "test-tools"
    }
)

print(response.status_code)
print(response.json())
