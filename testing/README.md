# API Testing Suite

This folder contains a comprehensive testing suite for the Serverless Aquifer Test API endpoints. The tests use real data from the `Model_Inputs.json` file and provide complete CRUD operation testing for all entities.

## 📁 Folder Structure

```
testing/
├── scripts/                    # Test scripts
│   ├── auth.sh                 # Authentication helper
│   ├── config.sh              # Configuration and utilities
│   ├── test_simulations.sh    # Simulation API tests
│   ├── test_model_inputs.sh   # Model Input API tests
│   ├── test_aquifer_data.sh   # Aquifer Data API tests
│   ├── test_well_data.sh      # Well Data API tests
│   ├── test_optimization_results.sh # Optimization Result API tests
│   └── run_all_tests.sh       # Master test runner
├── data/                       # Test data files (auto-generated)
├── logs/                       # Test logs and reports
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Install required tools:**
   ```bash
   # Install jq for JSON processing
   sudo apt-get install jq  # Ubuntu/Debian
   brew install jq          # macOS
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

3. **Run all tests:**
   ```bash
   cd testing/scripts
   ./run_all_tests.sh
   ```

## 🧪 Test Scripts

### Individual Test Scripts

Each entity has its own test script that performs complete CRUD operations:

- **`test_simulations.sh`** - Tests simulation endpoints
- **`test_model_inputs.sh`** - Tests model input endpoints using data from `Model_Inputs.json`
- **`test_aquifer_data.sh`** - Tests aquifer data endpoints
- **`test_well_data.sh`** - Tests well data endpoints
- **`test_optimization_results.sh`** - Tests optimization result endpoints

### Master Test Runner

**`run_all_tests.sh`** - Runs all tests in sequence and provides comprehensive reporting.

#### Usage Options:
```bash
# Run all tests
./run_all_tests.sh

# Run only specific test suites
./run_all_tests.sh -s                    # Simulation only
./run_all_tests.sh -m                    # Model Input only
./run_all_tests.sh -a                    # Aquifer Data only
./run_all_tests.sh -w                    # Well Data only
./run_all_tests.sh -o                    # Optimization Result only

# Advanced options
./run_all_tests.sh --skip-cleanup        # Keep test data
./run_all_tests.sh --no-report           # Skip report generation
./run_all_tests.sh -h                    # Show help
```

## ⚙️ Configuration

### Environment Variables

Set these environment variables to customize the testing:

```bash
export API_BASE_URL="http://localhost:8000"        # API base URL
export TEST_USERNAME="testuser@example.com"        # Test username
export TEST_PASSWORD="testpassword123"             # Test password
```

### Default Configuration

- **API Base URL:** `http://localhost:8000`
- **Test Username:** `testuser@example.com`
- **Test Password:** `testpassword123`
- **Model Inputs File:** `../data-processing/Model_Inputs.json`

## 📊 Test Data

The tests use real data extracted from `Model_Inputs.json`:

### Data Extraction
- **User ID:** `f81d4fae-7dec-11d0-a765-00a0c91e6bf6`
- **Model ID:** `a55d4fea-8wq2-6ds3-a765-00a5c91e1bf2`
- **Model Inputs:** Complete nested configuration object
- **Hydraulic Conductivity:** Array of soil layer data
- **Observation Data:** Well configuration and time series data

### Test Data Files (Auto-generated)
- `data/user_id.txt`
- `data/model_id.txt`
- `data/model_inputs.json`
- `data/hydraulic_conductivity.json`
- `data/observation_data.json`

## 🔐 Authentication

The testing suite includes automatic authentication:

1. **Token Management:** Automatically obtains and caches authentication tokens
2. **Token Validation:** Validates existing tokens before making API calls
3. **Re-authentication:** Automatically re-authenticates if tokens expire
4. **Token Storage:** Stores tokens in `data/auth_token.txt`

## 📈 Test Coverage

Each test script covers:

### CRUD Operations
- ✅ **CREATE** - Create new records
- ✅ **READ** - Retrieve records by ID
- ✅ **UPDATE** - Update existing records
- ✅ **DELETE** - Delete records
- ✅ **LIST** - List all records
- ✅ **FILTER** - Get records by simulation ID

### Data Validation
- ✅ **Structure Validation** - Verify JSON field structure
- ✅ **Data Integrity** - Check data matches input
- ✅ **Type Safety** - Validate data types
- ✅ **Required Fields** - Ensure required fields are present

### Error Handling
- ✅ **Authentication Errors** - Handle auth failures
- ✅ **Validation Errors** - Handle invalid data
- ✅ **Not Found Errors** - Handle missing records
- ✅ **Server Errors** - Handle server issues

## 📋 Test Results

### Logging
- **API Calls Log:** `logs/api_calls.log` - All API requests and responses
- **Test Reports:** `logs/test_report_YYYYMMDD_HHMMSS.txt` - Detailed test results

### Report Contents
- Test suite summary
- Individual test results
- Execution times
- Success rates
- Error details

### Sample Output
```
🚀 Starting Comprehensive API Testing Suite...
🧪 Running Simulation tests...
✅ Simulation tests completed successfully in 5s
🧪 Running Model Input tests...
✅ Model Input tests completed successfully in 8s
📊 Test Summary:
==================
Simulation: PASSED (5s)
Model Input: PASSED (8s)
Overall Results:
Total Test Suites: 2
Passed: 2
Failed: 0
Success Rate: 100% 🎉
```

## 🛠️ Troubleshooting

### Common Issues

1. **Backend Server Not Running**
   ```bash
   # Start the backend server
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Authentication Failures**
   - Check username/password in environment variables
   - Verify user exists in the database
   - Check authentication endpoint is working

3. **Missing Dependencies**
   ```bash
   # Install jq
   sudo apt-get install jq
   
   # Install curl (usually pre-installed)
   sudo apt-get install curl
   ```

4. **Model_Inputs.json Not Found**
   - Ensure the file exists in `data-processing/Model_Inputs.json`
   - Check file permissions

### Debug Mode

Run individual test scripts for debugging:
```bash
# Run with verbose output
bash -x ./test_simulations.sh

# Check specific test
./test_simulations.sh  # Run only simulation tests
```

## 🔄 Continuous Integration

The testing suite is designed for CI/CD integration:

```bash
# CI-friendly command
./run_all_tests.sh --no-report --skip-cleanup
```

This will:
- Run all tests
- Exit with appropriate code (0 for success, 1 for failure)
- Skip report generation
- Keep test data for debugging

## 📝 Contributing

When adding new tests:

1. **Follow the pattern** of existing test scripts
2. **Use the config.sh utilities** for common functions
3. **Include data validation** tests
4. **Add proper error handling**
5. **Update this README** with new test information

## 🎯 Best Practices

1. **Test Data Isolation** - Each test creates its own data
2. **Cleanup** - Tests clean up after themselves
3. **Idempotent** - Tests can be run multiple times safely
4. **Realistic Data** - Uses actual data from Model_Inputs.json
5. **Comprehensive Coverage** - Tests all CRUD operations
6. **Error Scenarios** - Tests both success and failure cases
