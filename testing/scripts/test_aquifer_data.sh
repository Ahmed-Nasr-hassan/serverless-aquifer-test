#!/bin/bash

# Aquifer Data API testing script
# Tests all aquifer data endpoints with CRUD operations using data from Model_Inputs.json

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

log_info "🧪 Starting Aquifer Data API tests..."

# Function to test create aquifer data
test_create_aquifer_data() {
    log_info "Testing CREATE aquifer data..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local hydraulic_conductivity=$(cat "$DATA_DIR/hydraulic_conductivity.json")
    
    local aquifer_data=$(jq -c -n \
        --arg simulation_id "$simulation_id" \
        --argjson hydraulic_conductivity_layers "$hydraulic_conductivity" \
        --arg specific_yield "0.11662639999999996" \
        --arg specific_storage "3.977036316666669e-07" \
        --arg description "Test aquifer data from Model_Inputs.json" \
        '{
            simulation_id: ($simulation_id | tonumber),
            hydraulic_conductivity_layers: $hydraulic_conductivity_layers,
            specific_yield: ($specific_yield | tonumber),
            specific_storage: ($specific_storage | tonumber),
            description: $description
        }')
    
    local response=$(api_call "POST" "/aquifer-data/" "$aquifer_data")
    
    if validate_response "$response" "id"; then
        local aquifer_data_id=$(echo "$response" | jq -r '.id')
        echo "$aquifer_data_id" > "$DATA_DIR/aquifer_data_id.txt"
        log_success "Aquifer data created with ID: $aquifer_data_id"
        log_api_call "POST" "/aquifer-data/" "$response"
        return 0
    else
        log_error "Failed to create aquifer data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get aquifer data
test_get_aquifer_data() {
    log_info "Testing GET aquifer data..."
    
    local aquifer_data_id=$(cat "$DATA_DIR/aquifer_data_id.txt")
    local response=$(api_call "GET" "/aquifer-data/$aquifer_data_id")
    
    if validate_response "$response" "id"; then
        log_success "Aquifer data retrieved successfully"
        log_api_call "GET" "/aquifer-data/$aquifer_data_id" "$response"
        return 0
    else
        log_error "Failed to get aquifer data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test update aquifer data
test_update_aquifer_data() {
    log_info "Testing UPDATE aquifer data..."
    
    local aquifer_data_id=$(cat "$DATA_DIR/aquifer_data_id.txt")
    local updated_description="Updated aquifer data description - $(date)"
    
    local update_data=$(jq -c -n \
        --arg description "$updated_description" \
        --arg specific_yield "0.12" \
        '{
            description: $description,
            specific_yield: ($specific_yield | tonumber)
        }')
    
    local response=$(api_call "PUT" "/aquifer-data/$aquifer_data_id" "$update_data")
    
    if validate_response "$response" "id"; then
        log_success "Aquifer data updated successfully"
        log_api_call "PUT" "/aquifer-data/$aquifer_data_id" "$response"
        return 0
    else
        log_error "Failed to update aquifer data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test list aquifer data
test_list_aquifer_data() {
    log_info "Testing LIST aquifer data..."
    
    local response=$(api_call "GET" "/aquifer-data/")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count aquifer data records"
        log_api_call "GET" "/aquifer-data/" "$response"
        return 0
    else
        log_error "Failed to list aquifer data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get aquifer data by simulation
test_get_aquifer_data_by_simulation() {
    log_info "Testing GET aquifer data by simulation..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local response=$(api_call "GET" "/aquifer-data/simulation/$simulation_id")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count aquifer data records for simulation $simulation_id"
        log_api_call "GET" "/aquifer-data/simulation/$simulation_id" "$response"
        return 0
    else
        log_error "Failed to get aquifer data by simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test delete aquifer data
test_delete_aquifer_data() {
    log_info "Testing DELETE aquifer data..."
    
    local aquifer_data_id=$(cat "$DATA_DIR/aquifer_data_id.txt")
    local response=$(api_call "DELETE" "/aquifer-data/$aquifer_data_id")
    
    if validate_response "$response" "message"; then
        log_success "Aquifer data deleted successfully"
        log_api_call "DELETE" "/aquifer-data/$aquifer_data_id" "$response"
        return 0
    else
        log_error "Failed to delete aquifer data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to validate aquifer data structure
test_aquifer_data_structure() {
    log_info "Testing aquifer data structure validation..."
    
    local aquifer_data_id=$(cat "$DATA_DIR/aquifer_data_id.txt")
    local response=$(api_call "GET" "/aquifer-data/$aquifer_data_id")
    
    # Check if required JSON fields exist
    if echo "$response" | jq -e '.hydraulic_conductivity_layers' >/dev/null 2>&1; then
        log_success "Aquifer data structure is valid"
        
        # Log some key data for verification
        local layers_count=$(echo "$response" | jq '.hydraulic_conductivity_layers | length')
        local specific_yield=$(echo "$response" | jq -r '.specific_yield')
        local specific_storage=$(echo "$response" | jq -r '.specific_storage')
        
        log_info "Hydraulic conductivity layers: $layers_count"
        log_info "Specific yield: $specific_yield"
        log_info "Specific storage: $specific_storage"
        
        # Log first layer details
        if [ "$layers_count" -gt 0 ]; then
            local first_layer=$(echo "$response" | jq '.hydraulic_conductivity_layers[0]')
            local soil_material=$(echo "$first_layer" | jq -r '.soil_material')
            local conductivity=$(echo "$first_layer" | jq -r '.hydraulic_conductivity_m_per_day')
            log_info "First layer - Material: $soil_material, Conductivity: $conductivity"
        fi
        
        return 0
    else
        log_error "Aquifer data structure is invalid"
        log_error "Response: $response"
        return 1
    fi
}

# Main test runner
run_aquifer_data_tests() {
    local tests_passed=0
    local tests_failed=0
    
    log_info "🚀 Running Aquifer Data API tests..."
    
    # Test sequence
    if test_create_aquifer_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
        log_error "Cannot continue without aquifer data. Exiting."
        return 1
    fi
    
    if test_get_aquifer_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_aquifer_data_structure; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_update_aquifer_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_list_aquifer_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_get_aquifer_data_by_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_delete_aquifer_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    # Summary
    log_info "📊 Aquifer Data API Test Results:"
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
    run_aquifer_data_tests
fi
