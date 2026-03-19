# Terraform configuration for RAG model architecture

## Ensure you include a .tfvars file with the following variables:

# Chroma host
-  chroma_host="YOUR_CHROMA_HOST_HERE"
-  The ECS public IP
-  AWS console --> ECS cluster --> your service --> your running task --> public IP

# Chroma port
-  chroma_port=YOUR_CHROMA_PORT_NUMBER
-  8000

# Open AI API key
-  openai_api_key="YOUR_API_KEY_HERE"

# Image URI
-  image_uri="YOUR_IMAGE_URI_HERE"
-  The image_uri from the repo pushed to
-  AWS console --> your ECR repo --> you image --> URI