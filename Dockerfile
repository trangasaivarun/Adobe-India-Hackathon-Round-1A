# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure input/output directories exist
RUN mkdir -p input_pdfs output_jsons

# Default command to run the main script
CMD ["python", "run.py"]
