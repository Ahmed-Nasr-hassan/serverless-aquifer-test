#!/bin/bash

# Test script for the new authentication system

echo "🧪 Testing Authentication System"
echo "==============================="

# Test 1: Check if server is running
echo "1. Checking server status..."
if curl -s http://localhost:8000/test-db >/dev/null 2>&1; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running. Starting server..."
    cd /home/ahmednasr/projects/serverless-aquifer-test/backend
    python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
    SERVER_PID=$!
    sleep 5
    echo "Server started with PID: $SERVER_PID"
fi

# Test 2: Test dev-users endpoint
echo ""
echo "2. Testing dev-users endpoint..."
curl -s http://localhost:8000/api/v1/auth/dev-users | jq '.' || echo "❌ Failed to get dev-users"

# Test 3: Test user registration
echo ""
echo "3. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "NewPass123"
  }')

echo "$REGISTER_RESPONSE" | jq '.' || echo "❌ Failed to register user"

# Test 4: Test user login
echo ""
echo "4. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "NewPass123"
  }')

echo "$LOGIN_RESPONSE" | jq '.' || echo "❌ Failed to login user"

# Extract token if login was successful
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -n "$TOKEN" ]; then
    echo "✅ Login successful, token: ${TOKEN:0:20}..."
    
    # Test 5: Test authenticated endpoint
    echo ""
    echo "5. Testing authenticated endpoint..."
    curl -s -X GET "http://localhost:8000/api/v1/auth/me" \
      -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get user info"
    
    # Test 6: Test models endpoint with authentication
    echo ""
    echo "6. Testing models endpoint with authentication..."
    curl -s -X GET "http://localhost:8000/api/v1/models/" \
      -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get models"
    
    # Test 7: Create a model
    echo ""
    echo "7. Testing model creation..."
    MODEL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/models/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Test Model",
        "description": "Test model for authentication",
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
        }
      }')
    
    echo "$MODEL_RESPONSE" | jq '.' || echo "❌ Failed to create model"
    
    # Extract model ID
    MODEL_ID=$(echo "$MODEL_RESPONSE" | jq -r '.id // empty')
    
    if [ -n "$MODEL_ID" ]; then
        echo "✅ Model created with ID: $MODEL_ID"
        
        # Test 8: Create a simulation
        echo ""
        echo "8. Testing simulation creation..."
        SIMULATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/simulations/" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d '{
            "model_id": '$MODEL_ID',
            "name": "Test Simulation",
            "description": "Test simulation for authentication",
            "simulation_type": "Forward Run"
          }')
        
        echo "$SIMULATION_RESPONSE" | jq '.' || echo "❌ Failed to create simulation"
        
        # Extract simulation ID
        SIMULATION_ID=$(echo "$SIMULATION_RESPONSE" | jq -r '.id // empty')
        
        if [ -n "$SIMULATION_ID" ]; then
            echo "✅ Simulation created with ID: $SIMULATION_ID"
            
            # Test 9: Get simulations by model
            echo ""
            echo "9. Testing get simulations by model..."
            curl -s -X GET "http://localhost:8000/api/v1/simulations/model/$MODEL_ID" \
              -H "Authorization: Bearer $TOKEN" | jq '.' || echo "❌ Failed to get simulations by model"
        fi
    fi
else
    echo "❌ Login failed, skipping authenticated tests"
fi

echo ""
echo "✅ Authentication system test completed!"
