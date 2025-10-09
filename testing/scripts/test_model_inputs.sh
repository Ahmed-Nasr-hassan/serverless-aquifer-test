#!/bin/bash

# Model Input API testing script
# Tests all model input endpoints with CRUD operations using data from Model_Inputs.json

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

log_info "🧪 Starting Model Input API tests..."

# Function to test create model input
test_create_model_input() {
    log_info "Testing CREATE model input..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local user_id=$(cat "$DATA_DIR/user_id.txt")
    local model_id=$(cat "$DATA_DIR/model_id.txt")
    local model_inputs=$(cat "$DATA_DIR/model_inputs.json")
    local hydraulic_conductivity=$(cat "$DATA_DIR/hydraulic_conductivity.json")
    
    local model_input_data=$(jq -c -n \
        --arg simulation_id "$simulation_id" \
        --arg user_id "$user_id" \
        --arg model_id "$model_id" \
        --argjson model_inputs "$model_inputs" \
        --argjson hydraulic_conductivity "$hydraulic_conductivity" \
        --arg description "Test model input from Model_Inputs.json" \
        '{
            simulation_id: ($simulation_id | tonumber),
            user_id: $user_id,
            model_id: $model_id,
            model_inputs: $model_inputs,
            hydraulic_conductivity: $hydraulic_conductivity,
            description: $description
        }')
    
    local response=$(api_call "POST" "/model-inputs/" "$model_input_data")
    
    if validate_response "$response" "id"; then
        local model_input_id=$(echo "$response" | jq -r '.id')
        echo "$model_input_id" > "$DATA_DIR/model_input_id.txt"
        log_success "Model input created with ID: $model_input_id"
        log_api_call "POST" "/model-inputs/" "$response"
        return 0
    else
        log_error "Failed to create model input"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get model input
test_get_model_input() {
    log_info "Testing GET model input..."
    
    local model_input_id=$(cat "$DATA_DIR/model_input_id.txt")
    local response=$(api_call "GET" "/model-inputs/$model_input_id")
    
    if validate_response "$response" "id"; then
        log_success "Model input retrieved successfully"
        log_api_call "GET" "/model-inputs/$model_input_id" "$response"
        return 0
    else
        log_error "Failed to get model input"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test update model input
test_update_model_input() {
    log_info "Testing UPDATE model input..."
    
    local model_input_id=$(cat "$DATA_DIR/model_input_id.txt")
    local updated_description="Updated model input description - $(date)"
    
    local update_data=$(jq -c -n \
        --arg description "$updated_description" \
        '{
            description: $description
        }')
    
    local response=$(api_call "PUT" "/model-inputs/$model_input_id" "$update_data")
    
    if validate_response "$response" "id"; then
        log_success "Model input updated successfully"
        log_api_call "PUT" "/model-inputs/$model_input_id" "$response"
        return 0
    else
        log_error "Failed to update model input"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test list model inputs
test_list_model_inputs() {
    log_info "Testing LIST model inputs..."
    
    local response=$(api_call "GET" "/model-inputs/")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count model inputs"
        log_api_call "GET" "/model-inputs/" "$response"
        return 0
    else
        log_error "Failed to list model inputs"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get model inputs by simulation
test_get_model_inputs_by_simulation() {
    log_info "Testing GET model inputs by simulation..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local response=$(api_call "GET" "/model-inputs/simulation/$simulation_id")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count model inputs for simulation $simulation_id"
        log_api_call "GET" "/model-inputs/simulation/$simulation_id" "$response"
        return 0
    else
        log_error "Failed to get model inputs by simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test delete model input
test_delete_model_input() {
    log_info "Testing DELETE model input..."
    
    local model_input_id=$(cat "$DATA_DIR/model_input_id.txt")
    local response=$(api_call "DELETE" "/model-inputs/$model_input_id")
    
    if validate_response "$response" "message"; then
        log_success "Model input deleted successfully"
        log_api_call "DELETE" "/model-inputs/$model_input_id" "$response"
        return 0
    else
        log_error "Failed to delete model input"
        log_error "Response: $response"
        return 1
    fi
}

# Function to validate model input data structure
test_model_input_data_structure() {
    log_info "Testing model input data structure validation..."
    
    local model_input_id=$(cat "$DATA_DIR/model_input_id.txt")
    local response=$(api_call "GET" "/model-inputs/$model_input_id")
    
    # Check if required JSON fields exist
    if echo "$response" | jq -e '.model_inputs' >/dev/null 2>&1 && \
       echo "$response" | jq -e '.hydraulic_conductivity' >/dev/null 2>&1; then
        log_success "Model input data structure is valid"
        
        # Log some key data for verification
        local user_id=$(echo "$response" | jq -r '.user_id')
        local model_id=$(echo "$response" | jq -r '.model_id')
        local layers_count=$(echo "$response" | jq '.hydraulic_conductivity | length')
        
        log_info "User ID: $user_id"
        log_info "Model ID: $model_id"
        log_info "Hydraulic conductivity layers: $layers_count"
        
        return 0
    else
        log_error "Model input data structure is invalid"
        log_error "Response: $response"
        return 1
    fi
}

# Main test runner
run_model_input_tests() {
    local tests_passed=0
    local tests_failed=0
    
    log_info "🚀 Running Model Input API tests..."
    
    # Test sequence
    if test_create_model_input; then
        ((tests_passed++))
    else
        ((tests_failed++))
        log_error "Cannot continue without a model input. Exiting."
        return 1
    fi
    
    if test_get_model_input; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_model_input_data_structure; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_update_model_input; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_list_model_inputs; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_get_model_inputs_by_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_delete_model_input; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    # Summary
    log_info "📊 Model Input API Test Results:"
    log_success "Passed: $tests_passed"
    if [ $tests_failed -gt 0 ]; then
        log_error "Failed: $tests_failed"
    else
        log_success "Failed: $tests_failed"
    fi
    
    return $tests_failed
}

# Run tests if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    init_testing
    run_model_input_tests
fi
