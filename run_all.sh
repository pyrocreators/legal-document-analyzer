#!/bin/bash

python3 mcp/server.py &

fastapi dev app.py &

cd ./frontend
npm run dev &

wait
