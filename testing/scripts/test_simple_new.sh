#!/bin/bash

# Simple test script for new 2-entity architecture (without authentication)

echo "🧪 Simple Test: Models & Simulations API (No Auth)"
echo "=================================================="

API_BASE_URL="http://localhost:8000/api/v1"

# Test 1: Create a model
echo "1. Creating a test model..."
MODEL_RESPONSE=$(curl -s -X POST "$API_BASE_URL/models/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Test Model",
    "description": "Model for simple testing",
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
    "user_id": "simple-test-user"
  }')

echo "$MODEL_RESPONSE" | jq '.' || echo "❌ Failed to create model"

# Extract model ID
MODEL_ID=$(echo "$MODEL_RESPONSE" | jq -r '.id // empty')

if [ -z "$MODEL_ID" ]; then
    echo "❌ Failed to get model ID"
    exit 1
fi

echo "✅ Model created with ID: $MODEL_ID"

# Test 2: Create simulation
echo ""
echo "2. Creating a simulation..."
SIMULATION_RESPONSE=$(curl -s -X POST "$API_BASE_URL/simulations/" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": '$MODEL_ID',
    "name": "Simple Test Simulation",
    "description": "Simple test simulation",
    "simulation_type": "Forward Run",
    "user_id": "simple-test-user"
  }')

echo "$SIMULATION_RESPONSE" | jq '.' || echo "❌ Failed to create simulation"

# Extract simulation ID
SIMULATION_ID=$(echo "$SIMULATION_RESPONSE" | jq -r '.id // empty')

if [ -z "$SIMULATION_ID" ]; then
    echo "❌ Failed to get simulation ID"
    exit 1
fi

echo "✅ Simulation created with ID: $SIMULATION_ID"

# Test 3: Update simulation with results
echo ""
echo "3. Updating simulation with results..."
curl -s -X PUT "$API_BASE_URL/simulations/$SIMULATION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "results": {
      "drawdownData": [
        {"time": 0, "drawdown": 0},
        {"time": 5, "drawdown": 0.5},
        {"time": 10, "drawdown": 1.0}
      ],
      "analysisResults": {
        "rmse": 0.15,
        "totalError": 2.3
      }
    }
  }' | jq '.' || echo "❌ Failed to update simulation"

# Test 4: Get simulations by model
echo ""
echo "4. Getting simulations by model..."
curl -s -X GET "$API_BASE_URL/simulations/model/$MODEL_ID" | jq '.' || echo "❌ Failed to get simulations by model"

# Test 5: List all models and simulations
echo ""
echo "5. Listing all entities..."
echo "Models:"
curl -s -X GET "$API_BASE_URL/models/" | jq '.[] | {id, name, model_type}' || echo "❌ Failed to list models"

echo ""
echo "Simulations:"
curl -s -X GET "$API_BASE_URL/simulations/" | jq '.[] | {id, name, model_id, simulation_type, status}' || echo "❌ Failed to list simulations"

# Test 6: Cleanup
echo ""
echo "6. Cleaning up..."
curl -s -X DELETE "$API_BASE_URL/simulations/$SIMULATION_ID" && echo "✅ Simulation deleted" || echo "❌ Failed to delete simulation"
curl -s -X DELETE "$API_BASE_URL/models/$MODEL_ID" && echo "✅ Model deleted" || echo "❌ Failed to delete model"

echo ""
echo "✅ Simple test completed successfully!"
echo "📊 Summary:"
echo "   - Created 1 model"
echo "   - Created 1 simulation linked to the model"
echo "   - Updated simulation with results"
echo "   - Tested model-simulation relationships"
echo "   - Cleaned up test data"
