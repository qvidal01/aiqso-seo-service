#!/bin/bash
# Run the SerpBear MCP Server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# Check if built
if [ ! -d "dist" ]; then
    echo "Building MCP server..."
    npm install
    npm run build
fi

# Run the server
node dist/server.js
