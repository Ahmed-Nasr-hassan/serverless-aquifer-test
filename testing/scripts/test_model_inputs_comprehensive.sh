#!/bin/bash

# Comprehensive Model Input Test using real data from Model_Inputs.json
# This script tests all model input endpoints with actual data

set -e

# Source configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo -e "${BLUE}🧪 Starting Comprehensive Model Input API Tests with Real Data...${NC}"

# Initialize testing environment
init_testing

# Extract real data from Model_Inputs.json
echo -e "${BLUE}📊 Extracting real data from Model_Inputs.json...${NC}"

# Get user_id and model_id from the JSON file
USER_ID=$(jq -r '.data.user_id' "$MODEL_INPUTS_FILE")
MODEL_ID=$(jq -r '.data.model_id' "$MODEL_INPUTS_FILE")

echo -e "${GREEN}✅ Using User ID: $USER_ID${NC}"
echo -e "${GREEN}✅ Using Model ID: $MODEL_ID${NC}"

# Save IDs for other tests
echo "$USER_ID" > "$DATA_DIR/user_id.txt"
echo "$MODEL_ID" > "$DATA_DIR/model_id.txt"

# Test 1: Create Model Input with complete real data
test_create_model_input() {
    log_info "Testing CREATE model input with complete real data..."
    
    # Create simulation first (required for model input)
    local simulation_data=$(jq -c -n \
        --arg name "Real Data Simulation $(date +%s)" \
        --arg description "Simulation using real Model_Inputs.json data" \
        --arg simulation_type "Calibration" \
        --arg user_id "$USER_ID" \
        '{
            name: $name,
            description: $description,
            simulation_type: $simulation_type,
            user_id: $user_id
        }')
    
    local simulation_response=$(api_call "POST" "/simulations/" "$simulation_data")
    
    if validate_response "$simulation_response" "id"; then
        local simulation_id=$(echo "$simulation_response" | jq -r '.id')
        echo "$simulation_id" > "$DATA_DIR/simulation_id.txt"
        log_success "Simulation created with ID: $simulation_id"
    else
        log_error "Failed to create simulation for model input test"
        return 1
    fi
    
    # Extract complete model inputs data
    local model_inputs_data=$(jq -c '.data.model_inputs' "$MODEL_INPUTS_FILE")
    local hydraulic_conductivity_data=$(jq -c '.data.hydraulic_conductivity' "$MODEL_INPUTS_FILE")
    
    # Create model input with complete real data
    local model_input_data=$(jq -c -n \
        --arg user_id "$USER_ID" \
        --arg model_id "$MODEL_ID" \
        --argjson model_inputs "$model_inputs_data" \
        --argjson hydraulic_conductivity "$hydraulic_conductivity_data" \
        --arg simulation_id "$simulation_id" \
        --arg description "Complete model input from Model_Inputs.json with all parameters" \
        '{
            user_id: $user_id,
            model_id: $model_id,
            model_inputs: $model_inputs,
            hydraulic_conductivity: $hydraulic_conductivity,
            simulation_id: ($simulation_id | tonumber),
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

# Test 2: Get Model Input
test_get_model_input() {
    log_info "Testing GET model input..."
    
    local model_input_id=$(cat "$DATA_DIR/model_input_id.txt")
    local response=$(api_call "GET" "/model-inputs/$model_input_id")
    
    if validate_response "$response" "id"; then
        log_success "Model input retrieved successfully"
        log_api_call "GET" "/model-inputs/$model_input_id" "$response"
        
        # Verify data integrity
        local retrieved_user_id=$(echo "$response" | jq -r '.user_id')
        local retrieved_model_id=$(echo "$response" | jq -r '.model_id')
        
        if [ "$retrieved_user_id" = "$USER_ID" ] && [ "$retrieved_model_id" = "$MODEL_ID" ]; then
            log_success "Data integrity verified - user_id and model_id match"
        else
            log_warning "Data integrity issue - IDs don't match"
        fi
        
        return 0
    else
        log_error "Failed to get model input"
        log_error "Response: $response"
        return 1
    fi
}

# Test 3: Get All Model Inputs
test_get_all_model_inputs() {
    log_info "Testing GET all model inputs..."
    
    local response=$(api_call "GET" "/model-inputs/")
    
    if validate_response "$response" "length"; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count model inputs"
        log_api_call "GET" "/model-inputs/" "$response"
        return 0
    else
        log_error "Failed to get all model inputs"
        log_error "Response: $response"
        return 1
    fi
}

# Test 4: Update Model Input
test_update_model_input() {
    log_info "Testing UPDATE model input..."
    
    local model_input_id=$(cat "$DATA_DIR/model_input_id.txt")
    
    # Update with modified hydraulic conductivity data
    local updated_hydraulic_conductivity='[
        {
            "soil_material": "Sandstone",
            "layer_top_level_m": 0.0,
            "layer_bottom_level_m": -350.0,
            "hydraulic_conductivity_m_per_day": 1.0
        },
        {
            "soil_material": "Sand",
            "layer_top_level_m": -350.0,
            "layer_bottom_level_m": -700.0,
            "hydraulic_conductivity_m_per_day": 60.0
        }
    ]'
    
    local update_data=$(jq -c -n \
        --argjson hydraulic_conductivity "$updated_hydraulic_conductivity" \
        --arg description "Updated model input with modified hydraulic conductivity values" \
        '{
            hydraulic_conductivity: $hydraulic_conductivity,
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

# Test 5: Test specific model input components
test_model_input_components() {
    log_info "Testing model input components validation..."
    
    local model_input_id=$(cat "$DATA_DIR/model_input_id.txt")
    local response=$(api_call "GET" "/model-inputs/$model_input_id")
    
    if validate_response "$response" "id"; then
        # Check for specific components
        local has_radial_discretization=$(echo "$response" | jq -r '.model_inputs.radial_discretization != null')
        local has_vertical_discretization=$(echo "$response" | jq -r '.model_inputs.vertical_discretization != null')
        local has_pumping_well=$(echo "$response" | jq -r '.model_inputs.pumping_well != null')
        local has_observation_wells=$(echo "$response" | jq -r '.model_inputs.observation_wells != null')
        local has_stress_periods=$(echo "$response" | jq -r '.model_inputs.stress_periods != null')
        local has_hydraulic_parameters=$(echo "$response" | jq -r '.model_inputs.hydraulic_parameters != null')
        local has_observation_data=$(echo "$response" | jq -r '.model_inputs.observation_data != null')
        local has_simulation_settings=$(echo "$response" | jq -r '.model_inputs.simulation_settings != null')
        
        local components_ok=true
        
        if [ "$has_radial_discretization" = "true" ]; then
            log_success "✅ Radial discretization data present"
        else
            log_error "❌ Radial discretization data missing"
            components_ok=false
        fi
        
        if [ "$has_vertical_discretization" = "true" ]; then
            log_success "✅ Vertical discretization data present"
        else
            log_error "❌ Vertical discretization data missing"
            components_ok=false
        fi
        
        if [ "$has_pumping_well" = "true" ]; then
            log_success "✅ Pumping well data present"
        else
            log_error "❌ Pumping well data missing"
            components_ok=false
        fi
        
        if [ "$has_observation_wells" = "true" ]; then
            log_success "✅ Observation wells data present"
        else
            log_error "❌ Observation wells data missing"
            components_ok=false
        fi
        
        if [ "$has_stress_periods" = "true" ]; then
            log_success "✅ Stress periods data present"
        else
            log_error "❌ Stress periods data missing"
            components_ok=false
        fi
        
        if [ "$has_hydraulic_parameters" = "true" ]; then
            log_success "✅ Hydraulic parameters data present"
        else
            log_error "❌ Hydraulic parameters data missing"
            components_ok=false
        fi
        
        if [ "$has_observation_data" = "true" ]; then
            log_success "✅ Observation data present"
        else
            log_error "❌ Observation data missing"
            components_ok=false
        fi
        
        if [ "$has_simulation_settings" = "true" ]; then
            log_success "✅ Simulation settings data present"
        else
            log_error "❌ Simulation settings data missing"
            components_ok=false
        fi
        
        if [ "$components_ok" = "true" ]; then
            log_success "✅ All model input components validated successfully"
            return 0
        else
            log_error "❌ Some model input components are missing"
            return 1
        fi
    else
        log_error "Failed to retrieve model input for component validation"
        return 1
    fi
}

# Test 6: Delete Model Input
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are available
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        return 1
    fi
    
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        return 1
    fi
    
    # Check if Model_Inputs.json exists
    if [ ! -f "$MODEL_INPUTS_FILE" ]; then
        log_error "Model_Inputs.json file not found at $MODEL_INPUTS_FILE"
        return 1
    fi
    
    # Check if backend is running
    if ! curl -s "$API_BASE_URL/health" >/dev/null 2>&1; then
        log_warning "Backend server not responding at $API_BASE_URL"
        log_warning "Make sure to start the backend server before running tests"
        return 1
    fi
    
    log_success "Prerequisites check completed"
    return 0
}

# Run all tests
run_model_input_tests() {
    local tests_passed=0
    local tests_failed=0
    
    echo -e "${BLUE}🚀 Running Model Input API tests with real data...${NC}"
    
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
    
    if test_get_all_model_inputs; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_model_input_components; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_update_model_input; then
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
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}📊 Model Input Tests Summary${NC}"
    echo -e "${GREEN}✅ Tests Passed: $tests_passed${NC}"
    echo -e "${RED}❌ Tests Failed: $tests_failed${NC}"
    echo -e "${BLUE}==========================================${NC}"
    
    if [ $tests_failed -eq 0 ]; then
        log_success "🎉 All model input tests passed!"
        return 0
    else
        log_error "Some model input tests failed"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}🧪 Starting Model Input API Tests with Real Data...${NC}"
    
    # Check prerequisites
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    # Run tests
    run_model_input_tests
}

# Run main function
main "$@"
