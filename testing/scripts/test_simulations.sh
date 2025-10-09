#!/bin/bash

# Simulation API testing script
# Tests all simulation endpoints with CRUD operations

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Test data
SIMULATION_NAME="Test Simulation $(date +%s)"
SIMULATION_DESCRIPTION="Automated test simulation created at $(date)"
SIMULATION_TYPE="Forward Run"

log_info "🧪 Starting Simulation API tests..."

# Function to test create simulation
test_create_simulation() {
    log_info "Testing CREATE simulation..."
    
    local user_id=$(cat "$DATA_DIR/user_id.txt")
    local simulation_data=$(jq -c -n \
        --arg name "$SIMULATION_NAME" \
        --arg description "$SIMULATION_DESCRIPTION" \
        --arg simulation_type "$SIMULATION_TYPE" \
        --arg user_id "$user_id" \
        '{
            name: $name,
            description: $description,
            simulation_type: $simulation_type,
            user_id: $user_id
        }')
    
    local response=$(api_call "POST" "/simulations/" "$simulation_data")
    
    if validate_response "$response" "id"; then
        local simulation_id=$(echo "$response" | jq -r '.id')
        echo "$simulation_id" > "$DATA_DIR/simulation_id.txt"
        log_success "Simulation created with ID: $simulation_id"
        log_api_call "POST" "/simulations/" "$response"
        return 0
    else
        log_error "Failed to create simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get simulation
test_get_simulation() {
    log_info "Testing GET simulation..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local response=$(api_call "GET" "/simulations/$simulation_id")
    
    if validate_response "$response" "id"; then
        log_success "Simulation retrieved successfully"
        log_api_call "GET" "/simulations/$simulation_id" "$response"
        return 0
    else
        log_error "Failed to get simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get simulation detail
test_get_simulation_detail() {
    log_info "Testing GET simulation detail..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local response=$(api_call "GET" "/simulations/$simulation_id/detail")
    
    if validate_response "$response" "id"; then
        log_success "Simulation detail retrieved successfully"
        log_api_call "GET" "/simulations/$simulation_id/detail" "$response"
        return 0
    else
        log_error "Failed to get simulation detail"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test update simulation
test_update_simulation() {
    log_info "Testing UPDATE simulation..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local update_data=$(jq -c -n \
        --arg status "running" \
        --arg radius_of_influence_meters "150.5" \
        --arg total_wells_analyzed "3" \
        --arg pumping_length_seconds "177960" \
        --arg total_simulation_time_steps "200" \
        '{
            status: $status,
            radius_of_influence_meters: ($radius_of_influence_meters | tonumber),
            total_wells_analyzed: ($total_wells_analyzed | tonumber),
            pumping_length_seconds: ($pumping_length_seconds | tonumber),
            total_simulation_time_steps: ($total_simulation_time_steps | tonumber)
        }')
    
    local response=$(api_call "PUT" "/simulations/$simulation_id" "$update_data")
    
    if validate_response "$response" "id"; then
        log_success "Simulation updated successfully"
        log_api_call "PUT" "/simulations/$simulation_id" "$response"
        return 0
    else
        log_error "Failed to update simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test list simulations
test_list_simulations() {
    log_info "Testing LIST simulations..."
    
    local response=$(api_call "GET" "/simulations/")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count simulations"
        log_api_call "GET" "/simulations/" "$response"
        return 0
    else
        log_error "Failed to list simulations"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test delete simulation
test_delete_simulation() {
    log_info "Testing DELETE simulation..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local response=$(api_call "DELETE" "/simulations/$simulation_id")
    
    if validate_response "$response" "message"; then
        log_success "Simulation deleted successfully"
        log_api_call "DELETE" "/simulations/$simulation_id" "$response"
        return 0
    else
        log_error "Failed to delete simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Main test runner
run_simulation_tests() {
    local tests_passed=0
    local tests_failed=0
    
    log_info "🚀 Running Simulation API tests..."
    
    # Test sequence
    if test_create_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
        log_error "Cannot continue without a simulation. Exiting."
        return 1
    fi
    
    if test_get_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_get_simulation_detail; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_update_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_list_simulations; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_delete_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    # Summary
    log_info "📊 Simulation API Test Results:"
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
    run_simulation_tests
fi
