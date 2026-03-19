ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=eu-west-2
REPOSITORY_NAME=c22-dashboard-divas-rag-service
IMAGE_NAME=c22-dashboard-divas-rag-service

# Authenticate Docker to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Create ECR repository if it doesn't exist
aws ecr create-repository --repository-name $REPOSITORY_NAME --region $REGION

# Build the Docker image for the RAG service
docker buildx build --platform "linux/amd64" --provenance=false -t $IMAGE_NAME .

# Tag the image with the ECR repository URI
docker tag $IMAGE_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest

# Push the image to ECR
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest
