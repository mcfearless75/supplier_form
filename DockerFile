# Use a slim Python image
FROM python:3.10-slim

# Install system deps including wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wkhtmltopdf \
      fonts-liberation \
      libxrender1 \
      libxext6 \
      libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose the port Streamlit uses
EXPOSE 8501

# Launch the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
