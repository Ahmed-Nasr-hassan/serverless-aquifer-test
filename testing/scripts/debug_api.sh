#!/bin/bash

# Simple test script to debug the API issue

set -e

API_BASE_URL="http://localhost:8000/api/v1"
USERNAME="admin"
PASSWORD="any"

echo "🔍 Debugging API issue..."

# Get authentication token
echo "1. Getting authentication token..."
TOKEN=$(curl -s -X POST "$API_BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    exit 1
fi

echo "✅ Authentication successful"

# Test health endpoint
echo "2. Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8000/health)
echo "Health response: $HEALTH"

# Test simulations endpoint
echo "3. Testing simulations GET endpoint..."
SIMULATIONS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/simulations/" \
    -H "Authorization: Bearer $TOKEN")
echo "Simulations response: $SIMULATIONS_RESPONSE"

# Test creating a simulation
echo "4. Testing simulation creation..."
CREATE_RESPONSE=$(curl -s -X POST "$API_BASE_URL/simulations/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"name": "Debug Test", "description": "Debug", "simulation_type": "Forward Run", "user_id": "dev-user-1"}')
echo "Create response: $CREATE_RESPONSE"

echo "🔍 Debug complete"
