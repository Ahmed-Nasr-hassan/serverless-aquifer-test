#!/bin/bash

# Master test runner script
# Runs all API tests in sequence and provides comprehensive reporting

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Test results tracking
declare -A test_results
declare -A test_times
total_tests=0
total_passed=0
total_failed=0

log_info "🚀 Starting Comprehensive API Testing Suite..."

# Function to run a test suite
run_test_suite() {
    local test_name="$1"
    local test_script="$2"
    local start_time=$(date +%s)
    
    log_info "🧪 Running $test_name tests..."
    echo "=========================================="
    
    if "$test_script"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        test_results["$test_name"]="PASSED"
        test_times["$test_name"]="$duration"
        ((total_passed++))
        log_success "$test_name tests completed successfully in ${duration}s"
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        test_results["$test_name"]="FAILED"
        test_times["$test_name"]="$duration"
        ((total_failed++))
        log_error "$test_name tests failed after ${duration}s"
    fi
    
    echo "=========================================="
    echo ""
    ((total_tests++))
}

# Function to check prerequisites
check_prerequisites() {
    log_info "🔍 Checking prerequisites..."
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Please install jq first."
        log_error "On Ubuntu/Debian: sudo apt-get install jq"
        log_error "On macOS: brew install jq"
        exit 1
    fi
    
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed. Please install curl first."
        exit 1
    fi
    
    # Check if Model_Inputs.json exists
    if [ ! -f "$MODEL_INPUTS_FILE" ]; then
        log_error "Model_Inputs.json not found at: $MODEL_INPUTS_FILE"
        log_error "Please ensure the data-processing folder contains Model_Inputs.json"
        exit 1
    fi
    
    # Check if backend is running
    if ! curl -s "$API_BASE_URL/health" >/dev/null 2>&1; then
        log_warning "Backend server not responding at $API_BASE_URL"
        log_warning "Please start the backend server before running tests"
        log_warning "You can start it with: cd backend && python -m uvicorn main:app --reload"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_success "Prerequisites check completed"
}

# Function to generate test report
generate_report() {
    local report_file="$LOGS_DIR/test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    log_info "📊 Generating test report..."
    
    {
        echo "API Testing Report"
        echo "=================="
        echo "Generated: $(date)"
        echo "API Base URL: $API_BASE_URL"
        echo ""
        echo "Summary:"
        echo "--------"
        echo "Total Test Suites: $total_tests"
        echo "Passed: $total_passed"
        echo "Failed: $total_failed"
        echo "Success Rate: $(( total_passed * 100 / total_tests ))%"
        echo ""
        echo "Detailed Results:"
        echo "----------------"
        
        for test_name in "${!test_results[@]}"; do
            local result="${test_results[$test_name]}"
            local duration="${test_times[$test_name]}"
            echo "$test_name: $result (${duration}s)"
        done
        
        echo ""
        echo "Log Files:"
        echo "----------"
        echo "API Calls Log: $LOGS_DIR/api_calls.log"
        echo "Test Data Directory: $DATA_DIR"
        
    } > "$report_file"
    
    log_success "Test report generated: $report_file"
    
    # Display summary
    echo ""
    log_info "📈 Test Summary:"
    echo "=================="
    for test_name in "${!test_results[@]}"; do
        local result="${test_results[$test_name]}"
        local duration="${test_times[$test_name]}"
        if [ "$result" = "PASSED" ]; then
            log_success "$test_name: $result (${duration}s)"
        else
            log_error "$test_name: $result (${duration}s)"
        fi
    done
    
    echo ""
    log_info "Overall Results:"
    log_success "Total Test Suites: $total_tests"
    log_success "Passed: $total_passed"
    if [ $total_failed -gt 0 ]; then
        log_error "Failed: $total_failed"
    else
        log_success "Failed: $total_failed"
    fi
    
    local success_rate=$(( total_passed * 100 / total_tests ))
    if [ $success_rate -eq 100 ]; then
        log_success "Success Rate: ${success_rate}% 🎉"
    elif [ $success_rate -ge 80 ]; then
        log_warning "Success Rate: ${success_rate}%"
    else
        log_error "Success Rate: ${success_rate}%"
    fi
}

