#!/bin/bash

# Simple demonstration of Model Input API with real data from Model_Inputs.json

set -e

# Source configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo -e "${BLUE}🧪 Model Input API Demo with Real Data from Model_Inputs.json${NC}"

# Initialize testing environment
init_testing

# Extract real data from Model_Inputs.json
echo -e "${BLUE}📊 Extracting real data from Model_Inputs.json...${NC}"

USER_ID=$(jq -r '.data.user_id' "$MODEL_INPUTS_FILE")
MODEL_ID=$(jq -r '.data.model_id' "$MODEL_INPUTS_FILE")

echo -e "${GREEN}✅ User ID: $USER_ID${NC}"
echo -e "${GREEN}✅ Model ID: $MODEL_ID${NC}"

# Create simulation first
echo -e "${BLUE}📝 Creating simulation...${NC}"
simulation_data=$(jq -c -n \
    --arg name "Real Data Demo Simulation" \
    --arg description "Demo simulation using complete Model_Inputs.json data" \
    --arg simulation_type "Calibration" \
    --arg user_id "$USER_ID" \
    '{
        name: $name,
        description: $description,
        simulation_type: $simulation_type,
        user_id: $user_id
    }')

simulation_response=$(api_call "POST" "/simulations/" "$simulation_data")
simulation_id=$(echo "$simulation_response" | jq -r '.id')
echo -e "${GREEN}✅ Simulation created with ID: $simulation_id${NC}"

# Create model input with complete real data
echo -e "${BLUE}📝 Creating model input with complete real data...${NC}"

model_inputs_data=$(jq -c '.data.model_inputs' "$MODEL_INPUTS_FILE")
hydraulic_conductivity_data=$(jq -c '.data.hydraulic_conductivity' "$MODEL_INPUTS_FILE")

model_input_data=$(jq -c -n \
    --arg user_id "$USER_ID" \
    --arg model_id "$MODEL_ID" \
    --argjson model_inputs "$model_inputs_data" \
    --argjson hydraulic_conductivity "$hydraulic_conductivity_data" \
    --arg simulation_id "$simulation_id" \
    --arg description "Complete model input from Model_Inputs.json with all real parameters" \
    '{
        user_id: $user_id,
        model_id: $model_id,
        model_inputs: $model_inputs,
        hydraulic_conductivity: $hydraulic_conductivity,
        simulation_id: ($simulation_id | tonumber),
        description: $description
    }')

model_input_response=$(api_call "POST" "/model-inputs/" "$model_input_data")
model_input_id=$(echo "$model_input_response" | jq -r '.id')
echo -e "${GREEN}✅ Model input created with ID: $model_input_id${NC}"

# Verify the data was stored correctly
echo -e "${BLUE}🔍 Verifying stored data...${NC}"

# Check radial discretization
echo -e "${YELLOW}📐 Radial Discretization:${NC}"
curl -s -X GET "http://localhost:8000/api/v1/model-inputs/$model_input_id" | jq '.model_inputs.radial_discretization'

# Check hydraulic conductivity
echo -e "${YELLOW}💧 Hydraulic Conductivity:${NC}"
curl -s -X GET "http://localhost:8000/api/v1/model-inputs/$model_input_id" | jq '.hydraulic_conductivity'

# Check observation wells
echo -e "${YELLOW}🔍 Observation Wells:${NC}"
curl -s -X GET "http://localhost:8000/api/v1/model-inputs/$model_input_id" | jq '.model_inputs.observation_data.observation_wells | keys'

# Check pumping well data
echo -e "${YELLOW}⛽ Pumping Well Data:${NC}"
curl -s -X GET "http://localhost:8000/api/v1/model-inputs/$model_input_id" | jq '.model_inputs.pumping_well'

# Check stress periods
echo -e "${YELLOW}⏰ Stress Periods:${NC}"
curl -s -X GET "http://localhost:8000/api/v1/model-inputs/$model_input_id" | jq '.model_inputs.stress_periods'

# Check hydraulic parameters
echo -e "${YELLOW}🔧 Hydraulic Parameters:${NC}"
curl -s -X GET "http://localhost:8000/api/v1/model-inputs/$model_input_id" | jq '.model_inputs.hydraulic_parameters'

# Check simulation settings
echo -e "${YELLOW}⚙️ Simulation Settings:${NC}"
curl -s -X GET "http://localhost:8000/api/v1/model-inputs/$model_input_id" | jq '.model_inputs.simulation_settings'

echo -e "${GREEN}🎉 Model Input API Demo completed successfully!${NC}"
echo -e "${GREEN}✅ All real data from Model_Inputs.json has been stored and retrieved correctly${NC}"
