#!/bin/bash

# Configuration file for API testing
# This script sets up environment variables and common functions

set -e

# API Configuration
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
export TEST_USERNAME="${TEST_USERNAME:-testuser@example.com}"
export TEST_PASSWORD="${TEST_PASSWORD:-testpassword123}"

# File paths
export TESTING_DIR="/home/ahmednasr/projects/serverless-aquifer-test/testing"
export SCRIPTS_DIR="$TESTING_DIR/scripts"
export DATA_DIR="$TESTING_DIR/data"
export LOGS_DIR="$TESTING_DIR/logs"
export MODEL_INPUTS_FILE="/home/ahmednasr/projects/serverless-aquifer-test/data-processing/Model_Inputs.json"

# Colors for output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export NC='\033[0m' # No Color

# Common functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to get authentication token
get_auth_token() {
    "$SCRIPTS_DIR/auth.sh"
}

# Function to make authenticated API call
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local token=$(get_auth_token)
    
    if [ -z "$token" ]; then
        log_error "Failed to get authentication token"
        return 1
    fi
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "$API_BASE_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "$API_BASE_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json"
    fi
}

# Function to extract data from Model_Inputs.json
extract_model_data() {
    local data_type="$1"
    
    case "$data_type" in
        "user_id")
            jq -r '.data.user_id' "$MODEL_INPUTS_FILE"
            ;;
        "model_id")
            jq -r '.data.model_id' "$MODEL_INPUTS_FILE"
            ;;
        "model_inputs")
            jq -c '.data.model_inputs' "$MODEL_INPUTS_FILE"
            ;;
        "hydraulic_conductivity")
            jq -c '.data.hydraulic_conductivity' "$MODEL_INPUTS_FILE"
            ;;
        "observation_data")
            jq -c '.data.model_inputs.observation_data' "$MODEL_INPUTS_FILE"
            ;;
        *)
            log_error "Unknown data type: $data_type"
            return 1
            ;;
    esac
}

# Function to create test data files
create_test_data() {
    log_info "Creating test data files..."
    
    # Extract and save individual data components
    extract_model_data "user_id" > "$DATA_DIR/user_id.txt"
    extract_model_data "model_id" > "$DATA_DIR/model_id.txt"
    extract_model_data "model_inputs" > "$DATA_DIR/model_inputs.json"
    extract_model_data "hydraulic_conductivity" > "$DATA_DIR/hydraulic_conductivity.json"
    extract_model_data "observation_data" > "$DATA_DIR/observation_data.json"
    
    log_success "Test data files created in $DATA_DIR"
}

# Function to validate API response
validate_response() {
    local response="$1"
    local expected_field="$2"
    
    if echo "$response" | jq -e ".$expected_field" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to log API call
log_api_call() {
    local method="$1"
    local endpoint="$2"
    local response="$3"
    local log_file="$LOGS_DIR/api_calls.log"
    
    echo "[$(date)] $method $endpoint" >> "$log_file"
    echo "Response: $response" >> "$log_file"
    echo "---" >> "$log_file"
}

# Initialize testing environment
init_testing() {
    log_info "Initializing testing environment..."
    
    # Create directories if they don't exist
    mkdir -p "$DATA_DIR" "$LOGS_DIR"
    
    # Create test data files
    create_test_data
    
    # Check if backend is running
    if ! curl -s "$API_BASE_URL/health" >/dev/null 2>&1; then
        log_warning "Backend server not responding at $API_BASE_URL"
        log_warning "Make sure to start the backend server before running tests"
    else
        log_success "Backend server is running at $API_BASE_URL"
    fi
    
    log_success "Testing environment initialized"
}

# Run initialization if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    init_testing
fi
