#!/bin/bash

# Well Data API testing script
# Tests all well data endpoints with CRUD operations using data from Model_Inputs.json

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

log_info "🧪 Starting Well Data API tests..."

# Function to test create well data
test_create_well_data() {
    log_info "Testing CREATE well data..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local observation_data=$(cat "$DATA_DIR/observation_data.json")
    
    # Extract well configuration from observation data
    local well_config=$(echo "$observation_data" | jq '.observation_wells["OBS-1"]')
    local well_id=$(echo "$well_config" | jq -r '.well_id')
    local distance=$(echo "$well_config" | jq -r '.distance_from_well')
    local top_screen=$(echo "$well_config" | jq -r '.top_screen_level')
    local bottom_screen=$(echo "$well_config" | jq -r '.bottom_screen_level')
    
    # Create well configuration JSON
    local well_configuration=$(jq -c -n \
        --arg distance "$distance" \
        --arg top_screen "$top_screen" \
        --arg bottom_screen "$bottom_screen" \
        --arg well_radius "0.1" \
        '{
            distance_from_pumping_well_meters: ($distance | tonumber),
            well_radius_meters: ($well_radius | tonumber),
            screen_top_meters: ($top_screen | tonumber),
            screen_bottom_meters: ($bottom_screen | tonumber)
        }')
    
    # Create simulation results JSON
    local simulation_results=$(echo "$well_config" | jq '.data')
    
    # Create analysis results JSON
    local analysis_results=$(jq -c -n \
        --arg rmse "0.05" \
        --arg total_residual_error "2.5" \
        '{
            rmse: ($rmse | tonumber),
            total_residual_error: ($total_residual_error | tonumber),
            interpolated_times: [],
            interpolated_observed_drawdown: [],
            interpolated_simulated_drawdown: []
        }')
    
    local well_data=$(jq -c -n \
        --arg simulation_id "$simulation_id" \
        --arg well_id "$well_id" \
        --arg well_type "observation" \
        --argjson well_configuration "$well_configuration" \
        --argjson simulation_results "$simulation_results" \
        --argjson analysis_results "$analysis_results" \
        --arg description "Test well data from Model_Inputs.json" \
        '{
            simulation_id: ($simulation_id | tonumber),
            well_id: $well_id,
            well_type: $well_type,
            well_configuration: $well_configuration,
            simulation_results: $simulation_results,
            analysis_results: $analysis_results,
            description: $description
        }')
    
    local response=$(api_call "POST" "/well-data/" "$well_data")
    
    if validate_response "$response" "id"; then
        local well_data_id=$(echo "$response" | jq -r '.id')
        echo "$well_data_id" > "$DATA_DIR/well_data_id.txt"
        log_success "Well data created with ID: $well_data_id"
        log_api_call "POST" "/well-data/" "$response"
        return 0
    else
        log_error "Failed to create well data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get well data
test_get_well_data() {
    log_info "Testing GET well data..."
    
    local well_data_id=$(cat "$DATA_DIR/well_data_id.txt")
    local response=$(api_call "GET" "/well-data/$well_data_id")
    
    if validate_response "$response" "id"; then
        log_success "Well data retrieved successfully"
        log_api_call "GET" "/well-data/$well_data_id" "$response"
        return 0
    else
        log_error "Failed to get well data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test update well data
test_update_well_data() {
    log_info "Testing UPDATE well data..."
    
    local well_data_id=$(cat "$DATA_DIR/well_data_id.txt")
    local updated_description="Updated well data description - $(date)"
    
    # Update analysis results
    local updated_analysis=$(jq -c -n \
        --arg rmse "0.03" \
        --arg total_residual_error "1.8" \
        '{
            rmse: ($rmse | tonumber),
            total_residual_error: ($total_residual_error | tonumber),
            interpolated_times: [0, 300, 600],
            interpolated_observed_drawdown: [0, 0.5, 1.0],
            interpolated_simulated_drawdown: [0, 0.48, 0.98]
        }')
    
    local update_data=$(jq -c -n \
        --arg description "$updated_description" \
        --argjson analysis_results "$updated_analysis" \
        '{
            description: $description,
            analysis_results: $analysis_results
        }')
    
    local response=$(api_call "PUT" "/well-data/$well_data_id" "$update_data")
    
    if validate_response "$response" "id"; then
        log_success "Well data updated successfully"
        log_api_call "PUT" "/well-data/$well_data_id" "$response"
        return 0
    else
        log_error "Failed to update well data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test list well data
test_list_well_data() {
    log_info "Testing LIST well data..."
    
    local response=$(api_call "GET" "/well-data/")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count well data records"
        log_api_call "GET" "/well-data/" "$response"
        return 0
    else
        log_error "Failed to list well data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get well data by simulation
test_get_well_data_by_simulation() {
    log_info "Testing GET well data by simulation..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local response=$(api_call "GET" "/well-data/simulation/$simulation_id")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count well data records for simulation $simulation_id"
        log_api_call "GET" "/well-data/simulation/$simulation_id" "$response"
        return 0
    else
        log_error "Failed to get well data by simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test delete well data
test_delete_well_data() {
    log_info "Testing DELETE well data..."
    
    local well_data_id=$(cat "$DATA_DIR/well_data_id.txt")
    local response=$(api_call "DELETE" "/well-data/$well_data_id")
    
    if validate_response "$response" "message"; then
        log_success "Well data deleted successfully"
        log_api_call "DELETE" "/well-data/$well_data_id" "$response"
        return 0
    else
        log_error "Failed to delete well data"
        log_error "Response: $response"
        return 1
    fi
}

# Function to validate well data structure
test_well_data_structure() {
    log_info "Testing well data structure validation..."
    
    local well_data_id=$(cat "$DATA_DIR/well_data_id.txt")
    local response=$(api_call "GET" "/well-data/$well_data_id")
    
    # Check if required JSON fields exist
    if echo "$response" | jq -e '.well_configuration' >/dev/null 2>&1 && \
       echo "$response" | jq -e '.simulation_results' >/dev/null 2>&1 && \
       echo "$response" | jq -e '.analysis_results' >/dev/null 2>&1; then
        log_success "Well data structure is valid"
        
        # Log some key data for verification
        local well_id=$(echo "$response" | jq -r '.well_id')
        local well_type=$(echo "$response" | jq -r '.well_type')
        local distance=$(echo "$response" | jq -r '.well_configuration.distance_from_pumping_well_meters')
        local rmse=$(echo "$response" | jq -r '.analysis_results.rmse')
        
        log_info "Well ID: $well_id"
        log_info "Well Type: $well_type"
        log_info "Distance from pumping well: $distance meters"
        log_info "RMSE: $rmse"
        
        # Check if simulation results have time series data
        local time_count=$(echo "$response" | jq '.simulation_results.time_minutes | length')
        local drawdown_count=$(echo "$response" | jq '.simulation_results.drawdown | length')
        
        log_info "Time series data points: $time_count"
        log_info "Drawdown data points: $drawdown_count"
        
        return 0
    else
        log_error "Well data structure is invalid"
        log_error "Response: $response"
        return 1
    fi
}

# Main test runner
run_well_data_tests() {
    local tests_passed=0
    local tests_failed=0
    
    log_info "🚀 Running Well Data API tests..."
    
    # Test sequence
    if test_create_well_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
        log_error "Cannot continue without well data. Exiting."
        return 1
    fi
    
    if test_get_well_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_well_data_structure; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_update_well_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_list_well_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_get_well_data_by_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_delete_well_data; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    # Summary
    log_info "📊 Well Data API Test Results:"
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
    run_well_data_tests
fi
