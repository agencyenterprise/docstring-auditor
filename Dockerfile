# Use the official Python image as the base image
FROM python:3.11

# Set the working directory in the container
RUN mkdir /app
WORKDIR /app

# Create a directory at /repo
RUN mkdir /repo

# Set the OpenAI API key environment variable
ENV OPENAI_API_KEY=your_api_key_here

# Copy the entire project into the container
COPY . /app/

# Install Hatch and the project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir hatch && \
    hatch env create

# Set the entry point to run the Docstring Auditor console script using Hatch
ENTRYPOINT ["hatch", "run", "docstring-auditor"]
CMD ["/repo"]