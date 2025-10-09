#!/bin/bash

# Comprehensive test script for new 2-entity architecture
# Tests Models and Simulations APIs together

echo "🧪 Comprehensive Test: Models & Simulations API (New Architecture)"
echo "=================================================================="

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

# Test 1: Create multiple models
echo ""
echo "1. Creating test models..."

# Create aquifer model
AQUIFER_MODEL_RESPONSE=$(curl -s -X POST "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aquifer Model Alpha",
    "description": "Primary aquifer simulation model",
    "model_type": "aquifer",
    "configuration": {
      "aquiferConfig": {
        "ztop": 100.0,
        "specificYield": 0.2,
        "specificStorage": 0.0001,
        "hydraulicConductivity": [
          {"layer": 1, "top": 100.0, "bottom": 80.0, "k": 10.0},
          {"layer": 2, "top": 80.0, "bottom": 60.0, "k": 5.0}
        ]
      },
      "wellConfig": {
        "pumpingRate": 1000.0,
        "wellRadius": 0.1,
        "screenTop": 50.0,
        "screenBottom": 30.0
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
            {"timeMinutes": 5, "waterLevel": 45.82, "drawdown": 0.52}
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

AQUIFER_MODEL_ID=$(echo "$AQUIFER_MODEL_RESPONSE" | jq -r '.id // empty')
echo "✅ Aquifer model created with ID: $AQUIFER_MODEL_ID"

# Create well model
WELL_MODEL_RESPONSE=$(curl -s -X POST "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Well Model Beta",
    "description": "Secondary well simulation model",
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

WELL_MODEL_ID=$(echo "$WELL_MODEL_RESPONSE" | jq -r '.id // empty')
echo "✅ Well model created with ID: $WELL_MODEL_ID"

# Test 2: Create simulations for each model
echo ""
echo "2. Creating simulations..."

# Create simulation for aquifer model
AQUIFER_SIM_RESPONSE=$(curl -s -X POST "$API_BASE_URL/simulations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": '$AQUIFER_MODEL_ID',
    "name": "Aquifer Forward Run",
    "description": "Forward simulation for aquifer model",
    "simulation_type": "Forward Run",
    "user_id": "'$TEST_USER_ID'"
  }')

AQUIFER_SIM_ID=$(echo "$AQUIFER_SIM_RESPONSE" | jq -r '.id // empty')
echo "✅ Aquifer simulation created with ID: $AQUIFER_SIM_ID"

# Create simulation for well model
WELL_SIM_RESPONSE=$(curl -s -X POST "$API_BASE_URL/simulations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": '$WELL_MODEL_ID',
    "name": "Well Optimization Run",
    "description": "Optimization simulation for well model",
    "simulation_type": "Optimization",
    "user_id": "'$TEST_USER_ID'"
  }')

WELL_SIM_ID=$(echo "$WELL_SIM_RESPONSE" | jq -r '.id // empty')
echo "✅ Well simulation created with ID: $WELL_SIM_ID"

# Test 3: Update simulations with results
echo ""
echo "3. Updating simulations with results..."

# Update aquifer simulation
curl -s -X PUT "$API_BASE_URL/simulations/$AQUIFER_SIM_ID" \
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
        "totalError": 2.3,
        "radiusOfInfluence": 150.5
      }
    }
  }' | jq '.' || echo "❌ Failed to update aquifer simulation"

# Update well simulation
curl -s -X PUT "$API_BASE_URL/simulations/$WELL_SIM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "results": {
      "optimizationResults": {
        "optimalParameters": {
          "hydraulicConductivity": 8.5,
          "specificYield": 0.18
        },
        "convergenceAchieved": true,
        "iterationsCompleted": 15,
        "finalRMSE": 0.12
      }
    }
  }' | jq '.' || echo "❌ Failed to update well simulation"

# Test 4: Test relationships
echo ""
echo "4. Testing model-simulation relationships..."

# Get simulations by aquifer model
echo "Simulations for aquifer model:"
curl -s -X GET "$API_BASE_URL/simulations/model/$AQUIFER_MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get simulations by aquifer model"

# Get simulations by well model
echo "Simulations for well model:"
curl -s -X GET "$API_BASE_URL/simulations/model/$WELL_MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get simulations by well model"

# Test 5: List all entities
echo ""
echo "5. Listing all entities..."

echo "All models:"
curl -s -X GET "$API_BASE_URL/models/" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {id, name, model_type, status}' || echo "❌ Failed to list models"

echo "All simulations:"
curl -s -X GET "$API_BASE_URL/simulations/" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {id, name, model_id, simulation_type, status}' || echo "❌ Failed to list simulations"

# Test 6: Cleanup
echo ""
echo "6. Cleaning up test data..."

# Delete simulations first (due to foreign key constraints)
curl -s -X DELETE "$API_BASE_URL/simulations/$AQUIFER_SIM_ID" \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Aquifer simulation deleted" || echo "❌ Failed to delete aquifer simulation"

curl -s -X DELETE "$API_BASE_URL/simulations/$WELL_SIM_ID" \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Well simulation deleted" || echo "❌ Failed to delete well simulation"

# Delete models
curl -s -X DELETE "$API_BASE_URL/models/$AQUIFER_MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Aquifer model deleted" || echo "❌ Failed to delete aquifer model"

curl -s -X DELETE "$API_BASE_URL/models/$WELL_MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Well model deleted" || echo "❌ Failed to delete well model"

echo ""
echo "✅ Comprehensive test completed!"
echo "📊 Summary:"
echo "   - Created 2 models (aquifer + well)"
echo "   - Created 2 simulations (forward + optimization)"
echo "   - Tested model-simulation relationships"
echo "   - Updated simulations with results"
echo "   - Cleaned up all test data"
