FROM chromadb/chroma:1.0.21.dev53

# Set working directory
WORKDIR /app

# Install Python and development tools
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --set python3 /usr/bin/python3.11

# Verify Python installation
RUN python3 --version && \
    pip3 --version

# Copy requirements first for better cache usage
COPY requirements.txt .

# Upgrade pip and install requirements
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables for Render
ENV PORT=10000
EXPOSE $PORT

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Command to run the application
CMD python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT