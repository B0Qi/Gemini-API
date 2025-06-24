#!/bin/bash

# Start both servers
echo "Starting Gemini API servers..."

# Start the original API server on port 8081
python server.py --port 8081 &
SERVER_PID=$!

# Start the OpenAI-compatible server on port 8080
python openai_compatible_server.py &
OPENAI_PID=$!

echo "Original API server running on port 8081 (PID: $SERVER_PID)"
echo "OpenAI-compatible API server running on port 8080 (PID: $OPENAI_PID)"

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?