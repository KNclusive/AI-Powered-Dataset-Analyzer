#!/bin/sh

# Read secrets from files and export them as environment variables
export AWS_ACCESS_KEY_ID="$(cat $AWS_ACCESS_KEY_ID_FILE)"
export AWS_SECRET_ACCESS_KEY="$(cat $AWS_SECRET_ACCESS_KEY_FILE)"
export LANGCHAIN_API_KEY="$(cat $LANGCHAIN_API_KEY_FILE)"
export OPENAI_API_KEY="$(cat $OPENAI_API_KEY_FILE)"
export TAVILY_API_KEY="$(cat $TAVILY_API_KEY_FILE)"

# Execute the command passed to the container (i.e., start the application)
exec "$@"