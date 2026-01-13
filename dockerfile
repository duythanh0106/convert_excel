FROM python:3.9-slim

# Set working directory
WORKDIR /app


# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Run the application
CMD ["python", "app.py"]