#!/bin/bash

# Test script for the new 2-entity backend architecture

echo "🧪 Testing New Backend Architecture"
echo "=================================="

# Test database connection
echo "1. Testing database connection..."
curl -s http://localhost:8000/test-db | jq '.' || echo "❌ Backend not running"

echo ""
echo "2. Testing Models API..."

# Test creating a model
echo "Creating a test model..."
MODEL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/models/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Aquifer Model",
    "description": "Test model for the new architecture",
    "model_type": "aquifer",
    "configuration": {
      "aquiferConfig": {
        "ztop": 100.0,
        "specificYield": 0.2,
        "specificStorage": 0.0001,
        "hydraulicConductivity": [
          {"layer": 1, "top": 100.0, "bottom": 80.0, "k": 10.0}
        ]
      },
      "wellConfig": {
        "pumpingRate": 1000.0,
        "wellRadius": 0.1,
        "screenTop": 50.0,
        "screenBottom": 30.0
      },
      "simulationConfig": {
        "simulationTimeDays": 30,
        "timeStepDays": 0.1,
        "runType": "forward"
      }
    },
    "user_id": "test-user-123"
  }')

echo "$MODEL_RESPONSE" | jq '.' || echo "❌ Failed to create model"

# Extract model ID
MODEL_ID=$(echo "$MODEL_RESPONSE" | jq -r '.id // empty')

if [ -n "$MODEL_ID" ]; then
    echo ""
    echo "3. Testing Simulations API..."
    
    # Test creating a simulation
    echo "Creating a test simulation..."
    SIMULATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/simulations/" \
      -H "Content-Type: application/json" \
      -d "{
        \"model_id\": $MODEL_ID,
        \"name\": \"Test Simulation Run\",
        \"description\": \"Test simulation for model $MODEL_ID\",
        \"simulation_type\": \"Forward Run\",
        \"user_id\": \"test-user-123\"
      }")
    
    echo "$SIMULATION_RESPONSE" | jq '.' || echo "❌ Failed to create simulation"
    
    # Test getting simulations by model
    echo ""
    echo "4. Testing get simulations by model..."
    curl -s "http://localhost:8000/api/v1/simulations/model/$MODEL_ID" | jq '.' || echo "❌ Failed to get simulations by model"
fi

echo ""
echo "5. Testing list endpoints..."
echo "Models:"
curl -s "http://localhost:8000/api/v1/models/" | jq '.[] | {id, name, model_type}' || echo "❌ Failed to list models"

echo ""
echo "Simulations:"
curl -s "http://localhost:8000/api/v1/simulations/" | jq '.[] | {id, name, model_id, simulation_type}' || echo "❌ Failed to list simulations"

echo ""
echo "✅ Backend architecture test completed!"
