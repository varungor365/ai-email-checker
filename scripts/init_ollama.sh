#!/bin/bash

# Ollama Model Initialization Script
# Downloads and configures AI models for local inference

set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
MODELS=("mistral" "llama2")

echo "🤖 AI Model Initialization"
echo "=========================="
echo ""

# Wait for Ollama to be ready
echo "Waiting for Ollama service..."
until curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; do
    echo "  ⏳ Ollama not ready yet... waiting"
    sleep 5
done
echo "  ✅ Ollama is ready!"
echo ""

# Check existing models
echo "Checking existing models..."
EXISTING_MODELS=$(curl -s "$OLLAMA_HOST/api/tags" | jq -r '.models[].name' 2>/dev/null || echo "")

# Download models
for MODEL in "${MODELS[@]}"; do
    echo ""
    echo "📦 Processing model: $MODEL"
    echo "----------------------------"
    
    if echo "$EXISTING_MODELS" | grep -q "^$MODEL:"; then
        echo "  ✓ Model $MODEL already exists"
    else
        echo "  ⬇️  Downloading $MODEL (this may take several minutes)..."
        
        # Pull the model
        if curl -X POST "$OLLAMA_HOST/api/pull" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"$MODEL\"}" \
            --max-time 1800 \
            --silent \
            --show-error; then
            echo "  ✅ Successfully downloaded $MODEL"
        else
            echo "  ❌ Failed to download $MODEL"
        fi
    fi
done

echo ""
echo "🎉 Model initialization complete!"
echo ""

# List all models
echo "Available models:"
curl -s "$OLLAMA_HOST/api/tags" | jq -r '.models[] | "  - \(.name) (\(.size/1024/1024/1024 | floor)GB)"' 2>/dev/null || echo "  (Unable to list models)"

echo ""
echo "✨ AI system is ready for autonomous operation"
