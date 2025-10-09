#!/bin/bash

# Example usage script for the API testing suite
# This script demonstrates how to use the testing framework

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "🧪 API Testing Suite - Example Usage"
echo "====================================="
echo ""

# Show current configuration
echo "📋 Current Configuration:"
echo "  API Base URL: $API_BASE_URL"
echo "  Test Username: $TEST_USERNAME"
echo "  Model Inputs File: $MODEL_INPUTS_FILE"
echo ""

# Show available test scripts
echo "🔧 Available Test Scripts:"
echo "  ./test_simulations.sh           - Test simulation endpoints"
echo "  ./test_model_inputs.sh          - Test model input endpoints"
echo "  ./test_aquifer_data.sh          - Test aquifer data endpoints"
echo "  ./test_well_data.sh             - Test well data endpoints"
echo "  ./test_optimization_results.sh  - Test optimization result endpoints"
echo "  ./run_all_tests.sh              - Run all tests with reporting"
echo ""

# Show usage examples
echo "💡 Usage Examples:"
echo ""
echo "1. Run all tests:"
echo "   ./run_all_tests.sh"
echo ""
echo "2. Run only simulation tests:"
echo "   ./run_all_tests.sh -s"
echo ""
echo "3. Run tests with custom API URL:"
echo "   API_BASE_URL=http://prod.example.com ./run_all_tests.sh"
echo ""
echo "4. Run tests and keep data for debugging:"
echo "   ./run_all_tests.sh --skip-cleanup"
echo ""
echo "5. Run individual test script:"
echo "   ./test_simulations.sh"
echo ""

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s "$API_BASE_URL/health" >/dev/null 2>&1; then
    log_success "Backend server is running at $API_BASE_URL"
else
    log_warning "Backend server not responding at $API_BASE_URL"
    echo "   Please start the backend server:"
    echo "   cd backend && python -m uvicorn main:app --reload"
fi
echo ""

# Check if Model_Inputs.json exists
echo "📄 Checking test data..."
if [ -f "$MODEL_INPUTS_FILE" ]; then
    log_success "Model_Inputs.json found"
    local user_id=$(jq -r '.data.user_id' "$MODEL_INPUTS_FILE")
    local model_id=$(jq -r '.data.model_id' "$MODEL_INPUTS_FILE")
    echo "   User ID: $user_id"
    echo "   Model ID: $model_id"
else
    log_error "Model_Inputs.json not found at: $MODEL_INPUTS_FILE"
fi
echo ""

# Show next steps
echo "🚀 Next Steps:"
echo "1. Ensure backend server is running"
echo "2. Run: ./run_all_tests.sh"
echo "3. Check logs in: $LOGS_DIR"
echo "4. View test data in: $DATA_DIR"
echo ""

echo "Happy Testing! 🎉"
