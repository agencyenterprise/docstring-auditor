# Use the slim version of the official Python image as the base image
FROM python:3.11-slim

# Set the OpenAI API key environment variable using build arguments
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY

# Set the working directory in the container and create a directory at /repo
RUN mkdir /app /repo
WORKDIR /app

# Copy the entire project into the container
COPY . /app/

# Install Hatch and the project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir hatch && \
    hatch env create

# Install Tini (A minimal init process)
RUN apt-get update && apt-get install -y tini

# Set the entry point to run the Docstring Auditor console script using Hatch
ENTRYPOINT ["/usr/bin/tini", "--", "sh", "-c", "hatch run docstring-auditor /repo/$0"]
