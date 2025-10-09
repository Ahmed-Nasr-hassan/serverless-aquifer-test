#!/bin/bash

# Master test runner for the new 2-entity architecture
# Runs all tests for Models and Simulations APIs

echo "🚀 Running All Tests - New 2-Entity Architecture"
echo "================================================"

# Source the config
source "$(dirname "$0")/config.sh"

# Initialize test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_script="$2"
    
    echo ""
    echo "🧪 Running $test_name..."
    echo "================================"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if bash "$test_script"; then
        echo "✅ $test_name PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ $test_name FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ jq is required but not installed. Please install jq first."
    echo "   On Ubuntu/Debian: sudo apt-get install jq"
    echo "   On macOS: brew install jq"
    exit 1
fi

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo "❌ curl is required but not installed. Please install curl first."
    exit 1
fi

# Check if backend is running
if ! curl -s "$API_BASE_URL/test-db" >/dev/null 2>&1; then
    echo "⚠️  Backend server not responding at $API_BASE_URL"
    echo "   Please start the backend server before running tests"
    echo "   You can start it with: cd backend && python -m uvicorn main:app --reload"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Prerequisites check completed"

# Run all tests
run_test "Models API Test" "$(dirname "$0")/test_models_new.sh"
run_test "Simulations API Test" "$(dirname "$0")/test_simulations_new.sh"
run_test "Comprehensive Integration Test" "$(dirname "$0")/test_comprehensive_new.sh"

# Print summary
echo ""
echo "📊 Test Results Summary"
echo "======================="
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! The new 2-entity architecture is working correctly."
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Please check the output above for details."
    exit 1
fi