# Function to cleanup test data
cleanup_test_data() {
    log_info "🧹 Cleaning up test data..."
    
    # Remove temporary data files
    rm -f "$DATA_DIR/simulation_id.txt"
    rm -f "$DATA_DIR/model_input_id.txt"
    rm -f "$DATA_DIR/aquifer_data_id.txt"
    rm -f "$DATA_DIR/well_data_id.txt"
    rm -f "$DATA_DIR/optimization_result_id.txt"
    
    log_success "Test data cleanup completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -s, --simulation    Run only simulation tests"
    echo "  -m, --model-input  Run only model input tests"
    echo "  -a, --aquifer      Run only aquifer data tests"
    echo "  -w, --well-data    Run only well data tests"
    echo "  -o, --optimization Run only optimization result tests"
    echo "  --skip-cleanup     Skip cleanup of test data"
    echo "  --no-report         Skip generating test report"
    echo ""
    echo "Environment Variables:"
    echo "  API_BASE_URL       API base URL (default: http://localhost:8000)"
    echo "  TEST_USERNAME       Test username (default: testuser@example.com)"
    echo "  TEST_PASSWORD       Test password (default: testpassword123)"
    echo ""
    echo "Examples:"
    echo "  $0                          # Run all tests"
    echo "  $0 -s                       # Run only simulation tests"
    echo "  $0 --skip-cleanup           # Run all tests but keep test data"
    echo "  API_BASE_URL=http://prod.example.com $0  # Test production API"
}

# Main execution
main() {
    local run_simulation=true
    local run_model_input=true
    local run_aquifer_data=true
    local run_well_data=true
    local run_optimization=true
    local skip_cleanup=false
    local no_report=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -s|--simulation)
                run_model_input=false
                run_aquifer_data=false
                run_well_data=false
                run_optimization=false
                shift
                ;;
            -m|--model-input)
                run_simulation=false
                run_aquifer_data=false
                run_well_data=false
                run_optimization=false
                shift
                ;;
            -a|--aquifer)
                run_simulation=false
                run_model_input=false
                run_well_data=false
                run_optimization=false
                shift
                ;;
            -w|--well-data)
                run_simulation=false
                run_model_input=false
                run_aquifer_data=false
                run_optimization=false
                shift
                ;;
            -o|--optimization)
                run_simulation=false
                run_model_input=false
                run_aquifer_data=false
                run_well_data=false
                shift
                ;;
            --skip-cleanup)
                skip_cleanup=true
                shift
                ;;
            --no-report)
                no_report=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Initialize testing environment
    init_testing
    
    # Check prerequisites
    check_prerequisites
    
    # Run test suites
    if [ "$run_simulation" = true ]; then
        run_test_suite "Simulation" "$SCRIPTS_DIR/test_simulations.sh"
    fi
    
    if [ "$run_model_input" = true ]; then
        run_test_suite "Model Input" "$SCRIPTS_DIR/test_model_inputs.sh"
    fi
    
    if [ "$run_aquifer_data" = true ]; then
        run_test_suite "Aquifer Data" "$SCRIPTS_DIR/test_aquifer_data.sh"
    fi
    
    if [ "$run_well_data" = true ]; then
        run_test_suite "Well Data" "$SCRIPTS_DIR/test_well_data.sh"
    fi
    
    if [ "$run_optimization" = true ]; then
        run_test_suite "Optimization Result" "$SCRIPTS_DIR/test_optimization_results.sh"
    fi
    
    # Generate report
    if [ "$no_report" = false ]; then
        generate_report
    fi
    
    # Cleanup
    if [ "$skip_cleanup" = false ]; then
        cleanup_test_data
    fi
    
    # Exit with appropriate code
    if [ $total_failed -eq 0 ]; then
        log_success "All tests completed successfully! 🎉"
        exit 0
    else
        log_error "Some tests failed. Please check the logs for details."
        exit 1
    fi
}

# Run main function
main "$@"
