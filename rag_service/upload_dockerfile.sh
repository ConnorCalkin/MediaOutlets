docker build --platform linux/amd64 -t rag-service .
docker run --rm -p 5001:5000 --env-file .env rag-service