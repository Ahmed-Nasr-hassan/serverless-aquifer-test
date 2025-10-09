#!/bin/bash

# Test script for Models API with new 2-entity architecture

echo "🧪 Testing Models API (New Architecture)"
echo "========================================"

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

# Test 1: Create model
echo ""
echo "1. Creating a test model..."
MODEL_RESPONSE=$(curl -s -X POST "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" \
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
          {"layer": 1, "top": 100.0, "bottom": 80.0, "k": 10.0},
          {"layer": 2, "top": 80.0, "bottom": 60.0, "k": 5.0},
          {"layer": 3, "top": 60.0, "bottom": 40.0, "k": 2.0}
        ]
      },
      "wellConfig": {
        "pumpingRate": 1000.0,
        "wellRadius": 0.1,
        "screenTop": 50.0,
        "screenBottom": 30.0,
        "distanceFromWell": 10.0
      },
      "observationPoints": [
        {
          "id": "OBS-1",
          "name": "Observation Well 1",
          "distanceFromWell": 53.0,
          "topScreenLevel": -212.0,
          "bottomScreenLevel": -300.0,
          "dataPoints": [
            {"timeMinutes": 0, "waterLevel": 45.3, "drawdown": 0},
            {"timeMinutes": 5, "waterLevel": 45.82, "drawdown": 0.52},
            {"timeMinutes": 10, "waterLevel": 46.32, "drawdown": 1.02}
          ]
        }
      ],
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

# Test 2: Get model
echo ""
echo "2. Getting model..."
curl -s -X GET "$API_BASE_URL/models/$MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get model"

# Test 3: Update model
echo ""
echo "3. Updating model..."
curl -s -X PUT "$API_BASE_URL/models/$MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Test Aquifer Model",
    "description": "Updated description for the test model",
    "status": "active"
  }' | jq '.' || echo "❌ Failed to update model"

# Test 4: List all models
echo ""
echo "4. Listing all models..."
curl -s -X GET "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to list models"

# Test 5: Create another model (well type)
echo ""
echo "5. Creating a well model..."
WELL_MODEL_RESPONSE=$(curl -s -X POST "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Well Model",
    "description": "Test well model for the new architecture",
    "model_type": "well",
    "configuration": {
      "wellConfig": {
        "pumpingRate": 2000.0,
        "wellRadius": 0.15,
        "screenTop": 40.0,
        "screenBottom": 20.0
      },
      "simulationConfig": {
        "simulationTimeDays": 15,
        "timeStepDays": 0.05,
        "runType": "optimization"
      }
    },
    "user_id": "'$TEST_USER_ID'"
  }')

echo "$WELL_MODEL_RESPONSE" | jq '.' || echo "❌ Failed to create well model"

# Extract well model ID
WELL_MODEL_ID=$(echo "$WELL_MODEL_RESPONSE" | jq -r '.id // empty')

# Test 6: List models again to see both
echo ""
echo "6. Listing all models (should show both)..."
curl -s -X GET "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to list models"

# Test 7: Delete models
echo ""
echo "7. Deleting models..."
if [ -n "$WELL_MODEL_ID" ]; then
    curl -s -X DELETE "$API_BASE_URL/models/$WELL_MODEL_ID" \
      -H "Authorization: Bearer $TOKEN" && echo "✅ Well model deleted" || echo "❌ Failed to delete well model"
fi

curl -s -X DELETE "$API_BASE_URL/models/$MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Aquifer model deleted" || echo "❌ Failed to delete aquifer model"

echo ""
echo "✅ Models API test completed!"
