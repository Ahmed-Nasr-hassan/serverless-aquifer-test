#!/bin/bash

# AWS Lambda Deployment Script for Aquifer Simulation
# This script builds and deploys the Lambda function

set -e

# Configuration
FUNCTION_NAME="aquifer-test-simulation"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${FUNCTION_NAME}"

echo "🚀 Starting Lambda deployment..."
echo "Function Name: ${FUNCTION_NAME}"
echo "Region: ${REGION}"
echo "ECR Repository: ${ECR_REPOSITORY}"

# Build Docker image
echo "📦 Building Docker image..."
docker build -t ${FUNCTION_NAME} .

# Tag image for ECR
echo "🏷️  Tagging image for ECR..."
docker tag ${FUNCTION_NAME}:latest ${ECR_REPOSITORY}:latest

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY}

# Create ECR repository if it doesn't exist
echo "📁 Creating ECR repository if needed..."
aws ecr describe-repositories --repository-names ${FUNCTION_NAME} --region ${REGION} || \
aws ecr create-repository --repository-name ${FUNCTION_NAME} --region ${REGION}

# Push image to ECR
echo "⬆️  Pushing image to ECR..."
docker push ${ECR_REPOSITORY}:latest


