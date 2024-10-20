# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables to point to the secret files
ENV LANGCHAIN_API_KEY_FILE="/run/secrets/langchain_api_key"
ENV OPENAI_API_KEY_FILE="/run/secrets/openai_api_key"
ENV AWS_ACCESS_KEY_ID_FILE="/run/secrets/aws_access_key_id"
ENV AWS_SECRET_ACCESS_KEY_FILE="/run/secrets/aws_secret_access_key"
ENV TAVILY_API_KEY_FILE="/run/secrets/tavily_api_key"

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/app/entrypoint.sh"]

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]