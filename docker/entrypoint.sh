#!/bin/bash

# Start the Ollama service in the background
echo "Starting the Ollama service..."
ollama serve &

# Give it some time to start up
sleep 5

# Pull the required model
echo "Pulling the llama3.1 model..."
ollama pull llama3.1

# Check if the model pull was successful
if [ $? -eq 0 ]; then
    echo "Model pulled successfully. Creating success flag."
    touch /root/.ollama/model_pulled
else
    echo "Failed to pull the model."
    exit 1
fi

# Start the main Ollama process with the correct arguments
# Replace `run` with the actual command and arguments needed for your use case
echo "Starting the main Ollama process..."
exec ollama run llama3.1
