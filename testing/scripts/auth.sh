#!/bin/bash

# Authentication script for API testing
# This script handles user authentication and returns the access token

set -e

# Configuration
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
USERNAME="${TEST_USERNAME:-testuser@example.com}"
PASSWORD="${TEST_PASSWORD:-testpassword123}"
AUTH_FILE="/home/ahmednasr/projects/serverless-aquifer-test/testing/data/auth_token.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to authenticate and get token
authenticate() {
    echo -e "${YELLOW}🔐 Starting authentication process...${NC}" >&2
    echo -e "${YELLOW}📡 Authenticating with API at $API_BASE_URL${NC}" >&2
    
    # Make authentication request
    response=$(curl -s -X POST "$API_BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$USERNAME\",
            \"password\": \"$PASSWORD\"
        }" 2>/dev/null)
    
    # Check if curl command succeeded
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to connect to API server${NC}" >&2
        echo -e "${RED}   Make sure the backend server is running on $API_BASE_URL${NC}" >&2
        exit 1
    fi
    
    # Extract token from response
    token=$(echo "$response" | jq -r '.access_token' 2>/dev/null)
    
    if [ "$token" = "null" ] || [ -z "$token" ]; then
        echo -e "${RED}❌ Authentication failed${NC}" >&2
        echo -e "${RED}   Response: $response${NC}" >&2
        echo -e "${RED}   Please check your credentials${NC}" >&2
        exit 1
    fi
    
    # Save token to file
    echo "$token" > "$AUTH_FILE"
    echo -e "${GREEN}✅ Authentication successful${NC}" >&2
    echo -e "${GREEN}   Token saved to: $AUTH_FILE${NC}" >&2
    
    return 0
}

# Function to get stored token
get_token() {
    if [ -f "$AUTH_FILE" ]; then
        cat "$AUTH_FILE"
    else
        echo ""
    fi
}

# Function to validate token
validate_token() {
    local token="$1"
    
    if [ -z "$token" ]; then
        return 1
    fi
    
    # Test token with a simple API call
    response=$(curl -s -X GET "$API_BASE_URL/auth/me" \
        -H "Authorization: Bearer $token" 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$response" | jq -e '.user_id' >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main execution
main() {
    # Check if we have a valid token
    existing_token=$(get_token)
    
    if [ -n "$existing_token" ] && validate_token "$existing_token"; then
        echo -e "${GREEN}✅ Using existing valid token${NC}" >&2
        echo "$existing_token"
        return 0
    fi
    
    # Need to authenticate
    if [ -n "$existing_token" ]; then
        echo -e "${YELLOW}⚠️  Existing token is invalid, re-authenticating...${NC}" >&2
    fi
    
    authenticate
}

# Run main function
main "$@"
