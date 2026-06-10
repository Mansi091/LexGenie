
FROM python:3.12-slim

# Set directory
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app code
COPY app/ ./app/

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
