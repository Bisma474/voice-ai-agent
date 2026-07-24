FROM python:3.10-slim

WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project code
COPY . .

# Expose port 7860 (Hugging Face default port)
EXPOSE 7860

# Set environment variable for port
ENV PORT=7860

# Run the web server
CMD ["python", "-m", "src.web_ui"]
