#!/bin/bash

# Optimization Result API testing script
# Tests all optimization result endpoints with CRUD operations

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

log_info "🧪 Starting Optimization Result API tests..."

# Function to test create optimization result
test_create_optimization_result() {
    log_info "Testing CREATE optimization result..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    
    # Create optimization configuration
    local optimization_config=$(jq -c -n \
        --argjson parameters_optimized '["hydraulic_conductivity", "specific_yield", "specific_storage"]' \
        --arg max_iterations "100" \
        --arg tolerance "1e-6" \
        --arg algorithm "PEST" \
        '{
            parameters_optimized: $parameters_optimized,
            max_iterations: ($max_iterations | tonumber),
            tolerance: ($tolerance | tonumber),
            algorithm: $algorithm,
            constraints: {
                hydraulic_conductivity_min: 0.001,
                hydraulic_conductivity_max: 100.0,
                specific_yield_min: 0.01,
                specific_yield_max: 0.5
            }
        }')
    
    # Create optimization results
    local optimization_results=$(jq -c -n \
        --arg hydraulic_conductivity "0.9073948333333328" \
        --arg specific_yield "0.11662639999999996" \
        --arg specific_storage "3.977036316666669e-07" \
        --arg convergence_achieved "true" \
        --arg iterations_completed "45" \
        '{
            optimal_values: {
                hydraulic_conductivity: ($hydraulic_conductivity | tonumber),
                specific_yield: ($specific_yield | tonumber),
                specific_storage: ($specific_storage | tonumber)
            },
            convergence_achieved: ($convergence_achieved == "true"),
            iterations_completed: ($iterations_completed | tonumber),
            final_objective_function: 0.025,
            parameter_sensitivity: {
                hydraulic_conductivity: 0.8,
                specific_yield: 0.6,
                specific_storage: 0.3
            }
        }')
    
    # Create performance metrics
    local performance_metrics=$(jq -c -n \
        --arg rmse "0.025" \
        --arg total_residual_error "2.5" \
        --arg r_squared "0.95" \
        --arg nash_sutcliffe "0.92" \
        '{
            rmse: ($rmse | tonumber),
            total_residual_error: ($total_residual_error | tonumber),
            r_squared: ($r_squared | tonumber),
            nash_sutcliffe: ($nash_sutcliffe | tonumber),
            convergence_history: [
                {"iteration": 1, "objective": 0.5},
                {"iteration": 10, "objective": 0.2},
                {"iteration": 20, "objective": 0.1},
                {"iteration": 30, "objective": 0.05},
                {"iteration": 45, "objective": 0.025}
            ]
        }')
    
    local optimization_data=$(jq -c -n \
        --arg simulation_id "$simulation_id" \
        --argjson optimization_config "$optimization_config" \
        --argjson optimization_results "$optimization_results" \
        --argjson performance_metrics "$performance_metrics" \
        --arg description "Test optimization result from automated testing" \
        '{
            simulation_id: ($simulation_id | tonumber),
            optimization_config: $optimization_config,
            optimization_results: $optimization_results,
            performance_metrics: $performance_metrics,
            description: $description
        }')
    
    local response=$(api_call "POST" "/optimization-results/" "$optimization_data")
    
    if validate_response "$response" "id"; then
        local optimization_result_id=$(echo "$response" | jq -r '.id')
        echo "$optimization_result_id" > "$DATA_DIR/optimization_result_id.txt"
        log_success "Optimization result created with ID: $optimization_result_id"
        log_api_call "POST" "/optimization-results/" "$response"
        return 0
    else
        log_error "Failed to create optimization result"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get optimization result
test_get_optimization_result() {
    log_info "Testing GET optimization result..."
    
    local optimization_result_id=$(cat "$DATA_DIR/optimization_result_id.txt")
    local response=$(api_call "GET" "/optimization-results/$optimization_result_id")
    
    if validate_response "$response" "id"; then
        log_success "Optimization result retrieved successfully"
        log_api_call "GET" "/optimization-results/$optimization_result_id" "$response"
        return 0
    else
        log_error "Failed to get optimization result"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test update optimization result
test_update_optimization_result() {
    log_info "Testing UPDATE optimization result..."
    
    local optimization_result_id=$(cat "$DATA_DIR/optimization_result_id.txt")
    local updated_description="Updated optimization result description - $(date)"
    
    # Update performance metrics
    local updated_metrics=$(jq -c -n \
        --arg rmse "0.020" \
        --arg total_residual_error "2.0" \
        --arg r_squared "0.96" \
        '{
            rmse: ($rmse | tonumber),
            total_residual_error: ($total_residual_error | tonumber),
            r_squared: ($r_squared | tonumber),
            nash_sutcliffe: 0.94,
            convergence_history: [
                {"iteration": 1, "objective": 0.5},
                {"iteration": 10, "objective": 0.2},
                {"iteration": 20, "objective": 0.1},
                {"iteration": 30, "objective": 0.05},
                {"iteration": 45, "objective": 0.020}
            ]
        }')
    
    local update_data=$(jq -c -n \
        --arg description "$updated_description" \
        --argjson performance_metrics "$updated_metrics" \
        '{
            description: $description,
            performance_metrics: $performance_metrics
        }')
    
    local response=$(api_call "PUT" "/optimization-results/$optimization_result_id" "$update_data")
    
    if validate_response "$response" "id"; then
        log_success "Optimization result updated successfully"
        log_api_call "PUT" "/optimization-results/$optimization_result_id" "$response"
        return 0
    else
        log_error "Failed to update optimization result"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test list optimization results
test_list_optimization_results() {
    log_info "Testing LIST optimization results..."
    
    local response=$(api_call "GET" "/optimization-results/")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count optimization result records"
        log_api_call "GET" "/optimization-results/" "$response"
        return 0
    else
        log_error "Failed to list optimization results"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test get optimization results by simulation
test_get_optimization_results_by_simulation() {
    log_info "Testing GET optimization results by simulation..."
    
    local simulation_id=$(cat "$DATA_DIR/simulation_id.txt")
    local response=$(api_call "GET" "/optimization-results/simulation/$simulation_id")
    
    if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
        local count=$(echo "$response" | jq 'length')
        log_success "Retrieved $count optimization result records for simulation $simulation_id"
        log_api_call "GET" "/optimization-results/simulation/$simulation_id" "$response"
        return 0
    else
        log_error "Failed to get optimization results by simulation"
        log_error "Response: $response"
        return 1
    fi
}

# Function to test delete optimization result
test_delete_optimization_result() {
    log_info "Testing DELETE optimization result..."
    
    local optimization_result_id=$(cat "$DATA_DIR/optimization_result_id.txt")
    local response=$(api_call "DELETE" "/optimization-results/$optimization_result_id")
    
    if validate_response "$response" "message"; then
        log_success "Optimization result deleted successfully"
        log_api_call "DELETE" "/optimization-results/$optimization_result_id" "$response"
        return 0
    else
        log_error "Failed to delete optimization result"
        log_error "Response: $response"
        return 1
    fi
}

# Function to validate optimization result structure
test_optimization_result_structure() {
    log_info "Testing optimization result structure validation..."
    
    local optimization_result_id=$(cat "$DATA_DIR/optimization_result_id.txt")
    local response=$(api_call "GET" "/optimization-results/$optimization_result_id")
    
    # Check if required JSON fields exist
    if echo "$response" | jq -e '.optimization_config' >/dev/null 2>&1 && \
       echo "$response" | jq -e '.optimization_results' >/dev/null 2>&1 && \
       echo "$response" | jq -e '.performance_metrics' >/dev/null 2>&1; then
        log_success "Optimization result structure is valid"
        
        # Log some key data for verification
        local parameters_count=$(echo "$response" | jq '.optimization_config.parameters_optimized | length')
        local convergence=$(echo "$response" | jq -r '.optimization_results.convergence_achieved')
        local iterations=$(echo "$response" | jq -r '.optimization_results.iterations_completed')
        local rmse=$(echo "$response" | jq -r '.performance_metrics.rmse')
        local r_squared=$(echo "$response" | jq -r '.performance_metrics.r_squared')
        
        log_info "Parameters optimized: $parameters_count"
        log_info "Convergence achieved: $convergence"
        log_info "Iterations completed: $iterations"
        log_info "RMSE: $rmse"
        log_info "R-squared: $r_squared"
        
        # Log optimal values
        local hydraulic_conductivity=$(echo "$response" | jq -r '.optimization_results.optimal_values.hydraulic_conductivity')
        local specific_yield=$(echo "$response" | jq -r '.optimization_results.optimal_values.specific_yield')
        
        log_info "Optimal hydraulic conductivity: $hydraulic_conductivity"
        log_info "Optimal specific yield: $specific_yield"
        
        return 0
    else
        log_error "Optimization result structure is invalid"
        log_error "Response: $response"
        return 1
    fi
}

# Main test runner
run_optimization_result_tests() {
    local tests_passed=0
    local tests_failed=0
    
    log_info "🚀 Running Optimization Result API tests..."
    
    # Test sequence
    if test_create_optimization_result; then
        ((tests_passed++))
    else
        ((tests_failed++))
        log_error "Cannot continue without an optimization result. Exiting."
        return 1
    fi
    
    if test_get_optimization_result; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_optimization_result_structure; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_update_optimization_result; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_list_optimization_results; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_get_optimization_results_by_simulation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_delete_optimization_result; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    # Summary
    log_info "📊 Optimization Result API Test Results:"
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
    run_optimization_result_tests
fi
