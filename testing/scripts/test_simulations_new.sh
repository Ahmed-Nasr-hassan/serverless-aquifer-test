#!/bin/bash

# Test script for Simulations API with new 2-entity architecture

echo "🧪 Testing Simulations API (New Architecture)"
echo "=============================================="

# Source the config
source "$(dirname "$0")/config.sh"

# Get auth token
echo "Getting authentication token..."
TOKEN=$($(dirname "$0")/auth.sh)
if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get authentication token"
    exit 1
fi

echo "✅ Authentication successful"

# Test 1: Create a model first (required for simulations)
echo ""
echo "1. Creating a test model..."
MODEL_RESPONSE=$(curl -s -X POST "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Model for Simulations",
    "description": "Model created for testing simulations",
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
    "user_id": "'$TEST_USER_ID'"
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
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": '$MODEL_ID',
    "name": "Test Simulation Run",
    "description": "Test simulation for the new architecture",
    "simulation_type": "Forward Run",
    "user_id": "'$TEST_USER_ID'"
  }')

echo "$SIMULATION_RESPONSE" | jq '.' || echo "❌ Failed to create simulation"

# Extract simulation ID
SIMULATION_ID=$(echo "$SIMULATION_RESPONSE" | jq -r '.id // empty')

if [ -z "$SIMULATION_ID" ]; then
    echo "❌ Failed to get simulation ID"
    exit 1
fi

echo "✅ Simulation created with ID: $SIMULATION_ID"

# Test 3: Get simulation
echo ""
echo "3. Getting simulation..."
curl -s -X GET "$API_BASE_URL/simulations/$SIMULATION_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get simulation"

# Test 4: Update simulation
echo ""
echo "4. Updating simulation..."
curl -s -X PUT "$API_BASE_URL/simulations/$SIMULATION_ID" \
  -H "Authorization: Bearer $TOKEN" \
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

# Test 5: Get simulations by model
echo ""
echo "5. Getting simulations by model..."
curl -s -X GET "$API_BASE_URL/simulations/model/$MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get simulations by model"

# Test 6: List all simulations
echo ""
echo "6. Listing all simulations..."
curl -s -X GET "$API_BASE_URL/simulations/" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to list simulations"

# Test 7: Delete simulation
echo ""
echo "7. Deleting simulation..."
curl -s -X DELETE "$API_BASE_URL/simulations/$SIMULATION_ID" \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Simulation deleted" || echo "❌ Failed to delete simulation"

# Clean up: Delete the test model
echo ""
echo "8. Cleaning up test model..."
curl -s -X DELETE "$API_BASE_URL/models/$MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Model deleted" || echo "❌ Failed to delete model"

echo ""
echo "✅ Simulations API test completed!"
