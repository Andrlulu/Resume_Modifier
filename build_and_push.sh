#!/bin/bash

# Define configurable variables
AWS_REGION="us-east-2"
AWS_ACCOUNT_ID="376129840507"
ECR_REPOSITORY="editor-backend"
ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Log in to AWS ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}

# Build the Docker image
docker build -f Dockerfile -t ${ECR_REPOSITORY} .

# Tag the Docker image
docker tag ${ECR_REPOSITORY}:latest ${ECR_URL}/${ECR_REPOSITORY}:latest

# Push the Docker image to ECR
docker push ${ECR_URL}/${ECR_REPOSITORY}:latest
