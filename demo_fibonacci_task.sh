#!/bin/bash
echo "Calling /run-task Fibonacci demo..."
curl -X POST http://localhost:8000/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a Python function that returns the nth Fibonacci number with type hints and docstring",
    "context": "Assume n is a non-negative integer and handle edge cases"
  }'
echo